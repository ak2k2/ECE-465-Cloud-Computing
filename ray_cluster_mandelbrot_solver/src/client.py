import cProfile
import pstats

from helpers import generate_mandelbrot_video

profiler = cProfile.Profile()
profiler.enable()

video_file = generate_mandelbrot_video(
    center_point=(-0.743643887037151, 0.131825904205330),
    num_frames=120,
    fps=20,
    initial_scale=2.5,
    scale_factor=1.12,
    frame_dimensions=(1000, 1000),
    maxiter=1520,
)

print(f"Video saved to {video_file}")
profiler.disable()

with open("profiling_results.txt", "w") as f:
    stats = pstats.Stats(profiler, stream=f).sort_stats("cumtime")
    stats.print_stats()
