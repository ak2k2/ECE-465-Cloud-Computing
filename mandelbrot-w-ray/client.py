# client.py
import base64
import io
import logging
import time

import moviepy.editor as mpy
import numpy as np
import ray
from mandelbrot_opencl import generate_frame
from PIL import Image

logging.basicConfig(level=logging.INFO)


def connect_to_server():
    try:
        ray.init(address="auto")
        print("Sucessfully Initialized Ray!")

    except Exception as e:
        print(f"An error occurred: {e}")


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
    start_delta: float,
    end_delta: float,
) -> str:
    start_delta = 2.5  # View of the whole set
    end_delta = 0.00001  # Zoomed in this much at the end

    # geometric sequence of zoom levels
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
        maxiter += 20  # increase the max iterations for each frame

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


def get_user_input(prompt, default):
    user_input = input(f"{prompt} (default is {default}): ")
    return user_input.strip() or default


def main():
    user_input = input(
        "Do you want to generate a video or act as a worker? (video/worker): "
    )

    if user_input.lower() == "video":
        connect_to_server()

        # Default parameters
        default_point = "-1.338238635,-0.057237059"  # Re, Im
        default_num_frames = "200"
        default_frame_width = "1000"
        default_frame_height = "1000"  # HD resolution
        default_maxiter = "1000"
        default_fps = "15"
        start_delta = 2.5  # View of the whole set
        end_delta = 0.00001

        # Get user's custom parameters or use defaults
        point_str = get_user_input(
            "Enter the point to zoom into as two floats, separated by a comma (e.g., -1.3,-0.05)",
            default_point,
        )
        point = tuple(map(float, point_str.split(",")))

        num_frames = int(
            get_user_input("Enter the number of frames", default_num_frames)
        )
        frame_width = int(get_user_input("Enter the frame width", default_frame_width))
        frame_height = int(
            get_user_input("Enter the frame height", default_frame_height)
        )
        frame_dimensions = (frame_width, frame_height)

        maxiter = int(
            get_user_input(
                "Enter the starting value for max iterations", default_maxiter
            )
        )
        fps = int(get_user_input("Enter the FPS", default_fps))

        start_delta = float(get_user_input("Enter the starting delta", start_delta))

        end_delta = float(get_user_input("Enter the ending delta", end_delta))

        # Request the Mandelbrot video
        st = time.time()
        video_filename = request_mandelbrot_video(
            point, num_frames, fps, frame_dimensions, maxiter, start_delta, end_delta
        )
        print(f"Video compiled: {video_filename}")
        print(f"Time elapsed: {time.time() - st}")

    elif user_input.lower() == "worker":
        connect_to_server()
        print("Worker connected to server")

        while True:
            time.sleep(60)
            print("worker alive")


if __name__ == "__main__":
    main()
