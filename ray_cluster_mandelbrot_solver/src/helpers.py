import io
import os
import tempfile

import moviepy.editor as mpy
import numpy as np
import ray
from PIL import Image

from mandelbrot import compute_mandelbrot_frame, process_frame


@ray.remote
def save_image(img_data, filename):
    image = Image.open(io.BytesIO(img_data))
    image.save(filename)


def compile_video(frame_images: list, fps: int = 15) -> io.BytesIO:
    # Convert in-memory images to NumPy arrays and then to moviepy ImageClips
    clips = []
    for img_data in frame_images:
        with Image.open(io.BytesIO(img_data)) as img:
            numpy_image = np.array(img)
            clip = mpy.ImageClip(numpy_image, duration=1.0 / fps)
            clips.append(clip)

    # Concatenate clips to make a video
    video = mpy.concatenate_videoclips(clips, method="compose")

    # Create a temporary file to write the video
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        video_file_path = temp_file.name

    # Write the video to the temporary file
    video.write_videofile(
        video_file_path, codec="libx264", audio=False, fps=fps, bitrate="5000k"
    )

    # Read the video from the temporary file into a BytesIO buffer
    with open(video_file_path, "rb") as file:
        video_buffer = io.BytesIO(file.read())

    # Optionally, delete the temporary file here if you want to clean up
    os.remove(video_file_path)

    video_buffer.seek(0)
    return video_buffer


def generate_mandelbrot_video(
    center_point: tuple[float, float],
    num_frames: int,
    fps: int,
    initial_scale: float,
    scale_factor: float,
    frame_dimensions: tuple[int, int],
    maxiter: int,
) -> str:
    compute_tasks = []
    current_scale = initial_scale

    # Step 1: Schedule computation of Mandelbrot data for each frame
    for _ in range(num_frames):
        half_width = current_scale * frame_dimensions[0] / frame_dimensions[1] / 2
        half_height = current_scale / 2

        xmin = center_point[0] - half_width
        xmax = center_point[0] + half_width
        ymin = center_point[1] - half_height
        ymax = center_point[1] + half_height

        compute_tasks.append(
            compute_mandelbrot_frame.remote(
                (xmin, xmax, ymin, ymax),
                frame_dimensions[0],
                frame_dimensions[1],
                maxiter,
            )
        )

        current_scale /= scale_factor

    # Retrieve the computed Mandelbrot data
    computed_frames = ray.get(compute_tasks)

    # Extract the correct Mandelbrot data for processing
    process_tasks = [
        process_frame.remote(frame_data[2], width, height)  # Change here
        for frame_data, width, height in computed_frames
    ]

    # Retrieve the processed images
    processed_images = ray.get(process_tasks)

    # Step 3: Compile the frames into a video
    video = compile_video(processed_images, fps)

    return video
