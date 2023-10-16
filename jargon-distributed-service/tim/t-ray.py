import time as t
from multiprocessing import Pool

# Define the function to compute the Fibonacci sequence
def fib(N):
    if N <= 2:
        return 1
    a, b = 0, 1
    for i in range(2, N):
        a, b = b, a + b
    return b

def main():
    # Create a pool of worker processes
    num_processes = 8  # This can be set to any number of your choice, commonly it's set to the number of cores in your CPU
    with Pool(processes=num_processes) as pool:
        st = t.time()

        # Map the range of numbers to the pool of workers
        results = pool.map(fib, range(10000))

        print(f"pool took {t.time() - st} seconds")

# This is the standard boilerplate that calls the main() function
if __name__ == '__main__':
    main()
