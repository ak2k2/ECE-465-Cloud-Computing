import numpy as np
from PIL import Image
from numba import jit


@jit
def make_mandelbrot(width, height, max_iterations):
    result = np.zeros((height, width))

    # for each pixel at (ix, iy)
    for iy in np.arange(height):
        for ix in np.arange(width):
            # start iteration at x0 in [-2, 1] and y0 in [-1, 1]
            x0 = ix * 3.0 / width - 2.0
            y0 = iy * 2.0 / height - 1.0

            x = 0.0
            y = 0.0
            # perform Mandelbrot set iterations
            for iteration in range(max_iterations):
                x_new = x * x - y * y + x0
                y = 2 * x * y + y0
                x = x_new

                # if escaped
                if x * x + y * y > 4.0:
                    # color using pretty linear gradient
                    color = 1.0 - 0.01 * (iteration - np.log2(np.log2(x * x + y * y)))
                    break
            else:
                # failed, set color to black
                color = 0.0

            result[iy, ix] = color

    return result


mandelbrot = make_mandelbrot(3000, 2000, 1055)

# convert from float in [0, 1] to to uint8 in [0, 255] for PIL
mandelbrot = np.clip(mandelbrot * 255, 0, 255).astype(np.uint8)
mandelbrot = Image.fromarray(mandelbrot)
mandelbrot.save("mandelbrot.png")
mandelbrot.show()
