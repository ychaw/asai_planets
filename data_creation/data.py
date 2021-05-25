#!/bin/python

#
# IMPORTS
#

import csv
import time
import multiprocessing
import os

#
# CONFIG
#

# Total search space, rectangle with (x1, y1, x2, y2)
# TODO: has to work with following coordinates: [-0.4, -1.1, 0.4, -0.3]
T = [1, 1, 100, 100]

# Search space resolution, where smaller means finer
# Values < 1 are not supported (yet)
res = 1

# Set of masses to test
M = [7e23, 5e25, 3e27]

# Path to output folder
OUT = os.path.join(os.path.abspath(os.getcwd()), 'data_creation', 'output')

# Chunk count
chunk_count_per_dim = 33
# Estimate for one simulation run in seconds
EST_SIM = 0.01

#
# CONSTANTS
#

chunk_count = chunk_count_per_dim ** 2
# Size of a search space chunk with (a, b)
C = [abs(T[2] - T[0] + 1) // chunk_count_per_dim,
     abs(T[3] - T[1] + 1) // chunk_count_per_dim]
# Total number of samples
N = C[1] * C[0] * len(M) * chunk_count // res
# Number of samples per chunk
N_C = C[1] * C[0] * len(M) // res
# Output folder name

#
# FUNCTIONS
#


# Stub for the sim function
def sim(x, y, m):
    # Simulate longer runtimes
    time.sleep(EST_SIM)
    return x * y * m


# Process one chunk identified by start and end values for x and y
# M is the set of masses to test with
def process(X, Y, M):
    L = []
    for x in range(X[0], X[1]):
        for y in range(Y[0], Y[1]):
            for m in M:
                L.append([x, y, m, sim(x, y, m)])
    return L


#
# SCRIPT
#
if __name__ == '__main__':
    time_per_chunk = N_C * EST_SIM
    avg_chunks_per_core = chunk_count / os.cpu_count()
    total_time = time_per_chunk * max(avg_chunks_per_core, 1)
    print('********************************************************************************')
    print('ASAI PLANETS - SIMULATION')
    print('********************************************************************************')
    print()
    print(f'Search space with coordinates: ({T[0]}, {T[1]}) ({T[2]}, {T[3]})')
    print(f'Search space size: {T[2] - T[0]}x{T[3] - T[1]}')
    print(f'Search space resolution: {res}')
    print(f'Total number of samples: {N}')
    print(f'Chunk count: {chunk_count}')
    print(f'Chunk size: {C[0]}x{C[1]}x{len(M)}')
    print(f'Number of samples per chunk: {N_C}')
    print(f'Testing masses: {M}')
    print()
    print(f'Using {os.cpu_count()} CPUs.')
    print(f'Average chunks per core: {avg_chunks_per_core}')
    print(f'Estimated time per chunk: {time_per_chunk}s')
    print()
    print(f'Estimated total time: {total_time}s')
    print()
    print('********************************************************************************')
    print()

    ###########################################################################
    # Create data

    print('Calculating chunks...')
    start_time = time.time()
    args = []

    for y in range(chunk_count_per_dim):
        for x in range(chunk_count_per_dim):
            X = [T[0] + x * C[0],
                 T[0] + (x + 1) * C[0]]
            Y = [T[1] + y * C[1],
                 T[1] + (y + 1) * C[1]]
            args.append([X, Y, M])

    result = []
    with multiprocessing.Pool() as p:
        r = p.starmap_async(process, args)
        result = r.get()

    # Print some info about how long things took
    finish_time = time.time()
    elapsed = finish_time - start_time
    avg_time_per_chunk = elapsed / avg_chunks_per_core
    avg_time_per_sim = avg_time_per_chunk / N_C
    total_time = time_per_chunk * max(avg_chunks_per_core, 1)

    print('Done\n')
    print(f'Avg. time per chunk: {avg_time_per_chunk}s')
    print(f'Avg. time per sim: {avg_time_per_sim}s')
    print(f'Finished in {elapsed}s')

    ###########################################################################
    # Write data

    file_name = os.path.join(OUT, f'{T[0]}_{T[1]}-{T[2]}_{T[3]}.csv')

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for chunk in result:
            for row in chunk:
                writer.writerow(row)

    print()
    print('********************************************************************************')
    print(f'Wrote results to {file_name}')
    print('********************************************************************************')
