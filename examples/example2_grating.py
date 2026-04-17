import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.grating.analysis import DiffractionGrating
from src.grating.visualization import plot_diffraction_angles, plot_efficiency

plt.style.use("config/optics_style.mplstyle")

grating = DiffractionGrating(
    period=2e-6,
    wavelength=632e-9,
    incidence_angle=0.0,
    max_order=5,
)

print(f"衍射光栅参数:")
print(f"  光栅周期: {grating.period*1e6:.1f} μm")
print(f"  波长: {grating.wavelength*1e9:.0f} nm")
print(f"  入射角: {np.degrees(grating.incidence_angle):.2f}°")

angles = grating.all_diffraction_angles()
print(f"\n衍射角 (垂直入射):")
for m, angle in angles.items():
    if angle is not None:
        print(f"  m={m:+d}: {np.degrees(angle):.2f}°")
    else:
        print(f"  m={m:+d}: 无传播级次")

os.makedirs("figures/grating", exist_ok=True)
plot_diffraction_angles(grating, save_path="figures/grating/diffraction_angles.png")
plot_efficiency(grating, phase_depth=2.0, duty_cycle=0.5, save_path="figures/grating/efficiency.png")
