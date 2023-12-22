import os
import pathlib
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


if __name__ == "__main__":
    # print current working directory
    print(os.getcwd())
    with open("action.yaml", "r") as file:
        config = yaml.safe_load(file)
    initialize_ray(config)
    app.run(host="0.0.0.0", port=5010)
