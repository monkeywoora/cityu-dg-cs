import numpy as np

class LPCenteringSolver():
    """
    A helper module for LPSolver

    Solves LP centering problem using infeasible start Newton method:
    minimize    c'x - sum( log(x_i) )
    subject to  Ax = b

    Hyperparameters
        alpha: the factor by which we weaken the slope of first-order approximation
               in backtracking line search (0 < alpha < 0.5)
        beta: multiplicative step size in backtracking line search (0 < beta < 1)
        max_iter: maximum number of Newton steps before quitting

    Attributes
        status: 'optimal' or None
        value: optimal value of objective function
        x_opt, v_opt: primal optimal point and a dual optimal point
        num_steps: Number of Newton steps executed
        residual_norm: array of ||r(x,v)||_2 (length num_steps+1)
    """

    def __init__(self, alpha=0.25, beta=0.5, max_iter=100):
        self.alpha = alpha
        self.beta = beta
        self.max_iter = max_iter
        self.convergence_threshold = 1e-6  # stop when ||r||_2 <= convergence_threshold
        self.status = None


    def solve(self, A, b, c, x0=None):
        m, n = A.shape
        self.status = None
        self.residual_norm = []

        # Initialize primal and dual variables (x, v)
        x = x0 if x0 is not None else np.random.rand(n) + 0.01
        v = np.zeros(m)

        for self.num_steps in range(self.max_iter):
            # Compute primal and dual residuals
            r_dual = c - 1 / x + np.dot(A.T, v)
            r_primal = A.dot(x) - b
            r_norm = np.sqrt(np.sum(r_dual ** 2) + np.sum(r_primal ** 2))
            self.residual_norm.append(r_norm)

            # Convergence check
            if r_norm <= self.convergence_threshold:
                self.status = 'optimal'
                self.x_opt, self.v_opt = x, v
                self.value = np.sum(c * x) - np.sum(np.log(x))
                break

            # Compute primal and dual Newton steps (dx, dv) via block elimination
            h_inv =  x ** 2  # diagonal entries of inv(Hessian)
            dv = np.linalg.solve( np.dot(A * h_inv, A.T), r_primal - np.dot(A * h_inv, r_dual) )
            dx = -h_inv * (r_dual + np.dot(A.T, dv))

            # Backtracking line search on ||r||_2
            t = 1
            while np.min(x + t * dx) <= 0:  # prevent x from going below 0
                t = self.beta * t
            while True:
                x_new = x + t * dx
                v_new = v + t * dv
                r_dual_new = c - 1 / x_new + np.dot(A.T, v_new)
                r_primal_new = A.dot(x_new) - b
                r_norm_new = np.sqrt(np.sum(r_dual_new ** 2) + np.sum(r_primal_new ** 2))

                if r_norm_new <= (1 - self.alpha * t) * r_norm:
                    x = x_new
                    v = v_new
                    break
                else:
                    t = self.beta * t

        self.residual_norm = np.array(self.residual_norm)
        if self.status != 'optimal':
            self.num_steps = self.max_iter
            self.value, self.x_opt, self.v_opt = None, None, None


class LPSolver():
    """
    LPSolver solves the standard form LP problem:
    minimize    c'x
    subject to  Ax = b, x >= 0

    The solver uses the barrier method.
    It traverses the central path by solving a centering problem at each step:
    minimize    t * c'x - sum( log(x_i) )
    subject to  Ax = b

    The solving procedure gradually increases t after each step, and stops when
    the duality gap n / t < tol, where n is the length of x

    Hyperparameters
        mu: multiplicative step size for barrier method (t := mu * t)
        tol: suboptimality tolerance (used for convergence check)

    Attributes:
        status: 'optimal', 'infeasible', or 'failure'
        value: optimal value of objective function
        x_opt, v_opt: primal optimal point and a dual optimal point
        num_steps: number of centering steps executed
        duality_gaps: array - duality gap after every centering step
        newton_steps: array - number of Newton steps for solving centering problems
    """

    def __init__(self, mu=10, tol=1e-3) :
        self.mu = mu  # multiplicative step size for barrier method
        self.tol = tol  # maximum acceptable duality gap
        self.max_iter = 100
        self.centering_solver = LPCenteringSolver(alpha=0.25, beta=0.5, max_iter=100)


    def solve_feasible_start(self, A, b, c, x):
        """
        Solves an LP problem given a strictly feasible starting point x.
        This is used as a helper method for solving an LP problem from scratch,
        no matter whether the problem is strictly feasible or not
        """
        m, n = A.shape
        status, x_opt, v_opt, value = None, None, None, None
        duality_gaps = []  # duality gap n/t after every iteration
        newton_steps = []  # number of Newton steps for solving centering problems

        t = 1
        for num_steps in range(1, self.max_iter+1):
            # Solve LP Centering problem
            self.centering_solver.solve(A, b, t*c, x)
            if self.centering_solver.status != 'optimal':
                status = 'failure'  # Centering solver failed
                break

            x, v = self.centering_solver.x_opt, self.centering_solver.v_opt
            duality_gap = n / t
            newton_steps.append(self.centering_solver.num_steps)
            duality_gaps.append(duality_gap)

            # Convergence check
            if duality_gap < self.tol:
                status = 'optimal'
                x_opt, v_opt = x, v
                value = np.sum(c * x)
                break
            else:
                t = self.mu * t  # Increase t

        return status, x_opt, v_opt, value, num_steps, \
               np.array(duality_gaps), np.array(newton_steps)


    def solve(self, A, b, c):
        """
        Checks feasibility of an LP problem, and solves the problem if it's feasible
        The solving procedure consists of two phases:
        -- Phase I: Check strict feasibility and obtain a strictly feasible starting
                    point by using solve_feasible_start() to solve the following LP,
                    for which we can always find a feasible starting point (x, t):
                    minimize    t
                    subject to  Ax = b, x >= (1 - t) * 1_n

        -- Phase II: If strictly feasible, directly invoke solve_feasible_start()
                     with the starting point x found in Phase I
        """
        m, n = A.shape

        # Phase I: Check strict feasibility and obtain a strictly feasible starting point
        x = np.linalg.pinv(A).dot(b)
        if np.min(x) <= 0:  # otherwise, x is already a strictly feasible point
            # Construct an LP for checking feasibility
            A1 = np.hstack(( A, -A.dot(np.ones((n, 1))) ))
            b1 = b - A.dot(np.ones(n))
            c1 = np.zeros(n+1)
            c1[-1] = 1

            t = 2 - np.min(x)  # makes sure the starting (x, t) pair is feasible
            z0 = np.concatenate(( x + (t-1)*np.ones(n), [t] ))
            status, z_opt, _, value, _, _, _ = self.solve_feasible_start(A1, b1, c1, z0)
            if status == 'optimal' and value < 1:  # strictly feasible
                x = z_opt[:n] - (z_opt[-1] - 1) * np.ones(n)
            else:
                self.status = "infeasible"
                self.x_opt, self.v_opt, self.value = None, None, None
                self.duality_gaps, self.newton_steps = None, None
                return

        # Phase II: Given a strictly feasible starting point x, solve the problem
        self.status, self.x_opt, self.v_opt, self.value, self.num_steps, \
        self.duality_gaps, self.newton_steps = self.solve_feasible_start(A, b, c, x)
