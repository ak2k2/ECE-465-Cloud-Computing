import io

import moviepy.editor as mpy
import numpy as np
import ray
from PIL import Image

from mandelbrot_opencl import compute_mandelbrot_frame, process_frame


@ray.remote
def save_image(img_data, filename):
    image = Image.open(io.BytesIO(img_data))
    image.save(filename)


def compile_video(frame_images: list, fps: int = 15, DB_path: str = "DB") -> str:
    # Parallel image saving
    save_tasks = []
    for i, img_data in enumerate(frame_images):
        filename = f"{DB_path}/frame_{i}.png"
        task = save_image.remote(img_data, filename)
        save_tasks.append(task)

    # Wait for all images to be saved
    ray.get(save_tasks)

    # Create video from frames
    frames = [f"{DB_path}/frame_{i}.png" for i in range(len(frame_images))]
    clip = mpy.ImageSequenceClip(frames, fps=fps)
    video_filename = DB_path + "/demo_zoom.mp4"
    clip.write_videofile(video_filename)

    return video_filename


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
