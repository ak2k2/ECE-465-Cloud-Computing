# Overview
This repository contains scripts to set up a Ray cluster distribute computation necessary to generate multiple frames of the Mandelbrot set and animate an mp4 video of a detailed fractal zoom sequence.

A client submits a JSON payload containing a point on the (real,imaginary) axis, along with parameters to control the granularity and number of frames in a sequence.

The spawner_ray_* shell scripts automate the process of initializing both a head (master) node and worker nodes, and launching a ray dashboard to monitor the cluster's status.

The core mandelbrot set computation uses PyOpenCL to carry out independent floating point operations using supported CPU and GPU cores/processing units.

The master node in a cluster stores sequences in the DB directory, and serves clients their mp4 animations via a configurable multithreaded socket.

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

The client submits a request directly to the distributed computing cluster via the head node, without necessarily requiring access to the source code in ray_head.py.

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
