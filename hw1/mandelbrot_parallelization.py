import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

NUM_CORES = cpu_count()
np.random.seed(0)


def mandelbrot_row(y, w, h, max_iter):
    """
    A mandelbrot row is computed by iterating over each pixel in the row
    """
    thread_name = threading.current_thread().name
    pid = os.getpid()
    print(f"Thread: {thread_name}, PID: {pid} - Processing row {y}")

    row_data = np.zeros((w, 3), dtype=np.uint8)
    for x in range(w):
        zx, zy = x * (3.5 / w) - 2.5, y * (2.0 / h) - 1.0
        c = zx + zy * 1j
        z = c
        for i in range(max_iter):
            if abs(z) > 2.0:
                color = plt.cm.get_cmap("hot")(i / max_iter)
                row_data[x] = tuple(int(c * 255) for c in color[:3])
                break
            z = z * z + c
    return row_data


def generate_mandelbrot_sequential(w, h, max_iter):
    """
    Sequentially generate Mandelbrot image by calling mandelbrot_row num_rows times
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
    with Pool(processes=NUM_CORES) as pool:
        rows_data = pool.starmap(
            mandelbrot_row, [(y, w, h, max_iter) for y in range(h)]
        )
    for y, row_data in enumerate(rows_data):
        image_data[y] = row_data
    return image_data


def process_grid(start_row, end_row, start_col, end_col, w, h, max_iter):
    """
    Compute mandelbrot set using thread pool for a given grid
    """
    pid = os.getpid()
    print(
        f"PID: {pid} - Processing grid from row {start_row} to {end_row}, col {start_col} to {end_col}"
    )

    grid_data = np.zeros((end_row - start_row, end_col - start_col, 3), dtype=np.uint8)
    with ThreadPoolExecutor(max_workers=32) as executor:
        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                zx, zy = x * (3.5 / w) - 2.5, y * (2.0 / h) - 1.0
                c = zx + zy * 1j
                z = c
                for i in range(max_iter):
                    if abs(z) > 2.0:
                        color = plt.cm.get_cmap("hot")(i / max_iter)
                        grid_data[y - start_row][x - start_col] = tuple(
                            int(c * 255) for c in color[:3]
                        )
                        break
                    z = z * z + c
    return start_row, end_row, start_col, end_col, grid_data


def generate_mandelbrot_grid(w, h, max_iter):
    """
    Distribute the image into 8 grids and compute each grid in 'true' parallel using starmap
    """
    image_data = np.zeros((h, w, 3), dtype=np.uint8)
    tasks = []

    # Divide the image into 8 grids
    grid_size = 8
    rows_per_grid = h // grid_size
    cols_per_grid = w // grid_size

    for i in range(grid_size):
        for j in range(grid_size):
            start_row, end_row = i * rows_per_grid, (i + 1) * rows_per_grid
            start_col, end_col = j * cols_per_grid, (j + 1) * cols_per_grid
            tasks.append((start_row, end_row, start_col, end_col, w, h, max_iter))

    # 8 cores 1:1 mapping
    with Pool(processes=NUM_CORES) as pool:
        grids_data = pool.starmap(process_grid, tasks)

    for start_row, end_row, start_col, end_col, grid_data in grids_data:
        image_data[start_row:end_row, start_col:end_col] = grid_data

    return image_data


def assert_images_equal(img1, img2, img3):
    """
    Assert that the 3 images are equal
    """
    if np.array_equal(img1, img2) and np.array_equal(img2, img3):
        return "Images are equal"
    else:
        return "Images are not equal"


# Main execution
if __name__ == "__main__":
    w, h = 100, 100  # Image size
    max_iter = 20  # Max iterations
    num_cores = cpu_count()  # Number of cores to use

    # Sequential
    start_time = time.time()
    image_data_single = generate_mandelbrot_sequential(w, h, max_iter)
    sequential_elapsed_time = time.time() - start_time
    print("\n", "=" * 80)

    # Row/Col based multiprocessing
    start_time = time.time()
    image_data_mp = generate_mandelbrot_starmap(w, h, max_iter)
    row_col_elapsed_time = time.time() - start_time
    print("\n", "=" * 80)

    # Grid based multiprocessing
    start_time = time.time()
    image_data_grid = generate_mandelbrot_grid(w, h, max_iter)
    grid_elapsed_time = time.time() - start_time
    print("\n", "=" * 80)

    print("\n\n")
    print(f"Time taken without multiprocessing: {sequential_elapsed_time} seconds")
    print(f"Time taken with row based parallelism: {row_col_elapsed_time} seconds")
    print(f"Time taken with grid-based multiprocessing: {grid_elapsed_time} seconds")

    print(assert_images_equal(image_data_single, image_data_mp, image_data_grid))

    img_single = Image.fromarray(image_data_single, "RGB")
    img_single.save("artifacts/mandelbrot_single_cpu.png")

    img_mp = Image.fromarray(image_data_mp, "RGB")
    img_mp.save("artifacts/mandelbrot_mp_cpu.png")

    img_grid = Image.fromarray(image_data_grid, "RGB")
    img_grid.save("artifacts/mandelbrot_grid_cpu.png")
