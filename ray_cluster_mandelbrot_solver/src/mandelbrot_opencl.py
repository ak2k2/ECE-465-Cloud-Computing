from __future__ import absolute_import, print_function

import io
import platform as plat

import matplotlib.colors as mcolors
import numpy as np
import pyopencl as cl
import ray
from matplotlib import cm
from PIL import Image

# # GL enabled mandelbrot set computation from Jean-François Puget: https://gist.github.com/jfpuget/60e07a82dece69b011bb)
# # SWITCH TO THIS?: https://github.com/jlesuffleur/gpu_mandelbrot/blob/master/mandelbrot.py
# PYCL_SCRIPT = """
#     #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable
#     __kernel void mandelbrot(__global float2 *q,
#                      __global ushort *output, ushort const maxiter)
#     {
#         int gid = get_global_id(0);
#         float nreal, real = 0;
#         float imag = 0;
#         output[gid] = 0;
#         for(int curiter = 0; curiter < maxiter; curiter++) {
#             nreal = real*real - imag*imag + q[gid].x;
#             imag = 2* real*imag + q[gid].y;
#             real = nreal;
#             if (real*real + imag*imag > 4.0f){
#                  output[gid] = curiter;
#                  break;
#             }
#         }
#     }
#     """


# def mandelbrot_opencl(q, maxiter):
#     platforms = cl.get_platforms()
#     if not platforms:
#         raise ValueError("No OpenCL platforms found.")
#     platform = platforms[0]

#     devices = platform.get_devices()
#     if not devices:
#         raise ValueError("No OpenCL devices found on the selected platform.")

#     is_mac = plat.system() == "Darwin"  # "Darwin" for a MacOS system
#     if is_mac:
#         # Chose Intel(R) Iris(TM) Plus Graphics
#         device = devices[
#             1
#         ]  # Because I have a Macbook Pro with a opencl enabled CPU and GPU
#     else:
#         device = devices[0]  # BeelinkPC only has a RYZEN

#     print("Using OpenCL device: ", device.name)
#     # Create a context with the selected device
#     ctx = cl.Context([device])
#     # ctx = cl.Context([cl.get_platforms()[0].get_devices()[0]])
#     queue = cl.CommandQueue(ctx)
#     output = np.empty(q.shape[0], dtype=np.uint16)

#     prg = cl.Program(
#         ctx,
#         PYCL_SCRIPT,
#     ).build()

#     mf = cl.mem_flags
#     q_opencl = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q)
#     output_opencl = cl.Buffer(ctx, mf.WRITE_ONLY, output.nbytes)

#     prg.mandelbrot(
#         queue, output.shape, None, q_opencl, output_opencl, np.uint16(maxiter)
#     )

#     cl.enqueue_copy(queue, output, output_opencl).wait()

#     return output


# def mandelbrot_set3(xmin, xmax, ymin, ymax, width, height, maxiter):
#     r1 = np.linspace(xmin, xmax, width, dtype=np.float32)
#     r2 = np.linspace(ymin, ymax, height, dtype=np.float32)
#     c = r1 + r2[:, None] * 1j
#     c = np.ravel(c)
#     n3 = mandelbrot_opencl(c, maxiter)
#     n3 = n3.reshape((width, height))
#     return (r1, r2, n3.T)


import numpy as np
from numba import (
    complex64,
    float32,
    float64,
    guvectorize,
    int32,
    jit,
    vectorize,
    complex128,
)


@jit(int32(complex128, int32))
def mandelbrot_j(c, maxiter):
    nreal = 0.0
    real = 0.0
    imag = 0.0
    for n in range(maxiter):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        if real * real + imag * imag > 4.0:
            return n
    return 0


@guvectorize([(complex128[:], int32[:], int32[:])], "(n),()->(n)", target="parallel")
def mandelbrot_numpy(c, maxit, output):
    maxiter = maxit[0]
    for i in range(c.shape[0]):
        output[i] = mandelbrot_j(c[i], maxiter)


def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float64)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float64)
    c = r1 + r2[:, None] * 1j
    n3 = mandelbrot_numpy(c, maxiter)
    return (r1, r2, n3.T)


@ray.remote
def compute_mandelbrot_frame(coords: tuple, width: int, height: int, maxiter: int):
    # Calculate Mandelbrot set based on provided coordinates
    xmin, xmax, ymin, ymax = coords
    mandelbrot_data = mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter)
    return mandelbrot_data, width, height


@ray.remote
def process_frame(mandelbrot_image: tuple, width: int, height: int):
    # Convert the image data to a numpy array
    mandelbrot_image = np.array(mandelbrot_image, dtype=np.uint16)

    # Rotate the image 90 degrees counterclockwise
    mandelbrot_image = np.rot90(mandelbrot_image)

    # Apply a more sophisticated colormap with normalization
    norm = mcolors.PowerNorm(0.3)
    cmap = cm.get_cmap("twilight_shifted")  # Using a 'twilight_shifted' colormap

    # Apply the colormap to the image
    normalized_image = norm(mandelbrot_image)
    colored_image = cmap(normalized_image)

    # Convert to RGBA values and scale to [0, 255]
    colored_image = (colored_image[:, :, :3] * 255).astype(np.uint8)

    # Convert to an image for encoding
    img = Image.fromarray(colored_image)

    # Encode the image as PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    image_data = buffer.read()

    return image_data
