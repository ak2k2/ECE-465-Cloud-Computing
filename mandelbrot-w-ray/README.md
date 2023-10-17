# Gist
Scripts for establishing a Ray cluster, designed to distribute the workload needed to generate various frames of the Mandelbrot set to produce intricate animated zoom sequences. It includes setup instructions for both head (master) and worker nodes, with tools to confirm the operational status of the cluster. Various compute nodes (CPU and GPU) can be assembled and used to complete the job in parallel. futures/promises can be managed from head. 

Using client.py, the mandelbrot service can be accessed using a simple JSON payload:



## Creating a new cluster

1. On the head machine (master):
    - activate venv $ source rayenv/bin/activate
    - $ ./spawn_ray_head.sh

2. On one or more worker nodes (ubuntu servers in this case):
    - activate venv $ conda activate py3115 
    - $ ./spawn_ray_server.sh

3. Verify that the cluster is running:
    - $ ray status
    - http://0.0.0.0:8265/#/cluster

## Generate Mandelbrot Zoom
$ python ray_head.py
$ python client.py
