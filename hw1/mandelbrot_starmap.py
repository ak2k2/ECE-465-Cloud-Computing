import time
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def mandelbrot_row(y, w, h, max_iter):
    """
    Calculate one row of the Mandelbrot set with size w * h
    """
    row_data = np.zeros((w, 3), dtype=np.uint8)
    for x in range(w):
        zx, zy = x * (3.5 / w) - 2.5, y * (2.0 / h) - 1.0
        c = zx + zy * 1j
        z = c
        for i in range(max_iter):
            if abs(z) > 2.0:
                color = plt.cm.get_cmap("hot")(
                    i / max_iter
                )  # Get color based on iteration
                row_data[x] = tuple(
                    int(c * 255) for c in color[:3]
                )  # Assign RGB values from color
                break
            z = z * z + c
    return row_data


def generate_mandelbrot_single(w, h, max_iter):
    """
    Call mandelbrot_row for each row of the image
    """
    image_data = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        row_data = mandelbrot_row(y, w, h, max_iter)
        image_data[y] = row_data
    return image_data


def generate_mandelbrot_starmap(w, h, max_iter):
    """
    Generate Mandelbrot image using process pool
    """
    image_data = np.zeros((h, w, 3), dtype=np.uint8)
    with Pool(num_cores=cpu_count()) as pool:
        rows_data = pool.starmap(
            mandelbrot_row, [(y, w, h, max_iter) for y in range(h)]
        )
    for y, row_data in enumerate(rows_data):
        image_data[y] = row_data
    return image_data


# Calculate Mandelbrot for a grid section
def mandelbrot_grid(start_row, end_row, start_col, end_col, w, h, max_iter):
    grid_data = np.zeros((end_row - start_row, end_col - start_col, 3), dtype=np.uint8)
    for x in range(start_col, end_col):
        for y in range(start_row, end_row):
            zx, zy = x * (3.5 / w) - 2.5, y * (2.0 / h) - 1.0
            c = zx + zy * 1j
            z = c
            for i in range(max_iter):
                if abs(z) > 2.0:
                    r = int(255 * i / max_iter)
                    grid_data[y - start_row][x - start_col] = (r, 0, 0)
                    break
                z = z * z + c
    return start_row, end_row, start_col, end_col, grid_data


# Generate Mandelbrot image using multiprocessing with grids
def generate_mandelbrot_grid(w, h, max_iter, grid_size):
    image_data = np.zeros((h, w, 3), dtype=np.uint8)
    tasks = []

    rows_per_grid = h // grid_size
    cols_per_grid = w // grid_size

    for i in range(grid_size):
        for j in range(grid_size):
            start_row, end_row = i * rows_per_grid, (i + 1) * rows_per_grid
            start_col, end_col = j * cols_per_grid, (j + 1) * cols_per_grid
            tasks.append((start_row, end_row, start_col, end_col, w, h, max_iter))

    with Pool() as pool:
        grids_data = pool.starmap(mandelbrot_grid, tasks)

    for start_row, end_row, start_col, end_col, grid_data in grids_data:
        image_data[start_row:end_row, start_col:end_col] = grid_data

    return image_data


# Main execution
if __name__ == "__main__":
    w, h = 1000, 800  # Image size
    max_iter = 100  # Max iterations
    num_cores = cpu_count()  # Number of cores to use

    # Without multiprocessing
    start_time = time.time()
    image_data_single = generate_mandelbrot_single(w, h, max_iter)
    print(f"Time taken without multiprocessing: {time.time() - start_time} seconds")

    # With multiprocessing
    start_time = time.time()
    image_data_mp = generate_mandelbrot_starmap(w, h, max_iter)
    print(f"Time taken with multiprocessing: {time.time() - start_time} seconds")

    # Calculate grid size so that the number of grids is at least equal to num_cores
    grid_size = int((w * h) ** 0.5 // (num_cores) ** 0.5)
    rows_per_grid = h // grid_size
    cols_per_grid = w // grid_size
    total_grids = (h // rows_per_grid) * (w // cols_per_grid)

    print(
        f"Grid size: {grid_size}, Total grids: {total_grids}, Number of Cores: {num_cores}"
    )
    # With multiprocessing and grids
    start_time = time.time()
    image_data_grid = generate_mandelbrot_grid(w, h, max_iter, grid_size)
    print(
        f"Time taken with grid-based multiprocessing: {time.time() - start_time} seconds"
    )

    img = Image.fromarray(image_data_grid, "RGB")
    img.save("mandelbrot_max_cpu.png")
