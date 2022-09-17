import math
import os
from dotenv import load_dotenv
import timeit
from graph import Graph
import csv
import ray
# from ray.util import inspect_serializability


load_dotenv()


@ray.remote
def worker(graph, n):
    random_hull, indexes = graph.available_hull().random_subset(n, os.getenv('WITH_WEIGHT') == 'True')
    hull = graph.mandatory_hull() + random_hull
    hull = graph.hull_algorithm(hull)
    return (hull, indexes)

def run_samples_parallel(graph, n):
    first = True
    # inspect_serializability(graph, name="graph") # to inspect serialization of ray
    # inspect_serializability(worker, name="worker") # to inspect serialization of ray
    for hull, idx in ray.get([worker.remote(graph, n) for _ in range(0, int(os.getenv('LENGTH_SAMPLE')))]):
        if first or (len(hull) > len(hull_best)) or (len(hull) == len(hull_best) and hull.time < hull_best.time):
            # don't make sense in parallel scenario
            # if not first and os.getenv('WITH_WEIGHT') == 'True':
            #     graph.available_hull().update_weights(indexes, True)
            first = False
            hull_best = hull
            indexes = idx
        # don't make sense in parallel scenario
        # if os.getenv('STOP_ON_FIRST_BEST_SAMPLE') == 'True' and reach_threshold(hull, len(graph)):
        #     break
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
            n = n + math.ceil((maximum - minimum) / 2)
        if maximum - minimum <= 1:
            break
    return hull_best, hull_time


def exec():
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


def bulkexec():
    first = True
    for i in range(1, 5):
        graphname = str(i).zfill(3)
        graph = Graph(graphname)
        start = timeit.default_timer()
        hull_best, hull_time = optimize(graph, os.getenv('FLEXIBLE_BINARY_SEARCH') == 'True')
        stop = timeit.default_timer()
        exec_time = stop - start

        hull_best.write(graph, f"best_{graphname}")
        hull_time.write(graph, f"time_{graphname}")

        dicts = {
            'Graph': graphname, 
            'Time': int(exec_time),
            'Len': len(hull_best.initial_hull()),
            'Alcance': len(hull_best),
            'T': hull_best.time,
            'Len(hulltime)': len(hull_time.initial_hull()),
            'Alcance(hulltime)': len(hull_time),
            'T(hulltime)': hull_time.time,
            'INITIAL_GRAPH': os.getenv('INITIAL_GRAPH'), 
            'CONTAMINANTS': os.getenv('CONTAMINANTS'),
            'LENGTH_SAMPLE': os.getenv('LENGTH_SAMPLE'),
            'STOP_ON_FIRST_BEST_SAMPLE': os.getenv('STOP_ON_FIRST_BEST_SAMPLE'),
            'FLEXIBLE_BINARY_SEARCH': os.getenv('FLEXIBLE_BINARY_SEARCH'),
            'WITH_WEIGHT': os.getenv('WITH_WEIGHT'),
            'VELOCITY': os.getenv('VELOCITY'),
            'PARALLEL': os.getenv('PARALLEL'),
            'MAX_PARALLEL': os.getenv('MAX_PARALLEL'),
            'ONE_IN': os.getenv('ONE_IN')
        }
        with open(f"outputs/results.csv", 'a', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, dicts.keys())
            if first:
                dict_writer.writeheader()
            dict_writer.writerow(dicts)
            first = False


if __name__ == '__main__':
    if os.getenv('PARALLEL') == 'True':
        print(f"numero de cpus detectados pelo ray: {ray._private.utils.get_num_cpus()}")
        # ray.init(num_cpus=12) # to increment cpu usage on ray

    exec()
    # bulkexec()