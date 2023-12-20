import subprocess

import ray
import requests
from flask import Flask, Response

from helpers import generate_mandelbrot_video

# Configuration for Ray
head_node_ip = "127.94.0.1"
head_node_port = "6379"
ray_head_address = f"{head_node_ip}:{head_node_port}"


def is_ray_head_running():
    try:
        response = requests.get(f"http://{head_node_ip}:8265")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def start_ray_node(is_head):
    subprocess.run(["ray", "stop"])  # Stop any existing Ray instance

    if is_head:
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
        subprocess.run(["ray", "start", "--address", ray_head_address, "--verbose"])


def initialize_ray():
    if is_ray_head_running():
        print("Ray head node detected. Starting as worker node.")
        start_ray_node(is_head=False)
    else:
        print("No Ray head node detected. Starting as head node.")
        start_ray_node(is_head=True)


app = Flask(__name__)


@app.route("/generate_video")
def generate_video():
    video_buffer = generate_mandelbrot_video(
        center_point=(-0.743643887037151, 0.131825904205330),
        num_frames=10,
        fps=5,
        initial_scale=2.5,
        scale_factor=1.2,
        frame_dimensions=(500, 500),
        maxiter=1020,
    )
    return Response(video_buffer, mimetype="video/mp4")


if __name__ == "__main__":
    initialize_ray()  # Initialize Ray when the Flask app starts
    app.run(host="0.0.0.0", port=5010)
