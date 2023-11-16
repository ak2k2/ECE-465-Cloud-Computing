import cv2
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
import time


def process_tile(tile):
    y, cr, cb = cv2.split(tile)
    y_eq = cv2.equalizeHist(y)
    return cv2.merge([y_eq, cr, cb])


def grid_equalization(image, grid_size):
    h, w, _ = image.shape
    tile_h, tile_w = h // grid_size, w // grid_size

    # YCrCb color space
    image_ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

    tiles = []
    coords = []

    # Split image into tiles
    for i in range(0, h, tile_h):
        for j in range(0, w, tile_w):
            tile = image_ycrcb[i : i + tile_h, j : j + tile_w]
            tiles.append(tile)
            coords.append((i, j))

    # Process tiles in parallel
    start_time_parallel = time.time()
    with ThreadPoolExecutor() as executor:
        processed_tiles = list(executor.map(process_tile, tiles))

    end_time_parallel = time.time()
    print(f"Time taken in parallel: {end_time_parallel - start_time_parallel} seconds")

    # Concatenate processed tiles back into the image
    for (i, j), tile in zip(coords, processed_tiles):
        image_ycrcb[i : i + tile_h, j : j + tile_w] = tile

    # BGR color space
    return cv2.cvtColor(image_ycrcb, cv2.COLOR_YCrCb2BGR)


def full_equalization(image):
    start_time_seq = time.time()
    image_ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(image_ycrcb)
    y_eq = cv2.equalizeHist(y)
    equalized_img = cv2.merge([y_eq, cr, cb])
    equalized_img = cv2.cvtColor(equalized_img, cv2.COLOR_YCrCb2BGR)
    end_time_seq = time.time()
    print(f"Time taken sequentially: {end_time_seq - start_time_seq} seconds")
    return equalized_img


if __name__ == "__main__":
    img = cv2.imread("overexposed.png")

    # Grid-based histogram equalization
    grid_size = 8
    equalized_img = grid_equalization(img, grid_size)

    # Apply full image equalization and display the time
    equalized_img_full = full_equalization(img)

    # Show original and equalized images
    cv2.imshow("Original", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("Grid Equalized", equalized_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("Fully Equalized", equalized_img_full)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
