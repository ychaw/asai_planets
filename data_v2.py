#!/bin/python3

#
# IMPORTS
#

import csv
import time
import multiprocessing
import os
from sim import simulate_orbital_system

#
# CONFIG
#

# Path to output folder
OUT = os.path.join(os.path.abspath(os.getcwd()), 'output')

# Total search space, rectangle with (x1, y1, x2, y2)
T = [-0.4, -1.1, 0.4, -0.3]

# Step size, assumes the search space is a square
step_size = 0.01

# How many digits will be used for coordinates
# Used to avoid floating point errors, because
# that would increase the size of the data set
precision = 15

# Set of masses to test
M = [7e23, 5e25, 3e27]

# Simulation specific
max_runs = 1000
collision_dist = 0.001
stability_cutoff = 3
speed = 0.014
angle = 4


# Estimate for one simulation run in seconds
EST_SIM = 2

#
# FUNCTIONS
#


# Stub for the sim function
def sim_stub(x, y, m):
    # Simulate longer runtimes
    time.sleep(EST_SIM)
    return x * y * m


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
                                             })]


#
# SCRIPT
#
if __name__ == '__main__':
    N_per_dim = int(step_size ** (-1))
    # Total number of samples
    N = N_per_dim ** 2 * len(M)

    # Values to sample the simulation at
    X = [(T[2] - T[0]) * (x * step_size) + T[0]
         for x in range(0, N_per_dim)]
    Y = [(T[3] - T[1]) * (y * step_size) + T[1]
         for y in range(0, N_per_dim)]

    avg_sims_per_core = N / os.cpu_count()
    total_time = EST_SIM * max(avg_sims_per_core, 1)
    chunk_size = int(N // os.cpu_count())
    print('********************************************************************************')
    print('ASAI PLANETS - SIMULATION')
    print('********************************************************************************')
    print()
    print(f'Search space with coordinates: ({T[0]}, {T[1]}) ({T[2]}, {T[3]})')
    print(f'Search space size: {T[2] - T[0]}x{T[3] - T[1]}')
    print(f'Search space resolution: {step_size}')
    print(f'Total number of samples: {N}')
    print(f'Testing masses: {M}')
    print()
    print(f'Using up to {os.cpu_count()} CPUs.')
    print(f'Chunk size: {chunk_size}')
    print(f'Average simulation runs per core: {avg_sims_per_core}')
    print()
    print(f'Estimated total time: {total_time}s')
    print()
    print('********************************************************************************')
    print()

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
    finish_time = time.time()
    elapsed = finish_time - start_time
    avg_time_per_sim = elapsed / N

    print('Done\n')
    print(f'Avg. time per sim: {avg_time_per_sim}s')
    print(f'Finished in {elapsed}s')

    ###########################################################################
    # Write data

    file_name = os.path.join(OUT, f'{T[0]}_{T[1]}-{T[2]}_{T[3]}-N{N}.csv')

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            writer.writerow(row)

    print()
    print('********************************************************************************')
    print(f'Wrote results to {file_name}')
    print('********************************************************************************')
