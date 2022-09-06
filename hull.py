import os
import random
import math
import heapq
import threading
import networkx as nx

class Hull:
    def __init__(self, array = None):
        self.infection = {} # mostra por quais vertices um vertice foi contaminado
        self.hull = []
        self.weights = []
        self.time = 0
        self.lock = threading.Lock()
        self.times = {} # tempo em houve a entrada do vertice
        self.times[self.time] = array or []
        for v in array or []:
            self.infection[v] = None
            self.hull.append(v)

    def append(self, other):
        self.hull.append(other)
        self.times[self.time].append(other)

    def append_with_weight(self, other, weight):
        self.hull.append(other)
        self.weights.append(weight)

    def __add__(self, other):
        return Hull(self.hull + other.hull)

    def __len__(self):
        return len(self.hull)
    
    def __contains__(self, key):
        return key in self.hull

    def __iter__(self):
        for v in self.hull:
            yield v

    def weighted_selection_without_replacement(self, n):
        # https://colab.research.google.com/drive/14Vnp-5xRHLZYE_WTczhpoMW2KdC6Cnvs#scrollTo=wEwWxLMKbpZn
        with self.lock:
            elt = [(math.log(random.random()) / self.weights[i], i) for i in range(len(self.weights))]
            return [x[1] for x in heapq.nlargest(n, elt)]

    def random_subset(self, n, with_weight = False):
        if with_weight:
            indexes = self.weighted_selection_without_replacement(n)
        else:
            indexes = random.sample(range(len(self.hull)), n)
        sample = [self.hull[i] for i in indexes]
        return Hull(sample), indexes

    def update_weights(self, indexes, internal = False):
        with self.lock:
            if internal:
                for i in indexes:
                    self.weights[i] *= int(os.getenv('VELOCITY')) 
            else:
                sum_indexes_weights = sum(self.weights[i] for i in indexes)
                sum_non_indexes = sum(weight for weight in self.weights)
                remain = (((4 * sum_non_indexes) - sum_indexes_weights) + len(indexes)) // len(indexes)
                for i in indexes:
                    self.weights[i] += remain
            biggest = max(self.weights)
            if biggest > 1000000: # normalize weights
                self.weights = [(weight * 1000000) / biggest for weight in self.weights]

    def evolve(self, array):
        if array:
            self.time += 1
            self.times[self.time] = array
            self.hull += array

    def last_border(self):
        return self.times[self.time]

    """
    contaminado na chave "i" tem a lista de vértices que o contaminaram
    os contaminados já no fecho inicial não tem uma lista e sim são iguais a None
    retorna True se for um novo contaminado por 2 elementos
    retorna False caso contrário
    """
    def infect(self, vcontaminant, vcontaminated):
        if vcontaminated in self.infection:
            if self.infection[vcontaminated] is None:
                return False
            if len(self.infection[vcontaminated]) < int(os.getenv('CONTAMINANTS')) and vcontaminant not in self.infection[vcontaminated]:
                self.infection[vcontaminated].add(vcontaminant)
                if len(self.infection[vcontaminated]) == int(os.getenv('CONTAMINANTS')):
                    return True
        else:
            self.infection[vcontaminated] = set()
            self.infection[vcontaminated].add(vcontaminant)
            if len(self.infection[vcontaminated]) == int(os.getenv('CONTAMINANTS')):
                # só existe essa condição para no futuro podermos evoluir pra qualquer N >= 1, aqui no caso N=2
                return True
        return False

    def initial_hull(self):
        return self.times[0]

    def write(self, graph, path):
        g = nx.Graph(graph.graph)
        for i in range(graph.vmin, graph.vmax + 1):
            g.add_node(i)
        for time, array in self.times.items():
            for i in array:
                g.nodes[i]['Time'] = time
        nx.write_gexf(g, f"outputs/hull_{path}.gexf")