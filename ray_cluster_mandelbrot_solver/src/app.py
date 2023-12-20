import subprocess

import yaml
from flask import Flask, Response

from helpers import generate_mandelbrot_video

app = Flask(__name__)


def initialize_ray(config):
    head_node_ip = config["ray"].get("head_node_ip", "127.0.0.1")
    head_node_port = "6379"
    ray_head_address = f"{head_node_ip}:{head_node_port}"

    if config["ray"]["action"] == "c":
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
    with open("action.yaml", "r") as file:
        config = yaml.safe_load(file)
    initialize_ray(config)
    app.run(host="0.0.0.0", port=5010)
