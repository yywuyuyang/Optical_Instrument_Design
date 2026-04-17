import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
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
n_rings = len(radii)
print(f"\n环带数量: {n_rings}")

os.makedirs("figures/fresnel", exist_ok=True)

fig = plt.figure(figsize=(16, 10), constrained_layout=True)

ax1 = fig.add_subplot(2, 3, 1)
ax1.text(0.5, 0.9, "菲涅尔透镜设计参数", fontsize=14, fontweight="bold",
         ha="center", transform=ax1.transAxes)
params_text = (
    f"波长 λ = {lens.wavelength*1e9:.0f} nm\n"
    f"焦距 f = {lens.focal_length*1e3:.0f} mm\n"
    f"直径 D = {lens.radius*2*1e3:.1f} mm\n"
    f"F数 = {lens.f_number():.2f}\n"
    f"折射率 n = {lens.n}\n"
    f"环带数 = {n_rings}\n"
    f"刻蚀深度 = {lens.etch_depth()*1e9:.1f} nm"
)
ax1.text(0.5, 0.5, params_text, fontsize=12, ha="center", va="center",
         transform=ax1.transAxes,
         bbox=dict(boxstyle="round,pad=0.6", facecolor="#E3F2FD", edgecolor="#1565C0"))
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.axis("off")

ax2 = fig.add_subplot(2, 3, 2)
ring_nums = np.arange(1, n_rings + 1)
ax2.plot(ring_nums[:100], radii[:100] * 1e3, "b-", linewidth=1.5)
ax2.scatter(ring_nums[:100], radii[:100] * 1e3, s=8, c="red", zorder=3)
ax2.set_xlabel("环带序号 n")
ax2.set_ylabel("环带半径 (mm)")
ax2.set_title(f"环带半径分布 r = √(nλf)")
ax2.grid(True, alpha=0.3)

ax3 = fig.add_subplot(2, 3, 3)
x_radial = np.linspace(-lens.radius, lens.radius, 1000)
y_zero = np.zeros_like(x_radial)
phase_radial = lens.wrapped_phase(x_radial.reshape(-1, 1), y_zero.reshape(1, -1))[0, :]
ax3.plot(x_radial * 1e3, phase_radial, "b-", linewidth=1.5)
ax3.set_xlabel("径向位置 (mm)")
ax3.set_ylabel("相位 (rad)")
ax3.set_title("包裹相位分布 (0~2π)")
ax3.grid(True, alpha=0.3)

ax4 = fig.add_subplot(2, 3, (4, 5))
r_plot = lens.radius * 1e3
step_height = lens.etch_depth() * 1e9
n_show = min(n_rings, 80)
for i in range(n_show):
    r_inner = 0 if i == 0 else radii[i-1] * 1e3
    r_outer = radii[i] * 1e3
    color = "#42A5F5" if i % 2 == 0 else "#BBDEFB"
    ax4.fill_between([r_inner, r_outer], [0, 0],
                     [step_height if i % 2 else step_height * 0.9,
                      step_height if i % 2 else step_height * 0.9],
                     color=color, edgecolor="#1565C0", linewidth=0.5)
if n_show < n_rings:
    ax4.fill_between([radii[n_show-1]*1e3, r_plot], [0, 0],
                     [step_height/2, step_height/2], color="#BDBDBD",
                     edgecolor="gray", linewidth=0.5, hatch="//")
    ax4.text((radii[n_show-1]+lens.radius)/2*1e3, step_height/2,
             f"... 共{n_rings}环", ha="center", va="center", fontsize=10)
ax4.annotate("", xy=(0, -step_height*0.15), xytext=(r_plot, -step_height*0.15),
             arrowprops=dict(arrowstyle="<->", lw=1.5, color="black"))
ax4.text(r_plot/2, -step_height*0.25, f"直径 D = {lens.radius*2*1e3:.1f} mm",
        ha="center", fontsize=11, fontweight="bold")
ax4.annotate("", xy=(-r_plot*0.08, 0), xytext=(-r_plot*0.08, step_height),
             arrowprops=dict(arrowstyle="<->", lw=1.5, color="black"))
ax4.text(-r_plot*0.15, step_height/2, f"h={step_height:.0f}nm",
        ha="right", va="center", fontsize=11, fontweight="bold")
ax4.set_xlim(-r_plot*0.25, r_plot*1.1)
ax4.set_ylim(-step_height*0.35, step_height*1.3)
ax4.set_xlabel("径向位置 (mm)")
ax4.set_ylabel("高度 (nm)")
ax4.set_title("菲涅尔透镜截面结构（阶梯状，蓝白交替透光/遮光）")
ax4.grid(True, alpha=0.2, axis="y")

ax5 = fig.add_subplot(2, 3, 6)
x = np.linspace(-lens.radius, lens.radius, 300)
y = np.linspace(-lens.radius, lens.radius, 300)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)
mask = R <= lens.radius
phase_2d = np.zeros_like(R)
phase_2d[mask] = lens.wrapped_phase(X[mask], Y[mask])
im = ax5.imshow(phase_2d, extent=[-lens.radius*1e3, lens.radius*1e3, -lens.radius*1e3, lens.radius*1e3],
                cmap="hsv", vmin=0, vmax=2*np.pi, origin="lower")
ax5.set_xlabel("x (mm)")
ax5.set_ylabel("y (mm)")
ax5.set_title("2D相位分布")
ax5.set_aspect("equal")
plt.colorbar(im, ax=ax5, label="相位 (rad)", shrink=0.8)

plt.savefig("figures/fresnel/透镜设计总览.png", dpi=300, bbox_inches="tight")
plt.show()

plot_phase_map(lens, save_path="figures/fresnel/连续相位分布.png")
plot_phase_map(lens, quantized=True, levels=8, save_path="figures/fresnel/量化相位分布.png")
plot_ring_structure(lens, save_path="figures/fresnel/环带结构.png", max_rings=50)

n_manufacture = 60
radii_mfg = radii[:n_manufacture]
r_cut = radii_mfg[-1]
print(f"\n=== 实际制造方案 ===")
print(f"  可制造环带数: {n_manufacture}")
print(f"  有效半径: {r_cut*1e3:.2f} mm (占比 {r_cut/lens.radius*100:.0f}%)")
print(f"  最内环间距: {(radii_mfg[1]-radii_mfg[0])*1e6:.1f} μm")
print(f"  最外环间距: {(radii_mfg[-1]-radii_mfg[-2])*1e6:.1f} μm")

fig_3d = plt.figure(figsize=(14, 10))

ax_3d = fig_3d.add_subplot(111, projection="3d")
N_theta = 360
theta = np.linspace(0, 2 * np.pi, N_theta)
x_ring = np.cos(theta) * r_cut * 1e3
y_ring = np.sin(theta) * r_cut * 1e3
h_step = lens.etch_depth() * 1e9
Z_base = np.zeros((N_theta,))
for i in range(n_manufacture):
    r_inner = 0 if i == 0 else radii_mfg[i-1] * 1e3
    r_outer = radii_mfg[i] * 1e3
    x_inner = np.cos(theta) * r_inner
    y_inner = np.sin(theta) * r_inner
    x_outer = np.cos(theta) * r_outer
    y_outer = np.sin(theta) * r_outer
    
    X_ring = np.zeros((N_theta, 4))
    Y_ring = np.zeros((N_theta, 4))
    Z_ring = np.zeros((N_theta, 4))
    
    X_ring[:, 0] = x_inner; Y_ring[:, 0] = y_inner; Z_ring[:, 0] = h_step if i % 2 else 0
    X_ring[:, 1] = x_outer; Y_ring[:, 1] = y_outer; Z_ring[:, 1] = h_step if i % 2 else 0
    X_ring[:, 2] = x_outer; Y_ring[:, 2] = y_outer; Z_ring[:, 2] = 0
    X_ring[:, 3] = x_inner; Y_ring[:, 3] = y_inner; Z_ring[:, 3] = 0
    
    color = "#42A5F5" if i % 2 == 0 else "#90CAF9"
    ax_3d.plot_surface(X_ring, Y_ring, Z_ring, color=color,
                       alpha=0.9, edgecolor="#1565C0", linewidth=0.15, shade=True)

X_circle = x_ring.reshape(-1, 1)
Y_circle = y_ring.reshape(-1, 1)
Z_circle = np.full_like(X_circle, -h_step * 0.05)
ax_3d.plot_surface(X_circle, Y_circle, Z_circle, color="#E3F2FD",
                   alpha=0.7, edgecolor="#1565C0", linewidth=0.3)

ax_3d.set_xlabel("x (mm)", fontsize=11)
ax_3d.set_ylabel("y (mm)", fontsize=11)
ax_3d.set_zlabel("高度 (nm)", fontsize=11)
ax_3d.set_title(
    f"菲涅尔透镜3D结构\n"
    f"(λ=632nm, f=100mm, D={lens.radius*2*1e3:.1f}mm, "
    f"可制造{n_manufacture}环, 刻蚀深度={h_step:.0f}nm)",
    fontsize=13, fontweight="bold"
)
ax_3d.view_init(elev=28, azim=-55)
ax_3d.set_box_aspect([1, 1, 0.12])

plt.savefig("figures/fresnel/菲涅尔透镜3D结构.png", dpi=300, bbox_inches="tight")
plt.show()
