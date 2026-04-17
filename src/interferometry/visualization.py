import numpy as np
import matplotlib.pyplot as plt
from src.interferometry.fp_cavity import FabryPerotCavity


def plot_transmission_comparison(
    cavity: FabryPerotCavity,
    R_list: list[float],
    wavelength_range: np.ndarray,
    save_path: str | None = None,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(R_list)))
    results = cavity.plot_transmission_comparison(R_list, wavelength_range)

    for R, color in zip(R_list, colors):
        T = results[R]
        axes[0].plot(wavelength_range * 1e9, T, label=f"R={R}", color=color, linewidth=1.5)
    axes[0].set_xlabel("波长 (nm)")
    axes[0].set_ylabel("透射率")
    axes[0].set_title("F-P腔透射率与反射率的关系")
    axes[0].legend()
    axes[0].set_ylim(-0.05, 1.05)

    R_sweep = np.linspace(0.1, 0.999, 200)
    finesse_values = np.pi * np.sqrt(R_sweep) / (1 - R_sweep)
    axes[1].semilogy(R_sweep, finesse_values, "b-", linewidth=2)
    for R in R_list:
        F = np.pi * np.sqrt(R) / (1 - R)
        axes[1].plot(R, F, "ro", markersize=8)
        axes[1].annotate(f"R={R}\nF={F:.1f}", xy=(R, F), fontsize=8,
                         xytext=(R - 0.05, F * 1.5))
    axes[1].set_xlabel("反射率 R")
    axes[1].set_ylabel("精细度")
    axes[1].set_title("精细度与反射率的关系")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_spectral_ranges(
    cavity: FabryPerotCavity,
    spectral_ranges: list[tuple[float, float, str]],
    save_path: str | None = None,
) -> None:
    n_plots = len(spectral_ranges)
    ncols = 2
    nrows = (n_plots + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4 * nrows))
    axes_flat = axes.flatten() if n_plots > 1 else [axes]

    for idx, (lam_min, lam_max, title) in enumerate(spectral_ranges):
        wl = np.linspace(lam_min, lam_max, 3000)
        T = cavity.transmission(wl)
        axes_flat[idx].plot(wl * 1e9, T, linewidth=1.5)
        axes_flat[idx].set_xlabel("波长 (nm)")
        axes_flat[idx].set_ylabel("透射率")
        axes_flat[idx].set_title(title)
        axes_flat[idx].set_ylim(-0.05, 1.05)
        axes_flat[idx].grid(True, alpha=0.3)

    for idx in range(n_plots, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    plt.suptitle(f"F-P Cavity Transmission (R={cavity.R})", fontsize=14)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
