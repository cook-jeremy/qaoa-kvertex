import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from scipy.special import comb
from scipy.optimize import minimize
from math import pi
from scipy.linalg import expm
import time
from scipy.optimize import basinhopping

# Global variables
I = np.array([[1,0],[0,1]])
X = np.array([[0,1],[1,0]])
Y = np.array([[0,-1],[1,0]])*complex(0,1)
Z = np.array([[1,0],[0,-1]])

# take the kronecker (tensor) product of a list of matrices
def kron(m):
    if len(m) == 1:
        return m
    total = np.kron(m[1], m[0])
    if len(m) > 2:
        for i in range(2, len(m)):
            total = np.kron(m[i], total)
    return total

def num_ones(n):
    c = 0
    while n:
        c += 1
        n &= n - 1
    return c

def expectation(G, state):
    total = 0
    for i in range(0, len(state)):
        if state[i] == 0:
            continue
        sa = [0]*len(G.nodes)
        b = bin(i)[2:]
        for j in range(0, len(b)):
            sa[j] = int(b[len(b)-1-j])
        total_cost = 0
        for edge in G.edges:
            cost = 3
            if sa[edge[0]] == 1 or sa[edge[1]] == 1:
                cost = -1
            total_cost += cost
        f = -(1/4)*(total_cost - 3*G.number_of_edges())
        prob = np.real(state[i]*np.conj(state[i]))
        total += f*prob
    return total

def create_C(G):
    init = [I]*len(G.nodes)
    C = complex(1,0)*np.zeros([2**len(G.nodes), 2**len(G.nodes)])
    for i in range(0, len(G.nodes)):
        init[i] = Z
        C += G.degree[i]*kron(init)
        # reset
        init = [I]*len(G.nodes)

    init = [I]*len(G.nodes)
    for edge in G.edges:
        init[edge[0]] = Z
        init[edge[1]] = Z
        C += kron(init)
        # reset
        init = [I]*len(G.nodes)
    return C.diagonal()

def create_M(G):
    init = [I]*len(G.nodes)
    M = complex(1,0)*np.zeros([2**len(G.nodes), 2**len(G.nodes)])
    for i in range(0, len(G.nodes)):
        # X_i X_{i+1}
        init[i] = X
        init[(i+1) % len(G.nodes)] = X
        M += kron(init)
        init = [I]*len(G.nodes)
        # Y_i Y_{i+1}
        init[i] = Y
        init[(i+1) % len(G.nodes)] = Y
        M += kron(init)
        init = [I]*len(G.nodes)
    return M

def phase_separator(state, C, gamma):
    eiC = np.exp(np.complex(0,-1)*gamma*C)
    return np.multiply(eiC, state)

def ring_mixer(state, M, beta):
    eibxxyy = expm(np.complex(0,-1)*beta*M)
    state = np.matmul(eibxxyy, state)
    return state

def prep(state, G, k, m):
    counter = 0
    for i in range(0, 2**len(G.nodes)):
        if num_ones(i) == k:
            # start with different initial states
            if m == counter:
                state[i] = 1
                break
            counter += 1
    return state

def qaoa(G, C, M, k, p, m, gamma, beta0, beta1):
    state = np.zeros(2**len(G.nodes))
    state = prep(state, G, k, m)
    state = ring_mixer(state, M, beta0)
    for i in range(p):
        state = phase_separator(state, C, gamma)
        state = ring_mixer(state, M, beta1)
    return state

def opt(args, *extras):
    state = qaoa(extras[0], extras[1], extras[2], extras[3], extras[4], extras[5], args[0], args[1], args[2])
    exp = expectation(extras[0], state)
    return -exp

def old_ring_ps_ring(G, k, p, num_steps):
    start_time = int(round(time.time() * 1000))
    C = create_C(G)
    M = create_M(G)
    opts = []
    exp_c = 0
    exp_arr = []
    angles = []
    angle_arr = []

    num_init = int(comb(len(G.nodes), k))
    for m in range(0, num_init):
        kwargs = {'method': 'L-BFGS-B', 'args': (G, C, M, k, p, m), 'bounds': [[0,pi/2],[0,pi],[0,pi]]}
        optimal = basinhopping(opt, np.array([pi/4, pi/2, pi/2]), minimizer_kwargs=kwargs, niter=30)
        angle_arr.append(optimal.x)
        exp_arr.append(-optimal.fun)

    avg = 0
    for entry in exp_arr:
        avg += entry*(1/num_init)

    end_time = int(round(time.time() * 1000))
    print('time delta:\t' + str(end_time - start_time))
    return avg, angle_arr

if __name__ == '__main__':
    G = nx.graph_atlas(6)
    exp, angles = old_ring_ps_ring(G, int(len(G.nodes)/2), 1, 3)
    print('exp: ' + str(exp))