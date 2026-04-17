import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from src.fresnel.lens import FresnelLens
from src.fresnel.visualization import plot_phase_map, plot_ring_structure

plt.style.use("config/optics_style.mplstyle")

lens = FresnelLens(
    focal_length=0.1,
    wavelength=632e-9,
    radius=0.0125,
    n=1.5,
)

print(f"菲涅尔透镜设计参数:")
print(f"  波长: {lens.wavelength*1e9:.0f} nm")
print(f"  焦距: {lens.focal_length*1e3:.0f} mm")
print(f"  半径: {lens.radius*1e3:.1f} mm")
print(f"  F数: {lens.f_number():.2f}")
print(f"  环带数量: {lens.num_rings()}")
print(f"  刻蚀深度: {lens.etch_depth()*1e9:.1f} nm")
print(f"  焦点光斑尺寸: {lens.focal_spot_size()*1e6:.1f} μm")

radii = lens.ring_radii()
print(f"\n环带半径 (mm):")
for i, r in enumerate(radii):
    print(f"  第{i+1}环: {r*1e3:.4f} mm")

os.makedirs("figures/fresnel", exist_ok=True)
plot_phase_map(lens, save_path="figures/fresnel/phase_map.png")
plot_phase_map(lens, quantized=True, levels=8, save_path="figures/fresnel/phase_quantized.png")
plot_ring_structure(lens, save_path="figures/fresnel/ring_structure.png")
