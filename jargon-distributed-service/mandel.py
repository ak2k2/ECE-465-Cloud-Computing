import numpy as np
from numba import complex64, float32, float64, guvectorize, int32, njit, vectorize
from matplotlib import colors
from matplotlib import pyplot as plt


@njit(int32(complex64, int32))
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


def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float32)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float32)
    c = r1 + r2[:, None] * 1j
    n3 = mandelbrot_numpy(c, maxiter)
    return (r1, r2, n3.T)


res = mandelbrot_set2(-0.74877, -0.74872, 0.06505, 0.06510, 1000, 1000, 2048)

# plot the output
dpi = 200
width = 2000
height = 2000
fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
axes = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)
plt.imshow(
    res[2],
    origin="lower",
    extent=[res[0].min(), res[0].max(), res[1].min(), res[1].max()],
)

plt.savefig("mandelbrot.png")
