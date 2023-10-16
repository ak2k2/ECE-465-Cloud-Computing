"""
Extremely fast Mandelbrot set computation using numpy and numba (credit to Jean-François Puget: https://gist.github.com/jfpuget/60e07a82dece69b011bb)

"""

from __future__ import absolute_import, print_function

import base64
import io
import platform as plat
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

    is_mac = plat.system() == "Darwin"  # "Darwin" signifies a MacOS system
    if is_mac:
        device = devices[1]
    else:
        device = devices[0]

    print(device.name)

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


@ray.remote
def generate_frame(coords: tuple, width: int, height: int, maxiter: int):
    # Calculate Mandelbrot set based on provided coordinates
    xmin, xmax, ymin, ymax = coords
    x, y, mandelbrot_image = mandelbrot_set3(
        xmin, xmax, ymin, ymax, width, height, maxiter
    )

    # PowerNorm the iteration counts for coloring
    norm = mcolors.PowerNorm(0.2)

    # Create a plot for the current frame
    plt.figure(figsize=(width / 100, height / 100), dpi=150)  # set DPI

    plt.axis("off")
    plt.imshow(mandelbrot_image, cmap="nipy_spectral", norm=norm)

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
    plt.close()

    # Convert the bytes buffer value to a base64 string to be easily transferred
    base64_bytes = base64.b64encode(buffer.getvalue())
    base64_string = base64_bytes.decode("utf8")

    return base64_string
