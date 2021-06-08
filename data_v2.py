#!/bin/python3

#
# IMPORTS
#

import csv
import multiprocessing
import os
import time
from datetime import datetime, timedelta

from cpuinfo import get_cpu_info
from numpy import linspace as np_linspace

from sim_v2 import simulate_orbital_system

#
# CONFIG
#

# Path to output folder
OUT = os.path.join(os.path.abspath(os.getcwd()), 'output')

# Total search space, rectangle with (x1, y1, x2, y2) (top-left, bottom-right)

# zoomed on the lower right quadrant
# T = [0.4, -0.25, 0.8, -0.65]
# T = [0.55, -0.4, 0.65, -0.5] # more zoooom

# T = [-1.5, 1.5, 1.5, -1.5]
T = [-1.2, 1.2, 1.2, -1.2]

# How many samples per axis should be calculated
resolution_per_axis = 100

# Set of masses to test
M = [1e28, 1e29, 1e30]
# M = [3e27]

# Simulation specific
max_runs = 1000
collision_dist = 0.001
stability_cutoff = 200  # 15
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
    return [
        x, y, m,
        simulate_orbital_system(
            max_runs,
            collision_dist,
            stability_cutoff,
            {
                'position': (x, y),
                'mass': m,
                'speed': speed,
                'angle': angle
            },
            False  # True
        )
    ]


#
# SCRIPT
#
def main():

    X, stepX = np_linspace(T[0], T[2], resolution_per_axis, retstep=True)
    Y, stepY = np_linspace(T[1], T[3], resolution_per_axis, retstep=True)

    N = len(X) * len(Y) * len(M)

    ghz = get_cpu_info()['hz_actual'][0] / 1e9
    cpus = os.cpu_count()
    total_time = EST_SIM * cpus * ghz * N

    avg_sims_per_core = N / cpus
    chunk_size = int(N // cpus)

    print('\n********************************************************************************')
    print('ASAI PLANETS - SIMULATION')
    print('********************************************************************************')
    print()
    print(f'Search space with coordinates: ({T[0]}, {T[1]}) ({T[2]}, {T[3]})')
    print(f'Search space size: {len(X)} x {len(Y)}')
    print(f'Search space step size: {stepX:.5f} x {stepY:.5f}')
    print(f'Testing masses: {M}')
    print(f'Total number of samples: {N}')
    print()
    print(f'Using up to {os.cpu_count()} CPUs.')
    print(f'Chunk size: {chunk_size}')
    print(f'Average simulation runs per core: {avg_sims_per_core}')
    print()
    print('Estimated total time: {} [HH:MM:SS]'.format(str(timedelta(seconds=total_time))))
    print()
    print('********************************************************************************\n')

    if input('Do you want to proceed? [Y/N] \n\n').upper() not in ['Y', 'J']:
        return

    args = [[x, y, m] for m in M for y in Y for x in X]
    del X, Y

    start_time = time.time()

    print('\n********************************************************************************')
    print('********************************************************************************\n')
    print('Started at: ' + datetime.fromtimestamp(start_time).strftime('%d.%m.%Y %H:%M:%S'))

    ###########################################################################
    # Create data

    result = []

    with multiprocessing.Pool() as p:
        r = p.starmap_async(process, args, chunk_size)
        result = r.get()

    # Print some info about how long things took
    elapsed = time.time() - start_time
    avg_time_per_sim = elapsed / N
    avg_time_per_sim_per_core_per_ghz = avg_time_per_sim / cpus / ghz

    print('\n********************************************************************************')
    print('\nDone\n')
    print(f'Avg. time per sim: {avg_time_per_sim}s')
    print(f'Avg. time per sim per core per ghz: {avg_time_per_sim_per_core_per_ghz}s')
    print('\nFinished in: {} [HH:MM:SS]'.format(str(timedelta(seconds=elapsed))))

    ###########################################################################
    # Write data

    file_name = os.path.join(OUT, f'X[{T[0]}, {T[1]}]__Y[{T[2]}, {T[3]}]__M{M}__N[{N}].csv')

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            writer.writerow(row)

    print('\n********************************************************************************')
    print(f'Wrote results to {file_name}')
    print('********************************************************************************\n')


if __name__ == '__main__':
    main()