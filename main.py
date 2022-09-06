import math
import threading
import queue
import os
from dotenv import load_dotenv
import timeit
from graph import Graph
# import numba as nb

load_dotenv()


# class Worker(multiprocessing.Process):
#     def __init__(self, graph, n, q, lock):
#         super(Worker, self).__init__()
#         self.graph = graph
#         self.n = n
#         self.q = q
#         self.lock = lock
#         
# 
#     def run(self):
#         random_hull, indexes = self.graph.available_hull().random_subset(self.n, os.getenv('WITH_WEIGHT') == 'True', self.lock)
#         hull = self.graph.mandatory_hull() + random_hull
#         hull = self.graph.hull_algorithm(hull)
#         self.q.put((hull, indexes))


# @nb.jit(forceobj=True, nogil = True)
# def worker(graph, n, q):
#     random_hull, indexes = graph.available_hull().random_subset(n, os.getenv('WITH_WEIGHT') == 'True')
#     hull = graph.mandatory_hull() + random_hull
#     hull = graph.hull_algorithm(hull)
#     q.put((hull, indexes))


def run_samples_parallel(graph, n):
    first = True
    q = queue.Queue()
    nthreads = 0
    cnt = 0
    threads = []
    while cnt < int(os.getenv('LENGTH_SAMPLE')):
        remain = int(os.getenv('LENGTH_SAMPLE')) - cnt # para terminar
        if nthreads < remain and nthreads < int(os.getenv('MAX_PARALLEL')): # and remain >= int(os.getenv('MAX_PARALLEL')):
            nthreads += 1
            thread = threading.Thread(target=worker, args=(graph, n, q))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        else:
            hull, idx = q.get()
            nthreads -= 1
            if first or (len(hull) > len(hull_best)) or (len(hull) == len(hull_best) and hull.time < hull_best.time):
                if not first and os.getenv('WITH_WEIGHT') == 'True':
                    graph.available_hull().update_weights(indexes, True)
                first = False
                hull_best = hull
                indexes = idx
            if os.getenv('STOP_ON_FIRST_BEST_SAMPLE') == 'True' and reach_threshold(hull, len(graph)):
                break
            cnt += 1
    return hull_best, indexes


def run_samples(graph, n):
    first = True
    for cnt in range(0, int(os.getenv('LENGTH_SAMPLE'))):
        random_hull, idx = graph.available_hull().random_subset(n, os.getenv('WITH_WEIGHT') == 'True')
        hull = graph.mandatory_hull() + random_hull
        hull = graph.hull_algorithm(hull)
        if first or (len(hull) > len(hull_best)) or (len(hull) == len(hull_best) and hull.time < hull_best.time):
            if not first and os.getenv('WITH_WEIGHT') == 'True':
                graph.available_hull().update_weights(indexes, True)
            first = False
            hull_best = hull
            indexes = idx
        if os.getenv('STOP_ON_FIRST_BEST_SAMPLE') == 'True' and reach_threshold(hull, len(graph)):
            break
    return hull_best, indexes


def reach_threshold(hull, vmax):
    return len(hull) == vmax


def optimize(graph, flexible = False):
    # when flexible is True run a reset on minimum to restart binary search, it is equivalent to run binary search multiple times
    minimum = 1
    maximum = len(graph.available_hull())
    n = math.ceil(maximum / 2)
    first_hull_time = True
    first_hull = True
    while True:
        print('minimum: {}, maximum: {}, n: {}'.format(minimum, maximum, n))
        
        if os.getenv('PARALLEL') == 'True':
            hull, indexes = run_samples_parallel(graph, n)
        else:
            hull, indexes = run_samples(graph, n)
        
        if reach_threshold(hull, len(graph)):
            if first_hull_time or (hull.time <= hull_time.time and len(hull.initial_hull()) < len(hull_time.initial_hull())):
                first_hull_time = False
                hull_time = hull
            if first_hull or len(hull.initial_hull()) < len(hull_best.initial_hull()) or (len(hull.initial_hull()) == len(hull_best.initial_hull()) and hull.time < hull_best.time):
                if not first_hull and os.getenv('WITH_WEIGHT') == 'True':
                    graph.available_hull().update_weights(indexes)
                first_hull = False
                hull_best = hull
                print("tamanho do MELHOR FECHO INICIAL: {}".format(len(hull_best.initial_hull())))
                print("numero de vertices alcancados pelo MELHOR FECHO INICIAL: {}".format(len(hull_best)))
                print("tempo do MELHOR FECHO INICIAL: {}".format(hull_best.time))
                print()
                if flexible:
                    minimum = 1
            maximum = n
            n = (maximum + minimum) // 2
        else:
            minimum = n
            n = n + math.ceil((maximum - minimum) / 2) # maximum - max(math.ceil((maximum - n) / 2), 1) # (maximum - n) // 2
        if maximum - minimum <= 1:
            break
    return hull_best, hull_time


def main():
    graph = Graph(f"{os.getenv('INITIAL_GRAPH')}")
    start = timeit.default_timer()

    hull_best, hull_time = optimize(graph, os.getenv('FLEXIBLE_BINARY_SEARCH') == 'True')
    
    stop = timeit.default_timer()
    print(f'\nfinalizado em {stop - start} segundos\n')

    # print("vertices do MELHOR FECHO INICIAL: {}".format(hull_best))
    print("tamanho do MELHOR FECHO INICIAL: {}".format(len(hull_best.initial_hull())))
    print("numero de vertices alcancados pelo MELHOR FECHO INICIAL: {}".format(len(hull_best)))
    print("tempo do MELHOR FECHO INICIAL: {}".format(hull_best.time))
    print()

    # print("vertices do FECHO DE MELHOR TEMPO: {}".format(hull_time))
    print("tamanho do FECHO DE MELHOR TEMPO: {}".format(len(hull_time.initial_hull())))
    print("numero de vertices alcancados pelo MELHOR FECHO INICIAL: {}".format(len(hull_time)))
    print("tempo do FECHO DE MELHOR TEMPO: {}".format(hull_time.time))

    hull_best.write(graph, f"best_{os.getenv('INITIAL_GRAPH')}")
    hull_time.write(graph, f"time_{os.getenv('INITIAL_GRAPH')}")


if __name__ == '__main__':
    main()