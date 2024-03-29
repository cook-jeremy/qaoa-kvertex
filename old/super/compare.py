import datetime
import os
import pickle

import matplotlib.pyplot as plt
import networkx as nx
# from dicke_hprime_parityring import dicke_hprime_parityring
# from pring_ps_pring import pring_ps_pring
from brute_force import brute_force
from dicke_ps_ring import dicke_ps_ring
from ring_ps_ring import ring_ps_ring

def get_exp(G, gi, k, p, num_steps, method, method_string):
    exp = None
    found = False
    exp_dict = {}
    path = '/home/montypylon/lanl/qaoa-kvertex/hpc/data/' + method_string + '.exp'

    if os.path.exists(path):
        with open(path, 'rb') as f:
            try:
                exp_dict = pickle.load(f)
                key = tuple([gi, k])
                if key in exp_dict:
                    found = True
                    exp = exp_dict[key]
            except Exception as e:
                print('Error opening dictionary for ' + method_string)
                print(e)

    if not found or exp is None:
        exp, angles = method(G, k, p, num_steps)
        key = tuple([gi, k])
        exp_dict[key] = exp
        pickle.dump(exp_dict, open(path, 'wb'))

    return exp

def compare():
    # min: 1, max: 995
    start = 1
    end = 10
    p = 1
    num_steps = 25
    x = []
    y1 = []
    y2 = []
    y3 = []

    for gi in range(start, end+1):
        print(str(gi) + '/' + str(end) + '\t' + str(datetime.datetime.now().time()))
        G = nx.read_gpickle('atlas/' + str(gi) + '.gpickle')
        k = int(len(G.nodes)/2)
        if k == 0:
            k = 1
        #x.append('gi=' + str(gi) + ',n=' + str(len(G.nodes)) + ',k=' + str(k))
        x.append(gi)
        y1.append(get_exp(G, gi, k, p, num_steps, brute_force, 'brute_force'))
        y2.append(get_exp(G, gi, k, p, num_steps, dicke_ps_ring, 'dicke_ps_ring'))
        y3.append(get_exp(G, gi, k, p, num_steps, ring_ps_ring, 'ring_ps_ring'))

    for i in range(0, len(y1)):
        y2[i] /= y1[i]
        y3[i] /= y1[i]
        y1[i] = 1

    plt.plot(x, y1, '-b', label='optimal')
    plt.plot(x, y2, '-go', label='dicke_ps_ring')
    plt.plot(x, y3, '-ro', label='ring_ps_ring')

    plt.legend()

    plt.xlabel('Graph atlas index')
    plt.ylabel('Approximation ratio')
    plt.title('Approximation ratio vs. graph atlas\np=' + str(p) + ', k=floor(n/2), iter=' + str(num_steps))
    plt.show()
        
if __name__ == '__main__':
    #generate_graphs()
    compare()
