import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.imaging.stereo import StereoRangingSystem
from src.imaging.visualization import plot_optical_layout, plot_error_analysis

plt.style.use("config/optics_style.mplstyle")

system = StereoRangingSystem(
    baseline=0.065,
    focal_length=0.008,
    pixel_size=3.45e-6,
    image_width=1920,
    image_height=1080,
)

print(f"双目测距系统参数:")
print(f"  基线长度: {system.baseline*1e3:.1f} mm")
print(f"  焦距: {system.focal_length*1e3:.1f} mm")
print(f"  像素尺寸: {system.pixel_size*1e6:.2f} μm")
print(f"  分辨率: {system.image_width}x{system.image_height}")
print(f"  水平视场角: {np.degrees(system.fov_horizontal()):.1f}°")
print(f"  垂直视场角: {np.degrees(system.fov_vertical()):.1f}°")
print(f"  最小测距 (1px视差): {system.min_measurable_distance():.2f} m")
print(f"  最大测距 (0.1px精度): {system.max_measurable_distance():.2f} m")

for d in [1, 2, 5, 10]:
    disp = system.disparity_from_distance(d)
    err = system.range_error(d)
    print(f"  @ {d}m: 视差={disp:.1f}px, 误差={err:.3f}m ({err/d*100:.1f}%)")

os.makedirs("figures/imaging", exist_ok=True)
plot_optical_layout(system, target_distance=5.0, save_path="figures/imaging/光路布局.png")
plot_error_analysis(system, save_path="figures/imaging/测距误差分析.png")
