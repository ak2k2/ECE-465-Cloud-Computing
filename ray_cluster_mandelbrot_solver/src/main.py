import subprocess

import requests

from helpers import generate_mandelbrot_video

# Configuration
head_node_ip = "127.94.0.1"
head_node_port = "6379"
ray_head_address = f"{head_node_ip}:{head_node_port}"


def is_ray_head_running():
    try:
        # Attempt to connect to the head node dashboard
        response = requests.get(f"http://{head_node_ip}:8265")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def start_ray_node(is_head):
    subprocess.run(["ray", "stop"])  # Stop any existing Ray instance

    if is_head:
        # Start Ray head node
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
        # Start Ray worker node
        subprocess.run(["ray", "start", "--address", ray_head_address, "--verbose"])


if __name__ == "__main__":
    if is_ray_head_running():
        print("Ray head node detected. Starting as worker node.")
        start_ray_node(is_head=False)
    else:
        print("No Ray head node detected. Starting as head node.")
        start_ray_node(is_head=True)

    video_file = generate_mandelbrot_video(
        center_point=(-1.5, 0),
        num_frames=20,
        fps=20,
        initial_scale=2.5,
        scale_factor=1.13,
        frame_dimensions=(1000, 1000),
        maxiter=2520,
    )

    print(f"Video saved to {video_file}")

    # stop Ray
    subprocess.run(["ray", "stop"])
