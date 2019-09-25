import numpy as np
import networkx as nx
from math import pi
from scipy.optimize import basinhopping
from scipy.optimize import minimize
from scipy.optimize import show_options
import sys
sys.path.insert(0, '../common/')
import os
import common
import pickle
import random
import time
import datetime

def qaoa(gb, G, C, M , k, p):
    state = common.dicke(len(G.nodes), k)
    for i in range(p):
        state = common.phase_separator(state, C, gb[i])
        state = common.mixer(state, M, gb[p+i])
    return -common.expectation(G, k, state)

def basin_best(G, C, M, k, p, num_samples):
    low_g, up_g = 0, 2*pi
    low_b, up_b = 0, pi/2
    bounds = [[low_g,up_g] if j < p else [low_b,up_b] for j in range(2*p)]
    evals = 0
    n_iter = 10
    max_fun = 100
    best_exp = -1
    while evals < num_samples:
        angles = [random.uniform(low_g, up_g) if j < p else random.uniform(low_b, up_b) for j in range(2*p)]
        kwargs = {'method': 'L-BFGS-B', 'options': {'maxfun': max_fun}, 'args': (G, C, M, k, p), 'bounds': bounds}
        optimal = basinhopping(qaoa, angles, minimizer_kwargs=kwargs, niter=n_iter, disp=True)
        evals += optimal.nfev
        if -optimal.fun > best_exp: best_exp = -optimal.fun
        print('p: ' + str(p) + ', evals: ' + str(evals))
    return best_exp

def monte_best(G, C, M, k, p, num_samples):
    low_g, up_g = 0, 2*pi
    low_b, up_b = 0, pi/2
    best_exp = -1
    for i in range(num_samples):
        angles = [random.uniform(low_g, up_g) if j < p else random.uniform(low_b, up_b) for j in range(2*p)]
        value = -qaoa(angles, G, C, M, k, p)
        if value > best_exp: best_exp = value
    return best_exp
