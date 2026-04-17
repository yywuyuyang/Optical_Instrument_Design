import numpy as np
import matplotlib.pyplot as plt
from src.fresnel.lens import FresnelLens


def plot_phase_map(
    lens: FresnelLens,
    resolution: int = 500,
    quantized: bool = False,
    levels: int = 8,
    save_path: str | None = None,
) -> None:
    x = np.linspace(-lens.radius, lens.radius, resolution)
    y = np.linspace(-lens.radius, lens.radius, resolution)
    X, Y = np.meshgrid(x, y)

    if quantized:
        phase = lens.quantize_phase(X, Y, levels=levels)
        title = f"菲涅尔透镜量化相位 ({levels}阶)"
    else:
        phase = lens.wrapped_phase(X, Y)
        title = "菲涅尔透镜包裹相位"

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(
        phase,
        extent=[-lens.radius * 1e3, lens.radius * 1e3, -lens.radius * 1e3, lens.radius * 1e3],
        cmap="hsv",
        vmin=0,
        vmax=2 * np.pi,
    )
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(title)
    ax.set_aspect("equal")
    plt.colorbar(im, label="相位 (rad)")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_ring_structure(
    lens: FresnelLens,
    save_path: str | None = None,
    max_rings: int | None = None,
) -> None:
    radii = lens.ring_radii()
    n_rings = len(radii)
    
    if max_rings is not None and n_rings > max_rings:
        indices = np.linspace(0, n_rings - 1, max_rings, dtype=int)
        radii_display = radii[indices]
        n_display = max_rings
    else:
        radii_display = radii
        n_display = n_rings
    
    theta = np.linspace(0, 2 * np.pi, 500)

    fig, ax = plt.subplots(figsize=(8, 8))
    
    for i in range(n_display):
        r_outer = radii_display[-(i+1)] if i < n_display else lens.radius
        r_inner = radii_display[-(i+2)] if i+1 < n_display else 0
        
        x_outer = r_outer * np.cos(theta) * 1e3
        y_outer = r_outer * np.sin(theta) * 1e3
        x_inner = r_inner * np.cos(theta) * 1e3
        y_inner = r_inner * np.sin(theta) * 1e3
        
        x = np.concatenate([x_outer, x_inner[::-1]])
        y = np.concatenate([y_outer, y_inner[::-1]])
        
        color = "lightblue" if i % 2 == 0 else "white"
        ax.fill(x, y, color=color, edgecolor="black", linewidth=0.5)

    r_max_mm = lens.radius * 1e3
    ax.set_xlim(-r_max_mm * 1.1, r_max_mm * 1.1)
    ax.set_ylim(-r_max_mm * 1.1, r_max_mm * 1.1)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    
    subtitle = f"({n_display}个环带"
    if max_rings and n_rings > max_rings:
        subtitle += f", 共{n_rings}个)"
    else:
        subtitle += ")"
    ax.set_title(
        f"菲涅尔透镜环带结构\n"
        f"{subtitle}, f={lens.focal_length*1e3:.0f}mm, "
        f"λ={lens.wavelength*1e9:.0f}nm)"
    )

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
