# Overview
This repository contains scripts to set up a Ray cluster, intended for distributed computation tasks necessary to generate frames of the Mandelbrot set, ultimately creating detailed animated zoom sequences. The setup encompasses instructions for initializing both the head (master) and worker nodes, and it offers utilities to verify the cluster's active status. The system leverages multiple compute nodes (both CPU and GPU) to parallelize the tasks, managing futures/promises from the head.

---
The **client.py** script facilitates access to the Mandelbrot service by sending a straightforward JSON payload to the socket initiated by **ray_head.py**.

```json
{   
    "point": "-1.338238635,-0.057237059",
    "num_frames": 50,
    "frame_width": 1000,
    "frame_height": 1000,
    "maxiter": 1000,
    "fps": 20,
    "start_delta": 2.5,
    "end_delta": 0.0001
}
```
---

Interestingly, the client itself can initiate a raw server through a shell script and integrate into the distributed computing cluster, all without requiring understanding of the source code in ray_head.py.

---

## Execution Steps

1. On the head machine (master):
    - Activate virtual environment: `$ source rayenv/bin/activate`
    - Launch the head node: `$ ./spawn_ray_head.sh`

2. On worker nodes (e.g., ubuntu servers):
    - Activate virtual environment: `$ conda activate py3115`
    - Start the worker node: `$ ./spawn_ray_server.sh`

3. Confirm the cluster's operational status:
    - Check Ray's status: `$ ray status`
    - Visit the dashboard: [http://0.0.0.0:8265/#/cluster](http://0.0.0.0:8265/#/cluster)

4. Execute the head script to start a socket for processing payloads and delivering mp4 animations:
    - `$ python ray_head.py`

6. Use the client script with a provided payload. The socket employs multipart file upload to deliver an h.264 encoded (mp4) zoom sequence:
    - `$ python client.py`
