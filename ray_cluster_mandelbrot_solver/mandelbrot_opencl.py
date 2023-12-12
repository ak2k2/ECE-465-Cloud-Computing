from __future__ import absolute_import, print_function

import io
import platform as plat

import matplotlib.colors as mcolors
import numpy as np
import pyopencl as cl
import ray
from matplotlib import pyplot as plt

# GL enabled mandelbrot set computation from Jean-François Puget: https://gist.github.com/jfpuget/60e07a82dece69b011bb)
PYCL_SCRIPT = """
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
    """


def mandelbrot_opencl(q, maxiter):
    """
    Fast Mandelbrot set computation using numpy and numba (credit to Jean-François Puget: https://gist.github.com/jfpuget/60e07a82dece69b011bb)
    """

    platforms = cl.get_platforms()
    if not platforms:
        raise ValueError("No OpenCL platforms found.")
    platform = platforms[0]

    devices = platform.get_devices()
    if not devices:
        raise ValueError("No OpenCL devices found on the selected platform.")

    is_mac = plat.system() == "Darwin"  # "Darwin" for a MacOS system
    if is_mac:
        # Chose Intel(R) Iris(TM) Plus Graphics
        device = devices[
            1
        ]  # Because I have a Macbook Pro with a opencl enabled CPU and GPU
    else:
        device = devices[0]  # My ubuntu server only has a RYZEN

    print("Using OpenCL device: ", device.name)
    # Create a context with the selected device
    ctx = cl.Context([device])
    queue = cl.CommandQueue(ctx)
    output = np.empty(q.shape[0], dtype=np.uint16)

    prg = cl.Program(
        ctx,
        PYCL_SCRIPT,
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

    # Rotate the image 90 degrees counterclockwise
    mandelbrot_image = np.rot90(mandelbrot_image)

    # flip the image top to bottom
    mandelbrot_image = np.flipud(mandelbrot_image)

    # Apply a more sophisticated colormap with normalization
    norm = mcolors.PowerNorm(0.3)
    cmap = plt.get_cmap(
        "twilight_shifted"
    )  # Using a 'twilight_shifted' colormap for a vibrant look

    # Create a high-resolution plot for the current frame
    plt.figure(figsize=(width / 100, height / 100), dpi=300)

    plt.axis("off")
    plt.imshow(mandelbrot_image, cmap=cmap, norm=norm, interpolation="bilinear")

    # Apply post-processing for enhanced visuals
    # (Optional techniques like smoothing, sharpening, etc., can be added here)

    # Convert the image to a byte array for transmission
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
    plt.close()
    buffer.seek(0)
    image_data = buffer.read()

    return image_data
