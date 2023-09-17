# README: Computing the Mandelbrot Set in Serial and Parallel (HW1)

##  Overview

The Mandelbrot Set (named after Benoit Mandelbrot) is a mathematical object that represents a collection of complex numbers. It is a fractal, meaning it has a self-similar pattern at any level of magnification.

### Process of Generating the Mandelbrot Set

The equation used to generate the Mandelbrot Set is:

\[
z_{n+1} = z_n^2 + c
\]

Where:
- \( z_{n+1} \) and \( z_n \) are complex numbers in the sequence.
- \( c \) is the complex number being tested for membership in the Mandelbrot Set.
- \( z_0 = 0 \)

### Sequential Algorithm

1. Start with \( z_0 = 0 \) and \( c \) as the complex number you are testing.
2. Calculate \( z_{n+1} \) using the equation \( z_{n+1} = z_n^2 + c \).
3. Repeat the calculation for a number of iterations or until \( |z_{n+1}| > 2 \).
4. If \( |z_{n+1}| > 2 \), then \( c \) is not in the Mandelbrot Set.
5. If after a large number of iterations \( |z_{n+1}| \) has not exceeded 2, then \( c \) is considered to be in the Mandelbrot Set.



## Problem Summary

Row based parallelism: In this method, each thread is responsible for processing a subset of rows.
```
def mandelbrot_row(y, w, h, max_iter):
```
The function can be distributed to multiple cores using a process pool (star map).

Grid based parallelism: The problem is broken down into N grids (where N is the nuber of cpu cores available). Each grid is processed in parallel by a different process, and each process spawns 32 threads. The threads are responsible for processing a subset of rows in the grid.


## Results

### Without Multiprocessing

The program runs on a single thread, processing rows one by one. The thread and process ID (PID) are the same for each row.

```
Thread: MainThread, PID: 36409 - Processing row 0
...
Thread: MainThread, PID: 36409 - Processing row 99
...
```

**Time taken: 3.4725 seconds**

### Row-Based Parallelism

The program uses multiple threads to process rows in parallel. Each thread is assigned a different PID, and they process different rows simultaneously.

```
Thread: MainThread, PID: 36417 - Processing row 0
...
Thread: MainThread, PID: 36424 - Processing row 99
```

**Time taken: 2.0996 seconds**

### Grid-Based Multiprocessing

The program uses multiprocessing to divide the data into grids and processes each grid in parallel. Each process is assigned a different PID.

```
PID: 36428 - Processing grid from row 0 to 12, col 0 to 12
...
PID: 36430 - Processing grid from row 84 to 96, col 84 to 96
```

**Time taken: 1.8262 seconds**

## Conclusion

The use of parallelism and multiprocessing significantly improves the time needed to compute the mandelbrot set. Grid-based multiprocessing offers the best performance, reducing the time taken to approximately half compared to the single-threaded approach. The time reduction is non linear with respect to output dimesions (width and height) untill a saturation point (function of num cores and machine info), but SHOULD ideally be linear wrt. num_iterations since each iteration is independent of other pixels outside the scope of its process/thread.

