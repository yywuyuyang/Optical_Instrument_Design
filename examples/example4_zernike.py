import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from src.wavefront.zernike import plot_zernike_modes
from src.wavefront.visualization import plot_wavefront_3d

plt.style.use("config/optics_style.mplstyle")

os.makedirs("figures/wavefront", exist_ok=True)
plot_zernike_modes(noll_max=36, resolution=256, save_path="figures/wavefront/zernike_36.png")

for j in [4, 7, 8, 11]:
    plot_wavefront_3d(j, save_path=f"figures/wavefront/zernike_3d_Z{j}.png")
