# ECE-465-Cloud-Computing - Prof. Marano

- Textbook: [Distributed_Systems_4-230829.pdf](https://github.com/ak2k2/ECE-465-Cloud-Computing/files/12460815/Distributed_Systems_4-230829.pdf)
  
## Week 1 (concurrency & thread/process pools, for IO/CPU bound processes)

### Web Scraping with Python: Sequential vs. Parallel Execution

#### Overview

```pooled_url_download.py``` fetches html content from the list of URLs (```urls_to_scrape_.csv```) and computes their SHA256 hash. It times the three following regimes.

#### Sequential Execution
All links are fetched one at a time by the same thread (`MainThread`) within the same Python process (`PID: 1382`).

- **Time taken to process links: 12.03 seconds**

#### Parallel Execution with Thread Pool
Each link is fetched by different threads (e.g., `ThreadPoolExecutor-0_0`, `ThreadPoolExecutor-0_1`...) but within the same Python process (`PID: 1382`).

- **Time taken with Thread Pool: 3.11 seconds**

#### Parallel Execution using Process Pool
Each link is fetched by a different process (`PID: 1397, 1398, 1401, 1402`), bypassing Python's Global Interpreter Lock (GIL) for true parallel execution.

- **Time taken with Process Pool: 4.77 seconds**

## Findings

1. **Max Speedup with Thread Pool**: Using a thread pool to fetch all the URLs is **3.87x** faster!

2. **Significant Overhead in Process Pool**: Though the process pool allows for true parallel execution, it is slower than the threadpool in this case due to the overhead of spinning up new processes.
