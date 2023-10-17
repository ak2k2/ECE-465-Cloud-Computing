# client.py
import base64
import io
import json
import logging
import socket
import time
import subprocess

import moviepy.editor as mpy
import numpy as np
import ray
from mandelbrot_opencl import generate_frame
from PIL import Image

from concurrent.futures import ThreadPoolExecutor


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
    DB_path = "DB"
    for i, img in enumerate(frame_images):
        filename = f"{DB_path}/frame_{i}.png"
        img.save(filename)
        frames.append(filename)

    # Create video from frames
    clip = mpy.ImageSequenceClip(frames, fps=fps)
    video_filename = DB_path + "/demo_zoom.mp4"
    clip.write_videofile(video_filename)

    return video_filename  # return the filename of created video


def generate_mandelbrot_video(
    point: tuple[float, float],
    num_frames: int,
    fps: int,
    frame_dimensions: tuple[int, int],
    maxiter: int,
    start_delta: float,
    end_delta: float,
) -> str:
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
        maxiter += 1000  # Increase the max iterations for each frame

    # Retrieve the frames from the futures.
    frame_images = ray.get(frames)

    # Decode the base64 strings and modify the images as needed
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


def process_request(request_json):
    connect_to_server()

    # Parse the JSON data
    try:
        data = json.loads(request_json)
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {str(e)}"

    # Extract parameters from JSON or set to default if not provided
    point = tuple(map(float, data.get("point", "-1.338238635,-0.057237059").split(",")))
    num_frames = int(data.get("num_frames", 20))
    frame_width = int(data.get("frame_width", 1000))
    frame_height = int(data.get("frame_height", 1000))
    frame_dimensions = (frame_width, frame_height)
    maxiter = int(data.get("maxiter", 1000))
    fps = int(data.get("fps", 15))
    start_delta = float(data.get("start_delta", 2.5))
    end_delta = float(data.get("end_delta", 0.00001))

    # Status
    st = time.time()
    video_filename = generate_mandelbrot_video(
        point, num_frames, fps, frame_dimensions, maxiter, start_delta, end_delta
    )
    print(f"Video compiled: {video_filename}")
    print(f"Time elapsed: {time.time() - st}")


def handle_client(conn, addr):
    print("Connected by", addr)
    try:
        while True:
            request_json = conn.recv(1024)
            if not request_json:
                break
            request_json = request_json.decode("utf-8")
            video_filename = process_request(request_json)

            with open(video_filename, "rb") as f:
                while True:
                    bytes_read = f.read(1024)
                    if not bytes_read:
                        break
                    conn.sendall(bytes_read)
            print(f"Video sent to {addr}")

            # Delete the video file
            subprocess.run(["rm", video_filename])

    finally:
        conn.close()


def start_server():
    HOST = "127.0.0.1"
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server started at {HOST}:{PORT}")
        with ThreadPoolExecutor() as executor:
            while True:
                conn, addr = s.accept()
                executor.submit(handle_client, conn, addr)


if __name__ == "__main__":
    start_server()
