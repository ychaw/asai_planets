#!/bin/python3

#
# IMPORTS
#

import csv
import multiprocessing
import os
import time

from cpuinfo import get_cpu_info
from numpy import arange

from sim_v2 import simulate_orbital_system

#
# CONFIG
#

# Path to output folder
OUT = os.path.join(os.path.abspath(os.getcwd()), 'output')

# Total search space, rectangle with (x1, y1, x2, y2)
# T = [-0.4, 1.1, 0.4, 0.3]
T = [-1.5, 1.5, 1.5, -1.5]

# Step size, assumes the search space is a square
step_size = 0.01

# How many digits will be used for coordinates
# Used to avoid floating point errors, because
# that would increase the size of the data set
precision = 14

# Set of masses to test
M = [1e26, 1e27, 1e28]

# Simulation specific
max_runs = 1000
collision_dist = 0.001
stability_cutoff = 15
speed = 0.015
angle = None


# Estimate for one simulation run per core per ghz
EST_SIM = 4.150119662004526e-05

#
# FUNCTIONS
#


# Process one chunk identified by start and end values for x and y
# M is the set of masses to test with
def process(x, y, m):
    return [x, y, m, simulate_orbital_system(max_runs,
                                             collision_dist,
                                             stability_cutoff,
                                             {
                                                 'position': (x, y),
                                                 'mass': m,
                                                 'speed': speed,
                                                 'angle': angle
                                             }, False)]


#
# SCRIPT
#
if __name__ == '__main__':

    X = list(arange(min(T[0], T[2]), max(T[0], T[2]) + step_size, step_size))
    Y = list(arange(min(T[1], T[3]), max(T[1], T[3]) + step_size, step_size))

    N = len(X) * len(Y) * len(M)

    ghz = get_cpu_info()['hz_actual'][0] / 1e9
    cpus = os.cpu_count()
    total_time = round(EST_SIM * cpus * ghz * N + 3, 3)

    avg_sims_per_core = N / cpus
    chunk_size = int(N // cpus)

    print('\n********************************************************************************')
    print('ASAI PLANETS - SIMULATION')
    print('********************************************************************************')
    print()
    print(f'Search space with coordinates: ({T[0]}, {T[1]}) ({T[2]}, {T[3]})')
    print(f'Search space size: {len(X)} x {len(Y)}')
    print(f'Search space resolution: {step_size}')
    print(f'Testing masses: {M}')
    print(f'Total number of samples: {N}')
    print()
    print(f'Using up to {os.cpu_count()} CPUs.')
    print(f'Chunk size: {chunk_size}')
    print(f'Average simulation runs per core: {avg_sims_per_core}')
    print()
    print(f'Estimated total time: {total_time}s')
    print()
    print('********************************************************************************\n')

    ###########################################################################
    # Create data

    args = [[round(x, precision), round(y, precision), m]
            for m in M
            for x in X
            for y in Y]

    result = []

    start_time = time.time()

    with multiprocessing.Pool() as p:
        r = p.starmap_async(process, args, chunk_size)
        result = r.get()

    # Print some info about how long things took
    elapsed = time.time() - start_time
    avg_time_per_sim = elapsed / N
    avg_time_per_sim_per_core_per_ghz = avg_time_per_sim / cpus / ghz

    print('Done\n')
    print(f'Avg. time per sim: {avg_time_per_sim}s')
    print(f'Avg. time per sim per core per ghz: {avg_time_per_sim_per_core_per_ghz}s')
    print(f'\nFinished in {elapsed:.3}s')

    ###########################################################################
    # Write data

    file_name = os.path.join(OUT, f'{T[0]}_{T[1]}-{T[2]}_{T[3]}-N{N}.csv')

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            writer.writerow(row)

    print('\n********************************************************************************')
    print(f'Wrote results to {file_name}')
    print('********************************************************************************\n')
