import os
import pathlib
import socket
import subprocess

import yaml
from flask import Flask, Response

from helpers import generate_mandelbrot_video

# set parent directory as working directory
os.chdir(pathlib.Path(__file__).parent.absolute())


app = Flask(__name__)

import ray


def initialize_ray(config):
    if ray.is_initialized():
        print("Ray is already initialized.")
        return

    print("Stopping all current ray processes...")
    subprocess.run(["ray", "stop"])

    head_node_ip = config["ray"].get("head_node_ip", "127.0.0.1")
    head_node_port = "6379"
    ray_head_address = f"{head_node_ip}:{head_node_port}"

    if config["ray"]["action"] == "c":
        print("creating ray cluster")
        subprocess.run(
            [
                "ray",
                "start",
                "--head",
                "--node-ip-address",
                head_node_ip,
                "--port",
                head_node_port,
                "--verbose",
            ]
        )
    else:
        print("joining ray cluster")
        subprocess.run(["ray", "start", "--address", ray_head_address, "--verbose"])


@app.route("/generate_video")
def generate_video():
    video_buffer = generate_mandelbrot_video(
        center_point=(-0.748131411301211, 0.08408805193551501),
        num_frames=5,
        fps=12,
        initial_scale=2.5,
        scale_factor=1.2,
        frame_dimensions=(500, 500),
        maxiter=1020,
    )
    return Response(video_buffer, mimetype="video/mp4")


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def check_critical_services():
    # Example check: Verify if Ray is initialized and critical ports are open
    try:
        # Check Ray initialization
        if not ray.is_initialized():
            return False

        # Flask
        if not is_port_open(5010):
            return False

        # Ray head node is running
        if not is_port_open(6379):
            return False

        # Ray dashboard is running
        if not is_port_open(8265):
            return False

        # Ray GCS server is running
        if not is_port_open(8075):
            return False

        if not is_port_open(8076):
            return False

        if not is_port_open(8077):
            return False

        if not is_port_open(6666):
            return False

        # worker nodes 10000-11000
        for wport in range(10000, 11000):
            if not is_port_open(wport):
                return False

        print("Health check passed.")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


@app.route("/health")
def health_check():
    if check_critical_services():
        return Response("OK", status=200)
    else:
        return Response("Service Unavailable", status=503)


if __name__ == "__main__":
    # print current working directory
    print(os.getcwd())
    with open("action.yaml", "r") as file:
        config = yaml.safe_load(file)
    initialize_ray(config)
    app.run(host="0.0.0.0", port=5010)
