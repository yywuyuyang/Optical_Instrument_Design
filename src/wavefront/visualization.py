import numpy as np
import matplotlib.pyplot as plt
from src.wavefront.zernike import zernike_grid, NOLL_TO_NM, ABERRATION_NAMES


def plot_wavefront_3d(
    j: int,
    resolution: int = 256,
    save_path: str | None = None,
) -> None:
    Z = zernike_grid(j, resolution)
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(x, y)
    mask = np.isnan(Z)
    Z_masked = np.ma.array(Z, mask=mask)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z_masked, cmap="RdBu_r", vmin=-1, vmax=1, alpha=0.9)
    n, m = NOLL_TO_NM[j - 1]
    ax.set_title(f"Z{j} {ABERRATION_NAMES[j-1]} (n={n}, m={m})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Zernike值")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
