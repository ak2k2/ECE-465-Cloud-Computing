import cv2
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor


def equalize_channel(channel):
    # Your equalization logic here, for example:
    hist, _ = np.histogram(channel.flatten(), 256, [0, 256])
    cdf = hist.cumsum()
    cdf = np.ma.masked_equal(cdf, 0)
    cdf = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    return cdf.filled(0)[channel].astype("uint8")


def process_all_channels_sequential(image):
    channels = cv2.split(image)
    equalized_channels = [equalize_channel(ch) for ch in channels]
    return cv2.merge(equalized_channels)


def process_all_channels_parallel(image):
    channels = cv2.split(image)
    with ProcessPoolExecutor() as executor:
        equalized_channels = list(executor.map(equalize_channel, channels))
    return cv2.merge(equalized_channels)


if __name__ == "__main__":
    # Create a synthetic multi-channel image
    h, w = 100, 100
    num_channels = 3  # or however many you want
    image = np.random.randint(0, 256, (h, w, num_channels), dtype=np.uint8)

    # Time the sequential approach
    start = time.time()
    equalized_image_sequential = process_all_channels_sequential(image)
    end = time.time()
    print(f"Time taken for sequential processing: {end - start} seconds")
    cv2.imshow("Equalized (Sequential)", equalized_image_sequential)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Time the parallel approach
    start = time.time()
    equalized_image_parallel = process_all_channels_parallel(image)
    end = time.time()
    print(f"Time taken for parallel processing: {end - start} seconds")
    cv2.imshow("Equalized (Parallel)", equalized_image_sequential)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
