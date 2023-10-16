"""
Extremely fast Mandelbrot set computation using numpy and numba (credit to Jean-François Puget: https://gist.github.com/jfpuget/60e07a82dece69b011bb)

"""

from __future__ import absolute_import, print_function

import base64
import io
import time as t
from io import BytesIO

import matplotlib.colors as mcolors
import numpy as np
import pyopencl as cl
import ray
from matplotlib import pyplot as plt
from PIL import Image


def mandelbrot_opencl(q, maxiter):
    platforms = cl.get_platforms()
    if not platforms:
        raise ValueError("No OpenCL platforms found.")
    platform = platforms[0]

    devices = platform.get_devices()
    if not devices:
        raise ValueError("No OpenCL devices found on the selected platform.")
    device = devices[0]

    # Create a context with the selected device
    ctx = cl.Context([device])
    queue = cl.CommandQueue(ctx)
    output = np.empty(q.shape[0], dtype=np.uint16)

    prg = cl.Program(
        ctx,
        """
    #pragma OPENCL EXTENSION cl_khr_byte_addressable_store : enable
    __kernel void mandelbrot(__global float2 *q,
                     __global ushort *output, ushort const maxiter)
    {
        int gid = get_global_id(0);
        float nreal, real = 0;
        float imag = 0;
        output[gid] = 0;
        for(int curiter = 0; curiter < maxiter; curiter++) {
            nreal = real*real - imag*imag + q[gid].x;
            imag = 2* real*imag + q[gid].y;
            real = nreal;
            if (real*real + imag*imag > 4.0f){
                 output[gid] = curiter;
                 break;
            }
        }
    }
    """,
    ).build()

    mf = cl.mem_flags
    q_opencl = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q)
    output_opencl = cl.Buffer(ctx, mf.WRITE_ONLY, output.nbytes)

    prg.mandelbrot(
        queue, output.shape, None, q_opencl, output_opencl, np.uint16(maxiter)
    )

    cl.enqueue_copy(queue, output, output_opencl).wait()

    return output


def mandelbrot_set3(xmin, xmax, ymin, ymax, width, height, maxiter):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float32)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float32)
    c = r1 + r2[:, None] * 1j
    c = np.ravel(c)
    n3 = mandelbrot_opencl(c, maxiter)
    n3 = n3.reshape((width, height))
    return (r1, r2, n3.T)


def save_result(res):
    # Extract the iteration counts from the result
    iteration_counts = res[2]

    # Normalize the iteration counts for coloring
    norm = mcolors.PowerNorm(0.3)  # Using a PowerNorm for non-linear scaling

    # Create a new figure and set the aspect ratio
    plt.figure(figsize=(20, 20))
    plt.axis("off")  # Turn off the axis
    plt.imshow(iteration_counts, cmap="nipy_spectral", norm=norm)
    plt.savefig("enhanced_mandelbrot.png", bbox_inches="tight", pad_inches=0, dpi=200)


# bounds = (-1.25066, -1.25061, 0.02012, 0.02017)
# st = t.time()
# res = mandelbrot_set3(*bounds, 10000, 10000, 1000000)
# print("Duration: ", t.time() - st)
# save_result(res)


@ray.remote
def generate_frame(coords: tuple, width: int, height: int, maxiter: int):
    # Extract coordinates
    xmin, xmax, ymin, ymax = coords

    # Calculate Mandelbrot set based on provided coordinates
    x, y, mandelbrot_image = mandelbrot_set3(
        xmin, xmax, ymin, ymax, width, height, maxiter
    )

    # Normalize the iteration counts for coloring
    norm = mcolors.PowerNorm(0.3)  # Using a PowerNorm for non-linear scaling

    # Create a plot for the current frame
    plt.figure(
        figsize=(width / 100, height / 100), dpi=100
    )  # Assuming the DPI you'd like to use
    plt.axis("off")  # Turn off the axis
    plt.imshow(mandelbrot_image, cmap="nipy_spectral", norm=norm)

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
    plt.close()

    # Convert the bytes buffer value to a base64 string to be easily transferred
    base64_bytes = base64.b64encode(buffer.getvalue())
    base64_string = base64_bytes.decode("utf8")

    return base64_string


# ray.init(
#     address="auto"
# )  # connect to the running Ray cluster; replace 'auto' with the server address if necessary

# # Define bounds and parameters
# bounds = (-2.0, 1.0, -1.0, 1.0)  # default Mandelbrot bounds
# width = 1000  # image width
# height = 1000  # image height
# maxiter = 1000  # max iterations for the Mandelbrot set

# # Asynchronously start a task to generate a Mandelbrot frame
# future = generate_frame.remote(bounds, width, height, maxiter)

# # Wait for the task to complete and get the result (base64 string)
# base64_string = ray.get(future)

# # Convert the base64 string back to an image
# image_bytes = base64.b64decode(base64_string)
# image_buf = BytesIO(image_bytes)
# image = Image.open(image_buf)

# # Display the image
# plt.figure(figsize=(6, 6))
# plt.imshow(image, cmap="nipy_spectral")
# plt.axis("off")  # Turn off the axis numbers and ticks
# plt.show()
