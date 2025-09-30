import numpy as np
import cvxpy as cp
from lp_solver import LPSolver

def generate_data(m, n, feasible=True):
    """
    Randomly generates an LP problem
    Returns A (m x n), b (m), c (n)
    """
    assert m < n
    A = np.random.randn(m, n)
    A[0,:] = np.random.rand(n) + 0.1  # make sure problem is bounded
    if feasible:
        p = np.random.rand(n) + 0.01  # all positive
    else:
        p = np.random.randn(n)
    b = np.dot(A, p)
    c = np.random.rand(n)
    return A, b, c


if __name__ == "__main__":
    # Generate a feasible LP problem
    m, n = 100, 500
    A, b, c = generate_data(m, n, feasible=True)

    # Solve the problem using LPSolver
    solver = LPSolver(mu=10, tol=1e-4)
    solver.solve(A, b, c)

    assert solver.status == 'optimal'
    x_opt = solver.x_opt
    print("LP Solver optimal value: {}".format(solver.value))
    print("LPSolver number of centering steps: {}".format(solver.num_steps))
    print("LPSolver norm(Ax-b): {}".format(np.linalg.norm(A.dot(x_opt) - b)))
    print("LPSolver number of negative x_i: {}".format((x_opt < 0).sum()))

    # Solve the same problem using CVXPY, and compare answers
    x_cp = cp.Variable(n)
    objective = c.T * x_cp
    problem = cp.Problem(cp.Minimize(objective), [A * x_cp == b, x_cp >= 0])
    problem.solve()

    assert problem.status == 'optimal'
    print("\nCVX optimal value: {}".format(objective.value))
    print("Percent diff: {}%".format((solver.value - objective.value) / objective.value * 100))

    # Experiment infeasible problems
    num_runs = 10
    print("\nTest LPSolver on {} infeasible problems...".format(num_runs))
    for i in range(num_runs):
        A, b, c = generate_data(m, n, feasible=False)
        solver = LPSolver(mu=10, tol=1e-4)
        solver.solve(A, b, c)
        problem = cp.Problem(cp.Minimize(objective), [A * x_cp == b, x_cp >= 0])
        problem.solve()
        if problem.status != 'infeasible':
            print("WHAT?!")
        assert solver.status == 'infeasible'
    print("LPSolver and CVXPY are consistent on the {} infeasible problems.".format(num_runs))
