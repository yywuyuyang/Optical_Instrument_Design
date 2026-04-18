import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv
from src.grating.analysis import DiffractionGrating


def plot_diffraction_angles(
    grating: DiffractionGrating,
    save_path: str | None = None,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)

    theta_i_range = np.linspace(-np.pi / 3, np.pi / 3, 200)
    for m in range(-grating.max_order, grating.max_order + 1):
        valid_i, valid_m = [], []
        for theta_i in theta_i_range:
            sin_val = m * grating.wavelength / grating.period + np.sin(theta_i)
            if np.abs(sin_val) <= 1:
                valid_i.append(np.degrees(theta_i))
                valid_m.append(np.degrees(np.arcsin(sin_val)))
        if valid_i:
            axes[0].plot(valid_i, valid_m, label=f"m={m}", linewidth=1.5)
    axes[0].set_xlabel("入射角 (°)")
    axes[0].set_ylabel("衍射角 (°)")
    axes[0].set_title("衍射角与入射角的关系")
    axes[0].legend(fontsize=8, ncol=2)
    axes[0].axhline(y=0, color="k", linestyle="--", alpha=0.3)

    wl_range = np.linspace(400e-9, 800e-9, 200)
    for m in range(-grating.max_order, grating.max_order + 1):
        if m == 0:
            continue
        valid_wl, valid_ang = [], []
        for lam in wl_range:
            sin_val = m * lam / grating.period + np.sin(grating.incidence_angle)
            if np.abs(sin_val) <= 1:
                valid_wl.append(lam * 1e9)
                valid_ang.append(np.degrees(np.arcsin(sin_val)))
        if valid_wl:
            axes[1].plot(valid_wl, valid_ang, label=f"m={m}", linewidth=1.5)
    axes[1].set_xlabel("波长 (nm)")
    axes[1].set_ylabel("衍射角 (°)")
    axes[1].set_title("衍射角与波长的关系")
    axes[1].legend(fontsize=8, ncol=2)

    d_range = np.linspace(1e-6, 5e-6, 200)
    for m in range(-grating.max_order, grating.max_order + 1):
        if m == 0:
            continue
        valid_d, valid_ang = [], []
        for d in d_range:
            sin_val = m * grating.wavelength / d + np.sin(grating.incidence_angle)
            if np.abs(sin_val) <= 1:
                valid_d.append(d * 1e6)
                valid_ang.append(np.degrees(np.arcsin(sin_val)))
        if valid_d:
            axes[2].plot(valid_d, valid_ang, label=f"m={m}", linewidth=1.5)
    axes[2].set_xlabel("光栅周期 (μm)")
    axes[2].set_ylabel("衍射角 (°)")
    axes[2].set_title("衍射角与光栅周期的关系")
    axes[2].legend(fontsize=8, ncol=2)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_efficiency(
    grating: DiffractionGrating,
    phase_depth: float = 2.0,
    duty_cycle: float = 0.5,
    save_path: str | None = None,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)

    orders = list(range(-grating.max_order, grating.max_order + 1))

    eff_sine = [grating.efficiency_sine_phase(m, phase_depth) for m in orders]
    axes[0].bar(orders, eff_sine, color="steelblue", alpha=0.7)
    axes[0].set_xlabel("衍射级次")
    axes[0].set_ylabel("衍射效率")
    axes[0].set_title(f"正弦相位光栅 (深度={phase_depth:.1f}rad)")

    eff_amp = [grating.efficiency_amplitude(m, duty_cycle) for m in orders]
    axes[1].bar(orders, eff_amp, color="coral", alpha=0.7)
    axes[1].set_xlabel("衍射级次")
    axes[1].set_ylabel("衍射效率")
    axes[1].set_title(f"振幅型光栅 (占空比={duty_cycle:.1f})")

    depths = np.linspace(0, 4 * np.pi, 200)
    for m in [0, 1, 2, -1, -2]:
        eff = [float(jv(m, d / 2) ** 2) for d in depths]
        axes[2].plot(depths / np.pi, eff, label=f"m={m}", linewidth=1.5)
    axes[2].set_xlabel("相位深度 (π rad)")
    axes[2].set_ylabel("衍射效率")
    axes[2].set_title("正弦相位光栅：衍射效率与相位深度的关系")
    axes[2].legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
