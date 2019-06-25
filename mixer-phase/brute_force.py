import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import comb
from itertools import combinations 
import random
from multiprocessing import Process

def generate_graph():
    # Pick a random graph from the atlas
    gi = random.randint(2,995)
    print('Graph index: ' + str(gi))
    G = nx.read_gpickle('../mixer-phase/benchmarks/atlas/' + str(gi) + '.gpickle')
    return G, gi

def brute_force(G, k, p, n):
    comb = combinations(G.nodes, k)
    highest = 0
    for group in list(comb):
        score = 0
        for edge in G.edges:
            for v in group:
                if v == edge[0] or v == edge[1]:
                    score += 1
                    break
        if score > highest:
            highest = score
    return highest

if __name__ == '__main__':
    G, gi = generate_graph()
    brute_force(G, int(len(G.nodes)/2))
