import cProfile
import pstats

from helpers import *

profiler = cProfile.Profile()
profiler.enable()

video_file = generate_mandelbrot_video(
    center_point=(-1.768778839, 0.001738953),
    num_frames=6,
    fps=20,
    initial_scale=2.5,
    scale_factor=1.23,
    frame_dimensions=(1200, 1200),
    maxiter=5520,
)

print(f"Video saved to {video_file}")
profiler.disable()

with open("profiling_results.txt", "w") as f:
    stats = pstats.Stats(profiler, stream=f).sort_stats("cumtime")
    stats.print_stats()
