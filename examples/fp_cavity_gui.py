import sys
import os

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.interferometry.fp_cavity import FabryPerotCavity

style_path = os.path.join(BASE_DIR, "config", "optics_style.mplstyle")
if os.path.exists(style_path):
    plt.style.use(style_path)


class FPCavityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F-P腔透射光场分析软件")
        self.root.geometry("1500x950")

        self.R_var = tk.DoubleVar(value=0.95)
        self.h_var = tk.DoubleVar(value=100.0)
        self.n_var = tk.DoubleVar(value=1.0)
        self.theta_var = tk.DoubleVar(value=0.0)

        self.R_list = [0.5, 0.7, 0.9, 0.95, 0.99]
        self.wl_base = tk.DoubleVar(value=632.0)

        self.setup_ui()
        self.update_all_plots()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(main_frame, width=320)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.pack_propagate(False)

        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        param_frame = ttk.LabelFrame(left_panel, text="F-P腔参数设置", padding="10")
        param_frame.pack(fill=tk.X, pady=(0, 10))

        params_info = [
            ("反射率 R:", self.R_var, 0.01, 0.999, "镜面反射率(0~1)，越高精细度越大"),
            ("腔长 h (μm):", self.h_var, 1.0, 10000.0, "两镜面间距，决定FSR"),
            ("折射率 n:", self.n_var, 1.0, 3.0, "腔内介质折射率"),
            ("入射角 θ (°):", self.theta_var, 0.0, 89.0, "光线入射角度"),
        ]

        for i, (label, var, min_val, max_val, tooltip) in enumerate(params_info):
            row_frame = ttk.Frame(param_frame)
            row_frame.pack(fill=tk.X, pady=3)
            ttk.Label(row_frame, text=label, width=14).pack(side=tk.LEFT)
            entry = ttk.Entry(row_frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=(5, 5))

            info_btn = ttk.Button(row_frame, text="?", width=2,
                                  command=lambda t=tooltip: messagebox.showinfo("参数说明", t))
            info_btn.pack(side=tk.LEFT)

            scale = ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                              orient=tk.HORIZONTAL, length=280)
            scale.pack(fill=tk.X, pady=(0, 8))
            var.trace_add("write", lambda *args: self.on_param_change())

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=(5, 10))
        ttk.Button(btn_frame, text="🔄 更新分析", command=self.update_all_plots).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(btn_frame, text="💾 保存图像", command=self.save_images).pack(
            side=tk.LEFT, expand=True, fill=tk.X)

        result_frame = ttk.LabelFrame(left_panel, text="计算结果", padding="10")
        result_frame.pack(fill=tk.X, pady=(0, 10))
        self.result_text = tk.Text(result_frame, height=12, width=38, font=("Consolas", 10),
                                   state=tk.DISABLED, bg="#f5f5f5")
        self.result_text.pack(fill=tk.X)

        R_config_frame = ttk.LabelFrame(left_panel, text="反射率对比列表 R0", padding="10")
        R_config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(R_config_frame, text="输入反射率列表(逗号分隔):").pack(anchor=tk.W)
        self.R_list_entry = ttk.Entry(R_config_frame,
                                       textvariable=tk.StringVar(value=", ".join(map(str, self.R_list))))
        self.R_list_entry.pack(fill=tk.X, pady=(5, 5))
        self.R_list_entry.bind("<Return>", lambda e: self.on_R_list_change())

        wl_frame = ttk.LabelFrame(left_panel, text="光谱范围配置", padding="10")
        wl_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(wl_frame, text="中心波长 λ0 (nm):").pack(anchor=tk.W)
        ttk.Entry(wl_frame, textvariable=self.wl_base, width=10).pack(anchor=tk.W, pady=(0, 5))

        desc_frame = ttk.LabelFrame(left_panel, text="图像说明", padding="10")
        desc_frame.pack(fill=tk.BOTH, expand=True)

        desc_text = """【图1】不同R0的透射率曲线
左图：不同反射率下的透射率光谱，
R越高→峰越尖锐（精细度越高）
右图：精细度F随R的变化关系

【图2】不同光谱范围的透射特性
可见光/窄带/近红外等范围的
透射率曲线，展示共振峰分布"""

        desc_label = ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT,
                               wraplength=290, font=("Microsoft YaHei", 9))
        desc_label.pack(anchor=tk.W)

        plot_frame = ttk.LabelFrame(right_panel, text="透射光场分析", padding="10")
        plot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        self.fig = plt.figure(figsize=(15, 9), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def get_cavity(self):
        return FabryPerotCavity(
            R=self.R_var.get(),
            h=self.h_var.get() * 1e-6,
            n=self.n_var.get(),
            theta=np.radians(self.theta_var.get()),
        )

    def on_param_change(self):
        try:
            self.get_cavity()
            self.update_result_display()
        except Exception:
            pass

    def on_R_list_change(self):
        try:
            val = self.R_list_entry.get()
            self.R_list = [float(x.strip()) for x in val.split(",") if x.strip()]
            self.R_list = sorted(set([r for r in self.R_list if 0 < r < 1]))
            self.update_all_plots()
        except ValueError:
            pass

    def update_result_display(self):
        cavity = self.get_cavity()
        wl0 = self.wl_base.get() * 1e-9

        result = f"╔══════════════════════════╗\n"
        result += f"║   F-P 腔设计参数         ║\n"
        result += f"╠══════════════════════════╣\n"
        result += f"║ 反射率 R     = {cavity.R:.4f}      ║\n"
        result += f"║ 腔长 h       = {cavity.h*1e6:.1f} μm     ║\n"
        result += f"║ 折射率 n     = {cavity.n:.3f}        ║\n"
        result += f"║ 入射角 θ     = {np.degrees(cavity.theta):.1f}°        ║\n"
        result += f"╠══════════════════════════╣\n"
        result += f"║ 精细度 F     = {cavity.finesse():.2f}      ║\n"
        result += f"║ FSR@{wl0*1e9:.0f}nm  = {cavity.fsr(wl0)*1e9:.3f} nm   ║\n"
        result += f"║ FWHM@{wl0*1e9:.0f}nm = {cavity.fwhm(wl0)*1e6:.4f} μm  ║\n"
        result += f"║ Q值@{wl0*1e9:.0f}nm  = {cavity.q_factor(wl0):.0f}       ║\n"

        res_wl = cavity.resonance_wavelengths(wl0 * 0.95, wl0 * 1.05)
        if len(res_wl) > 0:
            nearest = res_wl[np.argmin(np.abs(res_wl - wl0))]
            result += f"╠══════════════════════════╣\n"
            result += f"║ 最近共振波长 ≈ {nearest*1e9:.3f} nm   ║\n"
        result += f"╚══════════════════════════╝"

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)

    def update_all_plots(self):
        cavity = self.get_cavity()
        self.fig.clear()

        wl_range = np.linspace(600e-9, 660e-9, 5000)
        colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(self.R_list)))
        results = cavity.plot_transmission_comparison(self.R_list, wl_range)

        ax1 = self.fig.add_subplot(3, 2, (1, 2))
        for R, color in zip(self.R_list, colors):
            T = results[R]
            ax1.plot(wl_range * 1e9, T, label=f"R={R}", color=color, linewidth=1.5)
        ax1.set_xlabel("波长 (nm)")
        ax1.set_ylabel("透射率 T")
        ax1.set_title(f"不同反射率R0的透射率曲线 (n={cavity.n}, h={cavity.h*1e6:.0f}μm, θ={np.degrees(cavity.theta):.1f}°)",
                      fontsize=11)
        ax1.legend(fontsize=8, loc='upper right')
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, alpha=0.3)

        ax2 = self.fig.add_subplot(3, 2, 3)
        R_sweep = np.linspace(0.1, 0.999, 200)
        finesse_values = np.pi * np.sqrt(R_sweep) / (1 - R_sweep)
        ax2.semilogy(R_sweep, finesse_values, "b-", linewidth=2)
        for R in self.R_list:
            F = np.pi * np.sqrt(R) / (1 - R)
            ax2.plot(R, F, "ro", markersize=8)
            ax2.annotate(f"F={F:.1f}", xy=(R, F), fontsize=8,
                         xytext=(R + 0.02, F * 1.3))
        ax2.set_xlabel("反射率 R0")
        ax2.set_ylabel("精细度 F")
        ax2.set_title("精细度与反射率的关系\nF = π√R/(1-R)", fontsize=11)
        ax2.grid(True, alpha=0.3)

        spectral_ranges = [
            (400e-9, 800e-9, "可见光范围 (400-800nm)"),
            (1000e-9, 2000e-9, "近红外范围 (1000-2000nm)"),
        ]
        wl0 = self.wl_base.get() * 1e-9
        spectral_ranges.insert(1, (wl0 * 0.98, wl0 * 1.02,
                                    f"窄带范围 ({wl0*1e9*0.98:.0f}-{wl0*1e9*1.02:.0f}nm)"))

        spec_positions = [4, 5, (6, 7)]
        for idx, (lam_min, lam_max, title) in enumerate(spectral_ranges):
            ax = self.fig.add_subplot(3, 2, spec_positions[idx])
            wl = np.linspace(lam_min, lam_max, 3000)
            T = cavity.transmission(wl)
            ax.plot(wl * 1e9, T, 'b-', linewidth=1.2)
            ax.fill_between(wl * 1e9, T, alpha=0.15, color='blue')
            ax.set_xlabel("波长 (nm)")
            ax.set_ylabel("透射率 T")
            ax.set_title(title, fontsize=11)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, alpha=0.3)

            if idx == 0:
                res_wl = cavity.resonance_wavelengths(lam_min, lam_max)
                for rw in res_wl[::max(1, len(res_wl)//6)]:
                    if lam_min <= rw <= lam_max:
                        ax.axvline(rw * 1e9, color='red', linestyle='--', alpha=0.5, linewidth=0.8)

        self.fig.suptitle(
            f"Fabry-Perot 腔透射光场分析 | R={cavity.R} | F={cavity.finesse():.1f}",
            fontsize=14, fontweight='bold')
        self.canvas.draw()
        self.update_result_display()

    def save_images(self):
        filepath = filedialog.asksaveasfilename(
            title="保存图像",
            initialfile="fp_cavity_analysis.png",
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("PDF文档", "*.pdf"), ("所有文件", "*.*")]
        )
        if filepath:
            self.fig.savefig(filepath, dpi=300, bbox_inches="tight")
            messagebox.showinfo("保存成功", f"图像已保存到:\n{filepath}")


def main():
    root = tk.Tk()
    app = FPCavityGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
