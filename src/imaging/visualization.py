import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from src.imaging.stereo import StereoRangingSystem


def plot_optical_layout(
    system: StereoRangingSystem,
    target_distance: float = 5.0,
    save_path: str | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))

    B = system.baseline
    f = system.focal_length
    fov_h = system.fov_horizontal()

    ax.plot([-B / 2, -B / 2], [0, 0], "ro", markersize=10, label="左相机")
    ax.plot([B / 2, B / 2], [0, 0], "bo", markersize=10, label="右相机")
    ax.plot([0, 0], [0, 0], "k+", markersize=12, markeredgewidth=2)

    ax.annotate("", xy=(-B / 2, 0), xytext=(B / 2, 0),
                arrowprops=dict(arrowstyle="<->", color="green", lw=2))
    ax.text(0, -0.15, f"B={B*1e3:.0f}mm", ha="center", fontsize=10, color="green")

    half_w = target_distance * np.tan(fov_h / 2)
    ax.plot([-B / 2, -half_w], [0, target_distance], "r--", alpha=0.4)
    ax.plot([-B / 2, half_w], [0, target_distance], "r--", alpha=0.4)
    ax.plot([B / 2, -half_w], [0, target_distance], "b--", alpha=0.4)
    ax.plot([B / 2, half_w], [0, target_distance], "b--", alpha=0.4)

    ax.plot([0, 0], [0, target_distance], "k--", alpha=0.3, label="光轴")
    ax.plot(0, target_distance, "g^", markersize=12, label=f"目标 ({target_distance}m)")

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.5, target_distance * 1.2)
    ax.set_xlabel("水平位置 (m)")
    ax.set_ylabel("距离 (m)")
    ax.set_title(
        f"双目视觉系统光路图\n"
        f"视场角={np.degrees(fov_h):.1f}°, f={f*1e3:.1f}mm"
    )
    ax.legend(loc="upper right")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_error_analysis(
    system: StereoRangingSystem,
    distance_range: np.ndarray | None = None,
    disparity_error: float = 0.5,
    save_path: str | None = None,
) -> None:
    if distance_range is None:
        distance_range = np.linspace(0.5, 10, 200)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    disparity = system.disparity_from_distance(distance_range)
    axes[0].plot(distance_range, disparity, "b-", linewidth=2)
    for d in [1, 2, 5, 10]:
        disp = system.disparity_from_distance(d)
        axes[0].annotate(f"{d}m: {disp:.1f}px", xy=(d, disp),
                         xytext=(d + 0.3, disp + 5), fontsize=9,
                         arrowprops=dict(arrowstyle="->", color="red"))
    axes[0].set_xlabel("距离 (m)")
    axes[0].set_ylabel("视差 (像素)")
    axes[0].set_title("距离与视差的关系")
    axes[0].grid(True, alpha=0.3)

    baselines = [0.03, 0.065, 0.1, 0.2]
    for B in baselines:
        temp = StereoRangingSystem(baseline=B, focal_length=system.focal_length,
                                   pixel_size=system.pixel_size)
        disp = temp.disparity_from_distance(distance_range)
        axes[1].plot(distance_range, disp, label=f"B={B*1e3:.0f}mm", linewidth=1.5)
    axes[1].set_xlabel("距离 (m)")
    axes[1].set_ylabel("视差 (像素)")
    axes[1].set_title("视差与基线长度的关系")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    abs_error = system.range_error(distance_range, disparity_error)
    rel_error = system.relative_error(distance_range, disparity_error) * 100
    ax2 = axes[2]
    ax2.plot(distance_range, abs_error, "r-", linewidth=2, label="绝对误差 (m)")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(distance_range, rel_error, "b--", linewidth=2, label="相对误差 (%)")
    ax2.set_xlabel("距离 (m)")
    ax2.set_ylabel("绝对误差 (m)", color="red")
    ax2_twin.set_ylabel("相对误差 (%)", color="blue")
    ax2.set_title(f"测距误差分析 (视差误差={disparity_error}px)")
    ax2.legend(loc="upper left")
    ax2_twin.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
