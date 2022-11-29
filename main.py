import math
import os
from dotenv import load_dotenv
import timeit
from graph import Graph
import csv
# import ray
import itertools
# from ray.util import inspect_serializability


load_dotenv()


# @ray.remote
# def worker(graph, n):
#     random_hull, indexes = graph.available_hull().random_subset(n, os.getenv('WITH_WEIGHT') == 'True')
#     hull = graph.mandatory_hull() + random_hull
#     hull = graph.hull_algorithm(hull)
#     return (hull, indexes)

# def run_samples_parallel(graph, n):
#     first = True
#     # inspect_serializability(graph, name="graph") # to inspect serialization of ray
#     # inspect_serializability(worker, name="worker") # to inspect serialization of ray
#     for hull, idx in ray.get([worker.remote(graph, n) for _ in range(0, int(os.getenv('LENGTH_SAMPLE')))]):
#         if first or (len(hull) > len(hull_best)) or (len(hull) == len(hull_best) and hull.time < hull_best.time):
#           # don't make sense in parallel scenario
#           # if not first and os.getenv('WITH_WEIGHT') == 'True':
#           #     graph.available_hull().update_weights(indexes, True)
#           first = False
#           hull_best = hull
#           indexes = idx
#         # don't make sense in parallel scenario
#         # if os.getenv('STOP_ON_FIRST_BEST_SAMPLE') == 'True' and reach_threshold(hull, len(graph)):
#         #     break
#     return hull_best, indexes

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
    lastrun = 0
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
                print(f"grafo: {os.environ['INITIAL_GRAPH']}.{os.environ['FILE_INPUT_EXTENSION']}")
                print(f"vmin: {graph.vmin}")
                print(f"vmax: {graph.vmax}")
                print(f"tamanho do grafo: {len(graph)}")
                print()
                if flexible:
                    minimum = 1
            maximum = n
            n = (maximum + minimum) // 2
            if n == minimum or lastrun == 1:
                lastrun += 1
        else:
            minimum = n
            n = n + math.ceil((maximum - minimum) / 2)
            if n == maximum or lastrun == 1:
                lastrun += 1
        # if maximum - minimum <= 1:
        #     break
        if lastrun == 2:
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
    def unzip(collection):
        return list(zip(*enumerate(collection)))

    first = True

    files_idx, files = unzip(range(0, 60))
    lens_idx, lens = unzip([10, 50, 100, 500])
    one_in_idx, one_in = unzip([10, 100])
    velocities_idx, velocities = unzip([1, 2])
    stop_on_first_best_samples_idx, stop_on_first_best_samples = unzip(["True", "False"])

    for comb in itertools.product(files_idx, lens_idx, one_in_idx, velocities_idx, stop_on_first_best_samples_idx):
        os.environ["INITIAL_GRAPH"]=str(files[comb[0]]).zfill(3)
        os.environ["LENGTH_SAMPLE"]=str(lens[comb[1]])
        os.environ["ONE_IN"] = str(one_in[comb[2]])
        os.environ["VELOCITY"]= str(velocities[comb[3]])
        os.environ["STOP_ON_FIRST_BEST_SAMPLE"]=str(stop_on_first_best_samples[comb[4]])

        print(f"INITIAL_GRAPH: {os.environ['INITIAL_GRAPH']}")
        print(f"LENGTH_SAMPLE: {os.environ['LENGTH_SAMPLE']}")
        print(f"ONE_IN: {os.environ['ONE_IN']}")
        print(f"VELOCITY: {os.environ['VELOCITY']}")
        print(f"STOP_ON_FIRST_BEST_SAMPLE: {os.environ['STOP_ON_FIRST_BEST_SAMPLE']}")

        # default following:
        os.environ["CONTAMINANTS"]="2"
        os.environ["FLEXIBLE_BINARY_SEARCH"]="True"
        os.environ["WITH_WEIGHT"]="True"
        os.environ["PARALLEL"]="False"
        os.environ["MAX_PARALLEL"] = "8"
        os.environ["FILE_INPUT_EXTENSION"] = "tgf"

        try:
            graph = Graph(os.environ['INITIAL_GRAPH'])
        except FileNotFoundError as err:
            print("file not found: ", err)
            continue
        start = timeit.default_timer()
        hull_best, hull_time = optimize(graph, os.getenv('FLEXIBLE_BINARY_SEARCH') == 'True')
        stop = timeit.default_timer()
        exec_time = stop - start

        hull_best.write(graph, f"best_{os.environ['INITIAL_GRAPH']}")
        hull_time.write(graph, f"time_{os.environ['INITIAL_GRAPH']}")

        dicts = {
            'grafo': f"{os.environ['INITIAL_GRAPH']}.{os.environ['FILE_INPUT_EXTENSION']}", 
            'vmin': graph.vmin,
            'vmax': graph.vmax,
            'tamanho_grafo': len(graph),
            'tam_menor_fecho_inicial': len(hull_best.initial_hull()),
            'tempo_cotaminacao': hull_best.time,
            'tempo_execucao': int(exec_time),
            'LENGTH_SAMPLE': os.getenv('LENGTH_SAMPLE'),
            'ONE_IN': os.getenv('ONE_IN'),
            'VELOCITY': os.getenv('VELOCITY'),
            'STOP_ON_FIRST_BEST_SAMPLE': os.getenv('STOP_ON_FIRST_BEST_SAMPLE')
            # 'Alcance': len(hull_best),
            # 'Len(hulltime)': len(hull_time.initial_hull()),
            # 'Alcance(hulltime)': len(hull_time),
            # 'T(hulltime)': hull_time.time,
            # 'INITIAL_GRAPH': os.getenv('INITIAL_GRAPH'), 
            # 'CONTAMINANTS': os.getenv('CONTAMINANTS'),
            # 'FLEXIBLE_BINARY_SEARCH': os.getenv('FLEXIBLE_BINARY_SEARCH'),
            # 'WITH_WEIGHT': os.getenv('WITH_WEIGHT'),
            # 'PARALLEL': os.getenv('PARALLEL'),
            # 'MAX_PARALLEL': os.getenv('MAX_PARALLEL'),
            # 'FILE_INPUT_EXTENSION': os.getenv('FILE_INPUT_EXTENSION'),
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

    # exec()
    bulkexec()