# Requirements
- cartesian coordinates?
- chunk search space
  - rect with 2 points as format -> filename: x1-y1_x2-y2.csv?
  - constant resolution over entire search space
- app should use args x1, Y1, x2, y2 for search space
- CSV rows should look like: X, Y, M, O

## Parameters
- T: Total search space, rectangle with (x1, y1, x2, y2)
- res: search space resolution, where smaller means finer
- M: Set of masses to test
- C: Size of a search space chunk with (a, b)
- N: total number of samples, `abs(T.x2 - T.x1) * abs(T.y2 - T.y1) * len(M) / res`
- N_C: number of samples per chunk, `abs(C.a) * abs(C.b) * len(M) / res`

## Data creation
1. Sample search space at n equidistant points with offset `size(T_x) // N` and `size(T_y) // N` for all values of M
2. Evaluate orbit for each point for t timesteps
3. Create/Open file
4. Write data to file

---

Test whether it is faster/feasible to write every calculated value to disk at once or write everytime a value is calculated

## Sample values
Use either pandas or numpy datastructures for speed over 2-dimensional lists

## CSV's
### Reading
```python
import csv

with open('eggs.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        print(', '.join(row))
```

### Writing
```python
import csv

with open('eggs.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
```

## Parallelization
```python
import concurrent.futures

with concurrent.futures.ProcessPoolExecutor() as executor:
    results = [exectutor.submit(do_something, args) for _ in range(10)]

    for f in concurrent.futures.as_completed(results):
        pass
```


```python
from multiprocessing import Pool

def f(x):
    return x

def g(x, y):
    return (x, y)

if __name__ == '__main__':
    with Pool(5) as p:
        p.map(f, [1, 2, 3])
# or like this:
        p.starmap_async(g, [(1, 2), (3, 4), (5, 6)])
```
