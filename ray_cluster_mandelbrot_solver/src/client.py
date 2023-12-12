import cProfile
import pstats

from helpers import generate_mandelbrot_video

profiler = cProfile.Profile()
profiler.enable()

video_file = generate_mandelbrot_video(
    center_point=(-1.5, 0),
    num_frames=20,
    fps=20,
    initial_scale=2.5,
    scale_factor=1.13,
    frame_dimensions=(2000, 2000),
    maxiter=2520,
)

print(f"Video saved to {video_file}")
profiler.disable()

with open("profiling_results.txt", "w") as f:
    stats = pstats.Stats(profiler, stream=f).sort_stats("cumtime")
    stats.print_stats()
