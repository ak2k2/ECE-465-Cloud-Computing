import time
import os
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt

def poolme(val: int) -> int:
    time.sleep(np.random.random() / 10) # sleep for random float between 0 and 0.1
    res = val ** 2
    return res

def time_proc_pool(arr: list, num_procs: int) -> float:
    st = time.time()
    print(f"Running with {num_procs} processes...")
    with Pool(num_procs) as pool:
        pool.map(poolme, arr)
    et = time.time()
    return et - st

def time_thread_pool(arr: list, num_threads: int) -> float:
    st = time.time()
    print(f"Running with {num_threads} threads...")
    with ThreadPoolExecutor(num_threads) as pool:
        pool.map(poolme, arr)
    et = time.time()
    return et - st


if __name__ == "__main__":
    arr = [np.random.random() for _ in range(100)]
    res = []
    X = range(1,200)
    res = [time_thread_pool(arr, num_procs) for num_procs in X]
    plt.plot(res)
    plt.show()

