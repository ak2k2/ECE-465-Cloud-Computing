import logging

import ray

from helpers import generate_mandelbrot_video

logging.basicConfig(level=logging.INFO)


def connect_to_server():
    try:
        ray.init(address="auto")
        print("Sucessfully Initialized Ray!")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    connect_to_server()

    # Generate a video
    video_file = generate_mandelbrot_video(
        center_point=(-1.5, 0.0),
        num_frames=10,
        fps=6,
        initial_scale=3.5,
        scale_factor=1.5,
        frame_dimensions=(1000, 1000),
        maxiter=1000,
    )

    print(f"Video saved to {video_file}")
