import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.interferometry.fp_cavity import FabryPerotCavity
from src.interferometry.visualization import plot_transmission_comparison, plot_spectral_ranges

plt.style.use("config/optics_style.mplstyle")

cavity = FabryPerotCavity(R=0.95, h=100e-6, n=1.0, theta=0.0)

print(f"F-P腔参数:")
print(f"  反射率: {cavity.R}")
print(f"  腔长: {cavity.h*1e6:.0f} μm")
print(f"  折射率: {cavity.n}")
print(f"  精细度: {cavity.finesse():.2f}")
print(f"  自由光谱范围 @632nm: {cavity.fsr(632e-9)*1e9:.2f} nm")
print(f"  半高全宽 @632nm: {cavity.fwhm(632e-9)*1e9:.4f} nm")
print(f"  Q值 @632nm: {cavity.q_factor(632e-9):.0f}")

wl_range = np.linspace(600e-9, 660e-9, 5000)
R_list = [0.5, 0.7, 0.9, 0.95, 0.99]
os.makedirs("figures/interferometry", exist_ok=True)
plot_transmission_comparison(cavity, R_list, wl_range, save_path="figures/interferometry/transmission_vs_R.png")

spectral_ranges = [
    (400e-9, 800e-9, "可见光范围"),
    (620e-9, 640e-9, "窄带范围1"),
    (630e-9, 635e-9, "窄带范围2"),
    (1000e-9, 2000e-9, "近红外范围"),
]
plot_spectral_ranges(cavity, spectral_ranges, save_path="figures/interferometry/spectral_ranges.png")
