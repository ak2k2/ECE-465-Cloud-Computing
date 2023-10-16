# client.py
import base64

import moviepy.editor as mpy
import numpy as np
import ray
from mandelbrot_opencl import generate_frame
from PIL import Image

import io


def connect_to_server():
    ray.init(address="ray://192.168.1.11:6379", _redis_password="5241590000000000")


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
    end_delta = 0.001  # Zoomed in this much at the end

    # calculate the zoom levels for each frame
    zoom_levels = np.geomspace(start_delta, end_delta, num_frames)

    # calculate the coordinates for each frame based on zoom level
    frames = [
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
        for zoom in zoom_levels
    ]

    # Retrieve the frames from the futures.
    frame_images = ray.get(frames)

    # decode the base64 strings and modify the images as needed
    frame_images = [
        Image.open(io.BytesIO(base64.b64decode(frame_data)))
        for frame_data in frame_images
    ]

    # Compile the frames into a video
    video = compile_video(frame_images, fps=15)

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
            -0.706710842,  # Re
            -0.288516551,  # Im
        )
        num_frames = 2  # example frame count
        frame_dimensions = (2000, 2000)  # HD resolution
        maxiter = 100  # example max iterations

        # Request the Mandelbrot video
        video_filename = request_mandelbrot_video(
            point, num_frames, frame_dimensions, maxiter
        )

        print(f"Video compiled: {video_filename}")

    elif user_input.lower() == "worker":
        import time

        connect_to_server()
        print("Worker connected to server")

        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()
