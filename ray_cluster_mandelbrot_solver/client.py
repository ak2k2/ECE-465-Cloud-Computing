from helpers import *

video_file = generate_mandelbrot_video(
    center_point=(-0.76297572, -0.083163024),
    num_frames=50,
    fps=12,
    initial_scale=2.5,
    scale_factor=1.20,
    frame_dimensions=(1500, 1500),
    maxiter=1200,
)

print(f"Video saved to {video_file}")
