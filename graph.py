import math
import os
from hull import Hull
# import csv

class Graph:
    def __init__(self, path):
        self.reset_graph()
        self.avl_hull = None
        self.mnd_hull = None
        self.read(path)
        # self.write_graph(path)

    def reset_graph(self):
        self.graph = {}
        self.nedges = 0
        self.vmax = 0
        self.vmin = math.inf

    # def write_graph(self, path):
    #     dicts = []
    #     with open(f"inputs/{path}.txt") as f:
    #         while True:
    #             row = f.readline()
    #             if not row:
    #                 break
    #             v1, v2 = int(row.split()[0]), int(row.split()[1])
    #             dicts.append({'Source': v1, 'Target': v2, 'Type': 'Undirected'})
    #     with open(f"outputs/edges_{path}.csv", 'w', newline='') as output_file:
    #         dict_writer = csv.DictWriter(output_file, dicts[0].keys())
    #         dict_writer.writeheader()
    #         dict_writer.writerows(dicts)

    def read(self, path):
        self.path = f"inputs/{path}.{os.getenv('FILE_INPUT_EXTENSION')}"
        with open(self.path) as f:
            while True:
                row = f.readline()
                if not row:
                    break
                self.nedges += 1
                if "#" in row:
                    print('encontrado um #')
                    self.reset_graph()
                    continue
                v1, v2 = int(row.split()[0]), int(row.split()[1])
                self.vmin = min(self.vmin, v1, v2)
                self.vmax = max(self.vmax, v1, v2)
                self.add_on_adjacenty_list_undirected(v1, v2)

    def __len__(self):
        # o numero de vertices do grafo
        # obs.: vertices nao encontrados na entrada (entre vmin e vmax) sao considerados como vertices isolados de grau 0
        return self.vmax

    def add_on_adjacenty_list_undirected(self, u, w):
        self.add_on_adjacency_list(u, w)
        self.add_on_adjacency_list(w, u)

    def add_on_adjacency_list(self, u, w):
        if u not in self.graph:
            self.graph[u] = set()
            self.graph[u].add(w)
        else:
            self.graph[u].add(w)

    # @functools.lru_cache
    def mandatory_hull(self):
        if self.mnd_hull is None:
            # conjunto com o vertices que necessariamente devem estar no fecho inicial pois de outra forma nao seriam contaminados
            hull = Hull()
            for i in range(self.vmin, self.vmax + 1):
                if i not in self.graph: # vertice de grau 0
                    hull.append(i)
                elif len(self.graph[i]) < int(os.getenv('CONTAMINANTS')): # vertices de grau mais baixo que o numero de vizinhos necessarios para contaminar
                    hull.append(i)
            self.mnd_hull = hull
        return self.mnd_hull

    # @functools.lru_cache
    def available_hull(self):
        if self.avl_hull is None:
            # conjunto de vertices que podem ser selecionados para serem parte de um hull inicial
            hull = Hull()
            for i in range(self.vmin, self.vmax + 1):
                if i not in self.mandatory_hull():
                    hull.append_with_weight(i, 1)
            self.avl_hull = hull
        return self.avl_hull

    def evolve_hull(self, hull):
        hullarray = []
        for v in hull.last_border():
            if v in self.graph:
                for w in self.graph[v]:
                    wasinfected = hull.infect(v, w)
                    if wasinfected:
                        hullarray.append(w)
        hull.evolve(hullarray)
        return hull

    def hull_algorithm(self, hull):
        last_hull_length = len(hull)
        while True:
            # print("t: {}, fecho: {}".format(t, fecho))
            hull = self.evolve_hull(hull)
            if len(hull) == last_hull_length:
                break
            else:
                last_hull_length = len(hull)
            # print("novo_fecho: {}".format(novo_fecho))
        return hull