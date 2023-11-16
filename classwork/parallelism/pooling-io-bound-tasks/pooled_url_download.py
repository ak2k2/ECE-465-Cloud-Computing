import requests
import time
import csv
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading

import hashlib

import logging

logging.basicConfig(level=logging.INFO)


def fetch_url_print_sha(url):
    current_thread = threading.current_thread().name
    logging.info(f"{current_thread} - Fetching {url}")
    response = requests.get(url).content
    sha256_hash = hashlib.sha256(response)
    current_process = os.getpid()
    logging.info(f"{current_thread} ------- PID: {current_process} ----- Link: {url}. HASH: {sha256_hash.hexdigest()[:10]}...")
    return sha256_hash


def fetch_urls_parallel_threadpool(urls):
    with ThreadPoolExecutor() as executor:
        executor.map(fetch_url_print_sha, urls)


def fetch_urls_parallel_procpool(urls):
    with ProcessPoolExecutor() as executor:
        executor.map(fetch_url_print_sha, urls)


def fetch_urls_sequential(urls):
    for url in urls:
        fetch_url_print_sha(url)


def read_csv(file_name):
    urls = []
    with open(file_name, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            urls.extend(row)
    return urls


if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urls = read_csv(os.path.join("urls_to_scrape.csv"))  # big list of urls

    start_time = time.time()
    fetch_urls_sequential(urls)  # sequential single threaded single process
    print("\n")
    print("-" * 100)
    print(f"Time taken without parallelization: {time.time() - start_time} seconds")
    print("-" * 100)
    print("\n")

    start_time = time.time()
    fetch_urls_parallel_threadpool(urls)  # parallel multi threaded single process
    print("\n")
    print("-" * 100)
    print(f"Time taken with Thread Pool: {time.time() - start_time} seconds")
    print("-" * 100)
    print("\n")

    start_time = time.time()
    fetch_urls_parallel_procpool(urls)  # parallel multi threaded multi process
    print("\n")
    print("-" * 100)
    print(f"Time taken with Process Pool: {time.time() - start_time} seconds")
    print("-" * 100)
    print("\n")
