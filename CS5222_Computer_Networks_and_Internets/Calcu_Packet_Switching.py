import math
p = 0.1
k_max = 10
n = 35
E = 0
for k in range(k_max+1):
    E += math.comb(35,k)*(0.1**k)*(0.9**(35-k))
print("超过10个人在线的可能性是：",1-E)