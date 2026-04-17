import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.wavefront.zernike import zernike_grid, NOLL_TO_NM, ABERRATION_NAMES

plt.style.use("config/optics_style.mplstyle")


def plot_zernike_2d(j: int, resolution: int = 256, save_path: str | None = None) -> None:
    """绘制单个Zernike多项式的2D热力图"""
    Z = zernike_grid(j, resolution)
    n, m = NOLL_TO_NM[j - 1]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(
        Z,
        cmap="RdBu_r",
        extent=[-1, 1, -1, 1],
        vmin=-1,
        vmax=1,
    )
    ax.set_title(f"Z{j} {ABERRATION_NAMES[j-1]}\n(n={n}, m={m})", fontsize=12)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")
    plt.colorbar(im, ax=ax, label="Zernike值")
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_zernike_3d(j: int, resolution: int = 256, save_path: str | None = None) -> None:
    """绘制单个Zernike多项式的3D曲面图"""
    Z = zernike_grid(j, resolution)
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(x, y)
    mask = np.isnan(Z)
    Z_masked = np.ma.array(Z, mask=mask)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z_masked, cmap="RdBu_r", vmin=-1, vmax=1, alpha=0.9)
    n, m = NOLL_TO_NM[j - 1]
    ax.set_title(f"Z{j} {ABERRATION_NAMES[j-1]} (n={n}, m={m})", fontsize=12)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Zernike值")
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="Zernike值")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def plot_zernike_combined(j: int, resolution: int = 256, save_path: str | None = None) -> None:
    """同时绘制2D热力图和3D曲面图"""
    Z = zernike_grid(j, resolution)
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(x, y)
    n, m = NOLL_TO_NM[j - 1]
    
    fig = plt.figure(figsize=(16, 6))
    
    # 2D热力图
    ax1 = fig.add_subplot(121)
    im = ax1.imshow(
        Z,
        cmap="RdBu_r",
        extent=[-1, 1, -1, 1],
        vmin=-1,
        vmax=1,
    )
    ax1.set_title(f"Z{j} {ABERRATION_NAMES[j-1]} (n={n}, m={m})\n2D热力图", fontsize=12)
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_aspect("equal")
    plt.colorbar(im, ax=ax1, label="Zernike值")
    
    # 3D曲面图
    ax2 = fig.add_subplot(122, projection="3d")
    mask = np.isnan(Z)
    Z_masked = np.ma.array(Z, mask=mask)
    surf = ax2.plot_surface(X, Y, Z_masked, cmap="RdBu_r", vmin=-1, vmax=1, alpha=0.9)
    ax2.set_title(f"3D曲面图", fontsize=12)
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.set_zlabel("Zernike值")
    
    # 不使用tight_layout，因为样式文件已设置constrained_layout
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


def print_zernike_list():
    """打印所有可用的Zernike多项式列表"""
    print("=" * 60)
    print("Zernike 多项式列表 (Noll索引)")
    print("=" * 60)
    for i, (name, (n, m)) in enumerate(zip(ABERRATION_NAMES, NOLL_TO_NM)):
        print(f"  Z{i+1:2d}: {name:20s} (n={n}, m={m:+d})")
    print("=" * 60)


def interactive_menu():
    """交互式菜单"""
    os.makedirs("figures/wavefront", exist_ok=True)
    
    while True:
        print("\n" + "=" * 60)
        print("Zernike 多项式可视化工具")
        print("=" * 60)
        print("1. 显示所有36项的2D概览图")
        print("2. 显示指定项的2D+3D组合图")
        print("3. 查看Zernike多项式列表")
        print("0. 退出")
        print("=" * 60)
        
        choice = input("请选择功能 (0-3): ").strip()
        
        if choice == "0":
            print("退出程序")
            break
            
        elif choice == "1":
            from src.wavefront.zernike import plot_zernike_modes
            print("正在生成36项Zernike多项式概览图...")
            plot_zernike_modes(noll_max=36, resolution=256, 
                             save_path="figures/wavefront/zernike_36.png")
                
        elif choice == "2":
            try:
                j = int(input("请输入Zernike项编号 (1-36): ").strip())
                if 1 <= j <= 36:
                    print(f"正在生成 Z{j} {ABERRATION_NAMES[j-1]} 的组合图...")
                    plot_zernike_combined(j, save_path=f"figures/wavefront/zernike_combined_Z{j}.png")
                else:
                    print("错误：编号必须在1-36之间")
            except ValueError:
                print("错误：请输入有效的整数")
                
        elif choice == "3":
            print_zernike_list()
            
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        import argparse
        parser = argparse.ArgumentParser(description="Zernike多项式可视化工具")
        parser.add_argument("--mode", choices=["2d", "3d", "combined", "all"], 
                          default="all", help="显示模式")
        parser.add_argument("--j", type=int, nargs="+", 
                          help="Zernike项编号 (1-36)，可指定多个")
        parser.add_argument("--list", action="store_true", 
                          help="显示所有Zernike多项式列表")
        args = parser.parse_args()
        
        os.makedirs("figures/wavefront", exist_ok=True)
        
        if args.list:
            print_zernike_list()
        elif args.j:
            for j in args.j:
                if 1 <= j <= 36:
                    if args.mode == "2d":
                        plot_zernike_2d(j, save_path=f"figures/wavefront/zernike_2d_Z{j}.png")
                    elif args.mode == "3d":
                        plot_zernike_3d(j, save_path=f"figures/wavefront/zernike_3d_Z{j}.png")
                    elif args.mode == "combined":
                        plot_zernike_combined(j, save_path=f"figures/wavefront/zernike_combined_Z{j}.png")
                else:
                    print(f"警告：Z{j} 超出范围 (1-36)，已跳过")
        else:
            # 默认显示所有36项概览
            from src.wavefront.zernike import plot_zernike_modes
            plot_zernike_modes(noll_max=36, resolution=256, 
                             save_path="figures/wavefront/zernike_36.png")
    else:
        # 交互式模式
        interactive_menu()
