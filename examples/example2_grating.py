import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.grating.analysis import DiffractionGrating
from src.grating.visualization import plot_diffraction_angles, plot_efficiency
from scipy.special import jv

plt.style.use("config/optics_style.mplstyle")

def enhanced_grating_analysis():
    """增强的衍射光栅分析：展示完整的参数变化曲线"""
    
    # 基础光栅参数
    grating = DiffractionGrating(
        period=2e-6,
        wavelength=632e-9,
        incidence_angle=0.0,
        max_order=5,
    )

    print("=" * 60)
    print("衍射光栅参数分析")
    print("=" * 60)
    
    print(f"\n基本参数:")
    print(f"  光栅周期: {grating.period*1e6:.1f} μm")
    print(f"  波长: {grating.wavelength*1e9:.0f} nm")
    print(f"  入射角: {np.degrees(grating.incidence_angle):.2f}°")
    print(f"  最大级次: ±{grating.max_order}")

    # 计算所有衍射角
    angles = grating.all_diffraction_angles()
    print(f"\n衍射角计算结果:")
    for m, angle in angles.items():
        if angle is not None:
            print(f"  m={m:+d}: {np.degrees(angle):.2f}°")
        else:
            print(f"  m={m:+d}: 无传播级次")

    # 创建输出目录
    os.makedirs("figures/grating", exist_ok=True)

    # 1. 基本可视化
    print(f"\n生成基本可视化图表...")
    plot_diffraction_angles(grating, save_path="figures/grating/衍射角分布.png")
    plot_efficiency(grating, phase_depth=2.0, duty_cycle=0.5, save_path="figures/grating/衍射效率.png")

    # 2. 增强分析：衍射效率随参数变化
    print(f"\n生成衍射效率参数扫描图表...")
    plot_efficiency_与_parameters(grating)

    # 3. 衍射角参数扫描分析
    print(f"\n生成衍射角参数扫描图表...")
    plot_angle_parameter_scans(grating)

    print("\n" + "=" * 60)
    print("分析完成！所有图表已保存到 figures/grating/ 目录")
    print("=" * 60)


def plot_efficiency_与_parameters(grating):
    """绘制衍射效率随参数变化的曲线"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), constrained_layout=True)
    
    # 衍射效率随相位深度变化
    phase_depths = np.linspace(0, 4*np.pi, 200)
    orders = [0, 1, 2, -1, -2]
    
    for m in orders:
        efficiencies = [float(jv(m, d/2)**2) for d in phase_depths]
        axes[0,0].plot(phase_depths/np.pi, efficiencies, label=f'm={m}', linewidth=2)
    
    axes[0,0].set_xlabel('相位深度 (π rad)')
    axes[0,0].set_ylabel('衍射效率')
    axes[0,0].set_title('衍射效率与相位深度 (正弦相位光栅)')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)

    # 衍射效率随占空比变化
    duty_cycles = np.linspace(0.1, 0.9, 100)
    for m in [0, 1, 2]:
        efficiencies = []
        for dc in duty_cycles:
            if m == 0:
                eff = dc**2
            else:
                sinc_arg = np.pi * m * dc
                eff = (dc * np.sin(sinc_arg) / sinc_arg)**2
            efficiencies.append(eff)
        axes[0,1].plot(duty_cycles, efficiencies, label=f'm={m}', linewidth=2)
    
    axes[0,1].set_xlabel('占空比')
    axes[0,1].set_ylabel('衍射效率')
    axes[0,1].set_title('衍射效率与占空比 (振幅型光栅)')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)

    # 衍射效率随波长变化
    wavelengths = np.linspace(400e-9, 800e-9, 200)
    for m in [1, 2, 3]:
        efficiencies = []
        for lam in wavelengths:
            # 简化的效率模型：考虑波长相关的相位深度
            phase_depth = 2*np.pi * (1.5-1) * 1e-6 / lam  # 假设1μm厚，折射率差0.5
            eff = float(jv(m, phase_depth/2)**2)
            efficiencies.append(eff)
        axes[0,2].plot(wavelengths*1e9, efficiencies, label=f'm={m}', linewidth=2)
    
    axes[0,2].set_xlabel('波长 (nm)')
    axes[0,2].set_ylabel('衍射效率')
    axes[0,2].set_title('衍射效率与波长 (相位光栅)')
    axes[0,2].legend()
    axes[0,2].grid(True, alpha=0.3)

    # 高级分析：不同参数组合下的效率分布
    phase_range = np.linspace(0, 2*np.pi, 50)
    duty_range = np.linspace(0.2, 0.8, 50)
    
    # m=1级效率热图
    eff_map = np.zeros((len(phase_range), len(duty_range)))
    for i, phase in enumerate(phase_range):
        for j, duty in enumerate(duty_range):
            eff_map[i,j] = grating.efficiency_rect_phase(1, duty, phase)
    
    im = axes[1,0].imshow(eff_map, extent=[0.2, 0.8, 0, 2*np.pi], aspect='auto', origin='lower', cmap='viridis')
    axes[1,0].set_xlabel('占空比')
    axes[1,0].set_ylabel('相位深度 (rad)')
    axes[1,0].set_title('m=1级效率热图 (矩形相位光栅)')
    fig.colorbar(im, ax=axes[1,0])

    # 不同级次效率对比
    orders_compare = list(range(-3, 4))
    phase_val = np.pi
    efficiencies = [grating.efficiency_sine_phase(m, phase_val) for m in orders_compare]
    
    axes[1,1].bar(orders_compare, efficiencies, color='steelblue', alpha=0.7)
    axes[1,1].set_xlabel('衍射级次')
    axes[1,1].set_ylabel('衍射效率')
    axes[1,1].set_title(f'不同级次效率对比 (相位深度={phase_val/np.pi:.1f}π)')
    axes[1,1].grid(True, alpha=0.3)

    # 效率优化分析
    optimal_phase = 1.84  # 第一个贝塞尔函数最大值对应的参数
    orders_opt = list(range(-5, 6))
    efficiencies_opt = [grating.efficiency_sine_phase(m, optimal_phase) for m in orders_opt]
    
    axes[1,2].bar(orders_opt, efficiencies_opt, color='coral', alpha=0.7)
    axes[1,2].set_xlabel('衍射级次')
    axes[1,2].set_ylabel('衍射效率')
    axes[1,2].set_title(f'优化相位深度效率分布 (φ={optimal_phase:.2f}rad)')
    axes[1,2].grid(True, alpha=0.3)

    plt.savefig("figures/grating/衍射效率参数扫描.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_angle_parameter_scans(grating):
    """绘制衍射角参数扫描分析"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12), constrained_layout=True)
    
    # 1. 入射角扫描
    theta_range = np.linspace(-60, 60, 200)  # 度
    theta_rad = np.radians(theta_range)
    
    for m in [1, 2, 3, -1, -2, -3]:
        valid_theta, valid_angles = [], []
        for theta_i in theta_rad:
            sin_val = m * grating.wavelength / grating.period + np.sin(theta_i)
            if np.abs(sin_val) <= 1:
                valid_theta.append(np.degrees(theta_i))
                valid_angles.append(np.degrees(np.arcsin(sin_val)))
        if valid_theta:
            axes[0,0].plot(valid_theta, valid_angles, label=f'm={m}', linewidth=2)
    
    axes[0,0].set_xlabel('入射角 (°)')
    axes[0,0].set_ylabel('衍射角 (°)')
    axes[0,0].set_title('衍射角与入射角')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)

    # 2. 波长扫描
    wavelength_range = np.linspace(400e-9, 800e-9, 200)
    
    for m in [1, 2, 3]:
        valid_wl, valid_angles = [], []
        for lam in wavelength_range:
            sin_val = m * lam / grating.period + np.sin(grating.incidence_angle)
            if np.abs(sin_val) <= 1:
                valid_wl.append(lam * 1e9)
                valid_angles.append(np.degrees(np.arcsin(sin_val)))
        if valid_wl:
            axes[0,1].plot(valid_wl, valid_angles, label=f'm={m}', linewidth=2)
    
    axes[0,1].set_xlabel('波长 (nm)')
    axes[0,1].set_ylabel('衍射角 (°)')
    axes[0,1].set_title('衍射角与波长')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)

    # 3. 光栅周期扫描
    period_range = np.linspace(0.5e-6, 5e-6, 200)
    
    for m in [1, 2, 3]:
        valid_period, valid_angles = [], []
        for d in period_range:
            sin_val = m * grating.wavelength / d + np.sin(grating.incidence_angle)
            if np.abs(sin_val) <= 1:
                valid_period.append(d * 1e6)
                valid_angles.append(np.degrees(np.arcsin(sin_val)))
        if valid_period:
            axes[1,0].plot(valid_period, valid_angles, label=f'm={m}', linewidth=2)
    
    axes[1,0].set_xlabel('光栅周期 (μm)')
    axes[1,0].set_ylabel('衍射角 (°)')
    axes[1,0].set_title('衍射角与光栅周期')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)

    # 4. 高级分析：衍射角等高线图
    d_values = np.linspace(1e-6, 3e-6, 50)
    lam_values = np.linspace(400e-9, 700e-9, 50)
    D, L = np.meshgrid(d_values, lam_values)
    
    # 计算m=1级衍射角
    theta_diff = np.zeros_like(D)
    for i in range(len(lam_values)):
        for j in range(len(d_values)):
            sin_val = 1 * lam_values[i] / d_values[j] + np.sin(grating.incidence_angle)
            if np.abs(sin_val) <= 1:
                theta_diff[i,j] = np.degrees(np.arcsin(sin_val))
            else:
                theta_diff[i,j] = np.nan
    
    contour = axes[1,1].contourf(D*1e6, L*1e9, theta_diff, levels=20, cmap='viridis')
    axes[1,1].set_xlabel('光栅周期 (μm)')
    axes[1,1].set_ylabel('波长 (nm)')
    axes[1,1].set_title('m=1级衍射角等高线图')
    fig.colorbar(contour, ax=axes[1,1], label='衍射角 (°)')

    plt.savefig("figures/grating/衍射角参数扫描.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    enhanced_grating_analysis()
