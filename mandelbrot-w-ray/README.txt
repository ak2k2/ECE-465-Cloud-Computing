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

## Zooming into the mandelbrot set
$ python mandelbrot-w-ray/client.py