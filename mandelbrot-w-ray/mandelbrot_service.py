"""
Extremely fast Mandelbrot set computation using numpy and numba (credit to Jean-François Puget: https://gist.github.com/jfpuget/60e07a82dece69b011bb)

"""

import time as t

import matplotlib.colors as mcolors
import numpy as np
import ray
from matplotlib import pyplot as plt
from numba import complex64, float32, float64, guvectorize, int32, njit


@njit(int32(complex64, int32), fastmath=True, cache=True)
def mandelbrot(c, maxiter):
    nreal = 0
    real = 0
    imag = 0
    for n in range(maxiter):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        if real * real + imag * imag > 4.0:
            return n
    return 0


@guvectorize([(complex64[:], int32[:], int32[:])], "(n),()->(n)", target="parallel")
def mandelbrot_numpy(c, maxit, output):
    maxiter = maxit[0]
    for i in range(c.shape[0]):
        output[i] = mandelbrot(c[i], maxiter)


@ray.remote
def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float32)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float32)
    c = r1 + r2[:, None] * 1j
    n3 = mandelbrot_numpy(c, maxiter)
    return (r1, r2, n3.T)


def save_result(res):
    # Extract the iteration counts from the result
    iteration_counts = res[2]

    # Normalize the iteration counts for coloring
    norm = mcolors.PowerNorm(0.3)  # Using a PowerNorm for non-linear scaling

    # Create a new figure and set the aspect ratio
    plt.figure(figsize=(10, 10))
    plt.axis("off")  # Turn off the axis
    plt.imshow(iteration_counts, cmap="nipy_spectral", norm=norm)
    plt.savefig("enhanced_mandelbrot.png", bbox_inches="tight", pad_inches=0, dpi=200)


# # bounds = (-2.5, 1.5, -2.0, 2.0) # full mandelbrot
# # bounds = (-0.8, -0.7, 0.05, 0.15)  # valley of seahorses
# # bounds = (0.175, 0.375, -0.1, 0.1) # elephant valley
# bounds = (-1.25066, -1.25061, 0.02012, 0.02017)  # antenna valley

# st = t.time()
# res = mandelbrot_set2(*bounds, 1000, 1000, 10000000)
# print(t.time() - st)

# # Assuming 'res' is the result from your mandelbrot_set2 function
# plot_mandelbrot(res)
