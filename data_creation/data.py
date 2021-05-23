#!/bin/python

#
# IMPORTS
#

import csv
import time

#
# CONSTANTS
#

# Total search space, rectangle with (x1, y1, x2, y2)
T = [1, 1, 6, 6]
# Search space resolution, where smaller means finer
# Values < 1 are not supported (yet)
res = 1
# Set of masses to test
M = [1, 2, 3]
# Chunk count
chunk_count_per_dim = 3
chunk_count = chunk_count_per_dim ** 2
# Size of a search space chunk with (a, b)
C = [abs(T[2] - T[0] + 1) // chunk_count_per_dim,
     abs(T[3] - T[1] + 1) // chunk_count_per_dim]
# Total number of samples
N = C[1] * C[0] * len(M) * chunk_count // res
# Number of samples per chunk, `abs(C.a) * abs(C.b) * len(M) / res`
N_C = C[1] * C[0] * len(M) // res
# Output folder name
OUT = './output/'

#
# FUNCTIONS
#


# Stub for the sim function
def sim(x, y, m):
    # Simulate longer runtimes
    # time.sleep(2)
    return x * y * m


# this will be 1 process later
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
print('********************************************************************************')
print('ASAI PLANETS - SIMULATION')
print('********************************************************************************')
print()
print(f'Search space with coordinates: ({T[0]}, {T[1]}) ({T[2]}, {T[3]})')
print(f'Search space size: {T[2] - T[0] + 1}x{T[3] - T[1] + 1}')
print(f'Search space resolution: {res}')
print(f'Total number of samples: {N}')
print(f'Chunk count: {chunk_count}')
print(f'Chunk size: {C[0]}x{C[1]}')
print(f'Number of samples per chunk: {N_C}')
print(f'Testing masses: {M}')
print()
print('********************************************************************************')
print()

L = []
for y in range(chunk_count_per_dim):
    for x in range(chunk_count_per_dim):
        print(f'Calculating chunk ({x + y * chunk_count_per_dim + 1} of {chunk_count})')
        T = [1, 1, 6, 6]
        X = [T[0] + x * C[0],
             T[0] + (x + 1) * C[0]]
        Y = [T[1] + y * C[1],
             T[1] + (y + 1) * C[1]]
        L = L + process(X, Y, M)

file_name = f'{OUT}{T[0]}_{T[1]}-{T[2]}_{T[3]}.csv'
with open(file_name, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in L:
        writer.writerow(row)

print()
print('********************************************************************************')
print(f'Wrote results to {file_name}')
print('********************************************************************************')
