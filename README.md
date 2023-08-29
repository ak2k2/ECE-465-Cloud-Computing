# ECE-465-Cloud-Computing: 
## Prof. Marano

---

### **📚 Textbook**: [Distributed_Systems_4-230829.pdf](https://github.com/ak2k2/ECE-465-Cloud-Computing/files/12460815/Distributed_Systems_4-230829.pdf)

---

## **📅 Week 1: Concurrency & Thread/Process Pools for IO/CPU Bound Processes**

---

## **🔍 Web Scraping with Python: Sequential vs. Parallel Execution**

---

### **📄 File: `pooled_url_download.py`**

📍 **Objective**: Fetches HTML content from a list of URLs (`urls_to_scrape_.csv`) and computes their SHA256 hash. Three regimes are timed for performance analysis.

---

### **👨‍💻 Execution Modes**

#### **1️⃣ Sequential Execution**

- **🔗 Mode**: All links fetched and processed one-by-one.
- **🧵 Thread**: `MainThread`
- **🆔 PID**: `1382`
- **⏱ Time**: 12.03 seconds

---

#### **2️⃣ Parallel Execution with Thread Pool**

- **🔗 Mode**: Links fetched by different threads but within the same process.
- **🧵 Threads**: `ThreadPoolExecutor-0_0`, `ThreadPoolExecutor-0_1`, ...
- **🆔 PID**: `1382`
- **⏱ Time**: 3.11 seconds

---

#### **3️⃣ Parallel Execution with Process Pool**

- **🔗 Mode**: Links fetched by different processes, bypassing Python's GIL. True parallel execution. 
- **🆔 PIDs**: `1397`, `1398`, `1401`, `1402`
- **⏱ Time**: 4.77 seconds

<img width="1007" alt="ppool-htop" src="https://github.com/ak2k2/ECE-465-Cloud-Computing/assets/103453421/cb0fce2a-6d38-4aa2-94f6-a86de7b0d0ac">

---

## **📊 Findings**

1. **🚀 Max Speedup with Thread Pool**
   - **🔍 Insight**: Thread Pool is **3.87x faster** than sequential execution!

2. **🐌 Significant Overhead in Process Pool**
   - **🔍 Insight**: Process Pool is slower due to the overhead of new processes.

---
