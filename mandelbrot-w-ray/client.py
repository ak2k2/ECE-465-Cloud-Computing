# client.py
import base64

import moviepy.editor as mpy
import numpy as np
import ray
from mandelbrot_opencl import generate_frame
from PIL import Image

import io


def connect_to_server():
    ray.init(address="auto")


def compile_video(frame_images):
    # Save images and store their filepaths
    frames = []
    temp_path = "temp"
    for i, img in enumerate(frame_images):
        filename = f"{temp_path}/frame_{i}.png"
        img.save(filename)
        frames.append(filename)

    # Create video from frames
    fps = 10  # or whatever fps you want
    clip = mpy.ImageSequenceClip(frames, fps=fps)
    video_filename = temp_path + "/demo_zoom.mp4"
    clip.write_videofile(video_filename)

    return video_filename  # return the filename of created video


def request_mandelbrot_video(point, num_frames, frame_dimensions, maxiter):
    start_delta = 2.5  # View of the whole set
    end_delta = 0.01  # Zoomed in this much at the end

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
    video = compile_video(frame_images)

    return video


def main():
    # Connect to the Ray cluster
    connect_to_server()

    # Define parameters for the Mandelbrot video request
    point = (
        0,
        0,
    )  # example coordinates, should be based on your requirements
    num_frames = 20  # example frame count
    frame_dimensions = (2000, 2000)  # HD resolution
    maxiter = 200  # example max iterations

    # Request the Mandelbrot video
    video_filename = request_mandelbrot_video(
        point, num_frames, frame_dimensions, maxiter
    )

    print(f"Video compiled: {video_filename}")


if __name__ == "__main__":
    main()
    # connect_to_server()
    # byteframe = generate_frame.remote(
    #     coords=(-2.0, 1.0, -1.0, 1.0), width=1000, height=1000, maxiter=100
    # )

    # byteframe = ray.get(byteframe)

    # # display the frame which is a base64 string as an image
    # imgdata = base64.b64decode(byteframe)
    # filename = "frame.png"
    # with open(filename, "wb") as f:
    #     f.write(imgdata)
    # image = Image.open(filename)
    # image.show()
