import cProfile
import pstats

from helpers import *

profiler = cProfile.Profile()
profiler.enable()

video_file = generate_mandelbrot_video(
    center_point=(-1.5, 0),
    num_frames=80,
    fps=20,
    initial_scale=2.5,
    scale_factor=1.20,
    frame_dimensions=(1000, 1000),
    maxiter=520,
)

print(f"Video saved to {video_file}")
profiler.disable()

with open("profiling_results.txt", "w") as f:
    stats = pstats.Stats(profiler, stream=f).sort_stats("cumtime")
    stats.print_stats()
