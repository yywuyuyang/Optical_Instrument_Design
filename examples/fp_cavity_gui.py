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
        self.root.geometry("1200x800")

        self.R_var = tk.DoubleVar(value=0.95)
        self.h_var = tk.DoubleVar(value=100.0)
        self.n_var = tk.DoubleVar(value=1.0)
        self.theta_var = tk.DoubleVar(value=0.0)

        self.R_list = [0.5, 0.7, 0.9, 0.95, 0.99]
        self.wl_base = tk.DoubleVar(value=632.0)

        self.figures = {}
        self.canvases = {}
        self.R_checkboxes = {}

        self.setup_ui()
        self.update_all_plots()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.pack_propagate(False)

        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        param_frame = ttk.LabelFrame(left_panel, text="F-P腔参数设置", padding="8")
        param_frame.pack(fill=tk.X, pady=(0, 8))

        params_info = [
            ("反射率 R:", self.R_var, 0.01, 0.999, "镜面反射率(0~1)，越高精细度越大"),
            ("腔长 h (um):", self.h_var, 1.0, 10000.0, "两镜面间距，决定FSR"),
            ("折射率 n:", self.n_var, 1.0, 3.0, "腔内介质折射率"),
            ("入射角 theta (deg):", self.theta_var, 0.0, 89.0, "光线入射角度"),
        ]

        for i, (label, var, min_val, max_val, tooltip) in enumerate(params_info):
            row_frame = ttk.Frame(param_frame)
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=label, width=16).pack(side=tk.LEFT)
            entry = ttk.Entry(row_frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=(5, 5))

            info_btn = ttk.Button(row_frame, text="?", width=2,
                                  command=lambda t=tooltip: messagebox.showinfo("参数说明", t))
            info_btn.pack(side=tk.LEFT)

            scale = ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                              orient=tk.HORIZONTAL, length=260)
            scale.pack(fill=tk.X, pady=(0, 5))
            var.trace_add("write", lambda *args, v=var: self.on_param_change())

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=(5, 8))
        ttk.Button(btn_frame, text="更新分析", command=self.update_all_plots).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(btn_frame, text="保存当前图像", command=self.save_current_image).pack(
            side=tk.LEFT, expand=True, fill=tk.X)

        result_frame = ttk.LabelFrame(left_panel, text="计算结果", padding="8")
        result_frame.pack(fill=tk.X, pady=(0, 8))
        self.result_text = tk.Text(result_frame, height=10, width=35, font=("Consolas", 9),
                                   state=tk.DISABLED, bg="#f5f5f5")
        self.result_text.pack(fill=tk.X)

        R_config_frame = ttk.LabelFrame(left_panel, text="反射率对比列表 R0", padding="8")
        R_config_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(R_config_frame, text="勾选要对比的反射率:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=(0, 5))

        R_presets = [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.92, 0.95, 0.97, 0.99]
        for R_val in R_presets:
            var = tk.BooleanVar(value=R_val in self.R_list)
            cb = ttk.Checkbutton(R_config_frame, text=f"R = {R_val:.2f}", variable=var,
                                 command=self.on_R_list_change)
            cb.pack(anchor=tk.W, pady=1)
            self.R_checkboxes[R_val] = var

        guide_text = """说明:
勾选多个R值后，查看右侧
"不同R0透射率曲线"标签页，
可对比不同反射率下的透射
光谱。R值越高，透射峰越
尖锐，精细度越大。"""
        guide_label = ttk.Label(R_config_frame, text=guide_text, justify=tk.LEFT,
                                wraplength=260, font=("Microsoft YaHei", 8),
                                foreground="#666666")
        guide_label.pack(anchor=tk.W, pady=(8, 0))

        wl_frame = ttk.LabelFrame(left_panel, text="光谱范围配置", padding="8")
        wl_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(wl_frame, text="中心波长 lambda0 (nm):").pack(anchor=tk.W)
        ttk.Entry(wl_frame, textvariable=self.wl_base, width=10).pack(anchor=tk.W, pady=(3, 0))

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        tab_configs = [
            ("不同R0透射率曲线", "显示不同反射率R0下的透射率光谱曲线。\n反射率越高，透射峰越尖锐，精细度越大。"),
            ("精细度与反射率", "显示精细度F与反射率R的关系：F = π√R/(1-R)。\n反射率接近1时，精细度急剧增加。"),
            ("可见光范围", "显示可见光范围(400-800nm)内的透射特性。\n红色虚线标记共振波长位置。"),
            ("窄带范围", "显示中心波长附近±2%窄带范围内的透射特性。\n用于观察单峰透射行为。"),
            ("近红外范围", "显示近红外范围(1000-2000nm)内的透射特性。\n波长越长，自由光谱范围(FSR)越小。"),
        ]

        for name, desc in tab_configs:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=name)
            
            fig_frame = ttk.Frame(tab_frame)
            fig_frame.pack(fill=tk.BOTH, expand=True)
            
            self.figures[name] = plt.figure(figsize=(8, 6), constrained_layout=True)
            self.canvases[name] = FigureCanvasTkAgg(self.figures[name], master=fig_frame)
            self.canvases[name].get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            desc_label = ttk.Label(tab_frame, text=desc, justify=tk.LEFT,
                                   wraplength=700, font=("Microsoft YaHei", 9),
                                   foreground="#555555")
            desc_label.pack(fill=tk.X, padx=10, pady=(5, 8))

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
            self.update_all_plots()
        except Exception:
            pass

    def on_R_list_change(self):
        self.R_list = sorted([R for R, var in self.R_checkboxes.items() if var.get()])
        if len(self.R_list) == 0:
            self.R_list = [0.95]
            self.R_checkboxes[0.95].set(True)
        self.update_all_plots()

    def update_result_display(self):
        cavity = self.get_cavity()
        wl0 = self.wl_base.get() * 1e-9

        result = f"F-P 腔设计参数\n"
        result += f"=" * 25 + "\n"
        result += f"反射率 R     = {cavity.R:.4f}\n"
        result += f"腔长 h       = {cavity.h*1e6:.1f} um\n"
        result += f"折射率 n     = {cavity.n:.3f}\n"
        result += f"入射角 theta = {np.degrees(cavity.theta):.1f} deg\n"
        result += f"-" * 25 + "\n"
        result += f"精细度 F     = {cavity.finesse():.2f}\n"
        result += f"FSR@{wl0*1e9:.0f}nm  = {cavity.fsr(wl0)*1e9:.3f} nm\n"
        result += f"FWHM@{wl0*1e9:.0f}nm = {cavity.fwhm(wl0)*1e6:.4f} um\n"
        result += f"Q值@{wl0*1e9:.0f}nm  = {cavity.q_factor(wl0):.0f}\n"

        res_wl = cavity.resonance_wavelengths(wl0 * 0.95, wl0 * 1.05)
        if len(res_wl) > 0:
            nearest = res_wl[np.argmin(np.abs(res_wl - wl0))]
            result += f"-" * 25 + "\n"
            result += f"最近共振波长 = {nearest*1e9:.3f} nm\n"

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)

    def update_all_plots(self):
        cavity = self.get_cavity()
        wl0 = self.wl_base.get() * 1e-9

        wl_range = np.linspace(600e-9, 660e-9, 5000)
        colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(self.R_list)))
        results = cavity.plot_transmission_comparison(self.R_list, wl_range)

        fig1 = self.figures["不同R0透射率曲线"]
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        for R, color in zip(self.R_list, colors):
            T = results[R]
            ax1.plot(wl_range * 1e9, T, label=f"R={R}", color=color, linewidth=1.5)
        ax1.set_xlabel("波长 (nm)")
        ax1.set_ylabel("透射率 T")
        ax1.set_title(f"不同反射率R0的透射率曲线\n(n={cavity.n}, h={cavity.h*1e6:.0f}um, theta={np.degrees(cavity.theta):.1f}deg)",
                      fontsize=12)
        ax1.legend(fontsize=9, loc='upper right')
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, alpha=0.3)
        self.canvases["不同R0透射率曲线"].draw()

        fig2 = self.figures["精细度与反射率"]
        fig2.clear()
        ax2 = fig2.add_subplot(111)
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
        ax2.set_title("精细度与反射率的关系\nF = pi*sqrt(R)/(1-R)", fontsize=12)
        ax2.grid(True, alpha=0.3)
        self.canvases["精细度与反射率"].draw()

        spectral_ranges = [
            ("可见光范围", 400e-9, 800e-9),
            ("窄带范围", wl0 * 0.98, wl0 * 1.02),
            ("近红外范围", 1000e-9, 2000e-9),
        ]

        for name, lam_min, lam_max in spectral_ranges:
            fig = self.figures[name]
            fig.clear()
            ax = fig.add_subplot(111)
            wl = np.linspace(lam_min, lam_max, 3000)
            T = cavity.transmission(wl)
            ax.plot(wl * 1e9, T, 'b-', linewidth=1.2)
            ax.fill_between(wl * 1e9, T, alpha=0.15, color='blue')
            ax.set_xlabel("波长 (nm)")
            ax.set_ylabel("透射率 T")
            ax.set_title(f"{name} ({lam_min*1e9:.0f}-{lam_max*1e9:.0f}nm)", fontsize=12)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, alpha=0.3)

            if name == "可见光范围":
                res_wl = cavity.resonance_wavelengths(lam_min, lam_max)
                for rw in res_wl[::max(1, len(res_wl)//8)]:
                    if lam_min <= rw <= lam_max:
                        ax.axvline(rw * 1e9, color='red', linestyle='--', alpha=0.5, linewidth=0.8)

            self.canvases[name].draw()

        self.update_result_display()

    def save_current_image(self):
        current_tab = self.notebook.tab(self.notebook.select(), "text")

        filepath = filedialog.asksaveasfilename(
            title="保存图像",
            initialfile=f"fp_cavity_{current_tab}.png",
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("PDF文档", "*.pdf"), ("所有文件", "*.*")]
        )
        if filepath:
            self.figures[current_tab].savefig(filepath, dpi=300, bbox_inches="tight")
            messagebox.showinfo("保存成功", f"图像已保存到:\n{filepath}")


def main():
    root = tk.Tk()
    app = FPCavityGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
