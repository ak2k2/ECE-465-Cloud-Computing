import io

import moviepy.editor as mpy
import ray
from PIL import Image

from mandelbrot_opencl import generate_frame


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
    center_point: tuple[float, float],
    num_frames: int,
    fps: int,
    initial_scale: float,
    scale_factor: float,
    frame_dimensions: tuple[int, int],
    maxiter: int,
) -> str:
    frames = []
    current_scale = initial_scale

    for _ in range(num_frames):
        # Calculate the coordinates for each frame based on the current scale
        half_width = current_scale * frame_dimensions[0] / frame_dimensions[1] / 2
        half_height = current_scale / 2

        xmin = center_point[0] - half_width
        xmax = center_point[0] + half_width
        ymin = center_point[1] - half_height
        ymax = center_point[1] + half_height

        frames.append(
            generate_frame.remote(
                (xmin, xmax, ymin, ymax),
                frame_dimensions[0],
                frame_dimensions[1],
                maxiter,
            )
        )

        # Update the scale for the next frame
        current_scale /= scale_factor

    # Retrieve the frames from the futures
    frame_images = ray.get(frames)

    # Convert byte arrays to images
    frame_images = [Image.open(io.BytesIO(frame_data)) for frame_data in frame_images]

    # Compile the frames into a video
    video = compile_video(frame_images, fps)

    return video
