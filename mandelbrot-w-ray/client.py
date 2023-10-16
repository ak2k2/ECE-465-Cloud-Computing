# client.py
import base64
import io
import time

import moviepy.editor as mpy
import numpy as np
import ray
from mandelbrot_opencl import generate_frame
from PIL import Image

import logging
import subprocess


# Set up logging level to debug to see detailed logs from Ray
logging.basicConfig(level=logging.DEBUG)


def connect_to_server():
    try:
        subprocess.run(["ray", "stop"])
        subprocess.run("ray start", "--address=192.168.1.155:6379", "--verbose")
        ray.init(address="auto")

        print("Connected to Ray server!")

    except Exception as e:
        # If there's an exception, print it out
        print(f"An error occurred: {e}")


# Call the function
connect_to_server()


def compile_video(frame_images: list, fps: int = 15) -> str:
    # Save images and store their filepaths
    frames = []
    temp_path = "temp"
    for i, img in enumerate(frame_images):
        filename = f"{temp_path}/frame_{i}.png"
        img.save(filename)
        frames.append(filename)

    # Create video from frames
    clip = mpy.ImageSequenceClip(frames, fps=fps)
    video_filename = temp_path + "/demo_zoom.mp4"
    clip.write_videofile(video_filename)

    return video_filename  # return the filename of created video


def request_mandelbrot_video(
    point: tuple[float, float],
    num_frames: int,
    fps: int,
    frame_dimensions: tuple[int, int],
    maxiter: int,
) -> str:
    start_delta = 2.5  # View of the whole set
    end_delta = 0.000005  # Zoomed in this much at the end

    # calculate the zoom levels for each frame
    zoom_levels = np.geomspace(start_delta, end_delta, num_frames)

    # calculate the coordinates for each frame based on zoom level
    frames = []
    for zoom in zoom_levels:
        frames.append(
            generate_frame.remote(
                (
                    point[0] - zoom / 2,  # xmin
                    point[0] + zoom / 2,  # xmax
                    point[1] - zoom / 2,  # ymin
                    point[1] + zoom / 2,  # ymax
                ),
                frame_dimensions[0],
                frame_dimensions[1],
                maxiter,
            )
        )
        maxiter += 1  # increase the max iterations for each frame

    # Retrieve the frames from the futures.
    frame_images = ray.get(frames)

    # decode the base64 strings and modify the images as needed
    frame_images = [
        Image.open(io.BytesIO(base64.b64decode(frame_data)))
        for frame_data in frame_images
    ]

    # Compile the frames into a video
    video = compile_video(frame_images, fps)

    return video


def main():
    user_input = input(
        "Do you want to generate a video or act as a worker? (video/worker): "
    )

    if user_input.lower() == "video":
        # Connect to the Ray cluster
        connect_to_server()
        print("Connected to Ray cluster")

        # Define parameters for the Mandelbrot video request
        point = (
            -1.358238635,  # Re
            -0.037237059,  # Im
        )
        num_frames = 600  # example frame count
        frame_dimensions = (1000, 1000)  # HD resolution
        maxiter = 400  # example max iterations
        fps = 30

        # Request the Mandelbrot video

        st = time.time()
        video_filename = request_mandelbrot_video(
            point, num_frames, fps, frame_dimensions, maxiter
        )
        print(f"Video compiled: {video_filename}")
        print(f"Time elapsed: {time.time() - st}")

    elif user_input.lower() == "worker":
        connect_to_server()
        print("Worker connected to server")

        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()
