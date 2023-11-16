import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time


def calculate_cdf(tile):
    hist, _ = np.histogram(tile.flatten(), 256, [0, 256])
    cdf = hist.cumsum()
    cdf = np.ma.masked_equal(cdf, 0)
    cdf = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    return cdf.filled(0).astype("uint8")


def whole_image_equalization(image):
    cdf = calculate_cdf(image)
    return cdf[image]


def grid_equalization(image, grid_size):
    h, w = image.shape
    tile_h, tile_w = h // grid_size, w // grid_size

    tiles = []

    for i in range(0, h, tile_h):
        for j in range(0, w, tile_w):
            tile = image[i : i + tile_h, j : j + tile_w]
            tiles.append(tile)

    cdf_list = []

    with ThreadPoolExecutor(max_workers=1000) as executor:
        cdf_list = list(executor.map(calculate_cdf, tiles))

    avg_cdf = np.mean(cdf_list, axis=0).astype("uint8")
    img_equalized = avg_cdf[image]

    return img_equalized


if __name__ == "__main__":
    img = cv2.imread("overexposed.png", 0)

    start_time = time.time()
    grid_size = 10  # Adjust the grid size as needed
    equalized_img_grid = grid_equalization(img, grid_size)
    grid_time = time.time() - start_time
    print(f"Time taken for grid-based equalization: {grid_time:.4f} seconds")

    start_time = time.time()
    equalized_img_whole = whole_image_equalization(img)
    whole_time = time.time() - start_time
    print(f"Time taken for whole-image equalization: {whole_time:.4f} seconds")

    cv2.imshow("Original", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("Equalized (Grid-Based)", equalized_img_grid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("Equalized (Whole Image)", equalized_img_whole)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
