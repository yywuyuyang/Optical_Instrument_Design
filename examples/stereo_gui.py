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
from src.imaging.stereo import StereoRangingSystem
from src.imaging.visualization import plot_optical_layout, plot_error_analysis

style_path = os.path.join(BASE_DIR, "config", "optics_style.mplstyle")
if os.path.exists(style_path):
    plt.style.use(style_path)


class StereoRangingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("双目测距系统分析 - Stereo Ranging Analyzer")
        self.root.geometry("1400x900")

        # 参数变量
        self.baseline_var = tk.DoubleVar(value=65.0)  # mm
        self.focal_length_var = tk.DoubleVar(value=8.0)  # mm
        self.pixel_size_var = tk.DoubleVar(value=3.45)  # μm
        self.image_width_var = tk.IntVar(value=1920)
        self.image_height_var = tk.IntVar(value=1080)

        self.setup_ui()
        self.update_analysis()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # 左侧控制面板
        left_panel = ttk.Frame(main_frame, width=350)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.pack_propagate(False)

        # 右侧显示面板
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        self.setup_control_panel(left_panel)
        self.setup_display_area(right_panel)

    def setup_control_panel(self, parent):
        # 基本参数设置
        param_frame = ttk.LabelFrame(parent, text="系统参数设置", padding="8")
        param_frame.pack(fill=tk.X, pady=(0, 8))

        params = [
            ("基线长度 (mm):", self.baseline_var, 10.0, 200.0, 
             "双相机之间的距离，影响测距精度和范围"),
            ("焦距 (mm):", self.focal_length_var, 1.0, 50.0,
             "相机焦距，影响视场角和测距精度"),
            ("像素尺寸 (μm):", self.pixel_size_var, 1.0, 10.0,
             "像素大小，影响测距分辨率"),
            ("图像宽度 (px):", self.image_width_var, 640, 4096,
             "相机水平分辨率"),
            ("图像高度 (px):", self.image_height_var, 480, 2160,
             "相机垂直分辨率"),
        ]

        for i, (label, var, min_val, max_val, tooltip) in enumerate(params):
            row_frame = ttk.Frame(param_frame)
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=label, width=18).pack(side=tk.LEFT)
            entry = ttk.Entry(row_frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=(5, 5))

            info_btn = ttk.Button(row_frame, text="?", width=2,
                                  command=lambda t=tooltip: messagebox.showinfo("参数说明", t))
            info_btn.pack(side=tk.LEFT)

            if isinstance(var, tk.DoubleVar):
                scale = ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                                  orient=tk.HORIZONTAL, length=320)
                scale.pack(fill=tk.X, pady=(0, 5))
                var.trace_add("write", lambda *args: self.on_param_change())
            else:
                var.trace_add("write", lambda *args: self.on_param_change())

        # 控制按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(5, 8))
        ttk.Button(btn_frame, text="更新分析", command=self.update_analysis).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(btn_frame, text="保存图像", command=self.save_image).pack(
            side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="重置参数", command=self.reset_params).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # 计算结果显示
        result_frame = ttk.LabelFrame(parent, text="系统参数计算", padding="8")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.result_text = tk.Text(result_frame, height=15, width=40, font=("Consolas", 9),
                                   state=tk.DISABLED, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 测距原理说明
        desc_frame = ttk.LabelFrame(parent, text="测距原理", padding="8")
        desc_frame.pack(fill=tk.X)

        desc_text = """【测距原理】
基于三角测量原理：
- 基线长度 B：两相机间距
- 焦距 f：相机焦距
- 视差 d：同一目标在两像面上的像素差

公式：Z = (B × f) / d

【参数影响】
- 基线越长：测距范围越大，精度越高
- 焦距越长：视场角越小，测距精度越高
- 像素尺寸越小：测距分辨率越高"""

        desc_label = ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT,
                               wraplength=320, font=("Microsoft YaHei", 9))
        desc_label.pack(anchor=tk.W)

    def setup_display_area(self, parent):
        display_frame = ttk.LabelFrame(parent, text="双目测距可视化分析", padding="10")
        display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)

        # 创建多标签页
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页1：光路布局
        layout_frame = ttk.Frame(self.notebook)
        layout_frame.columnconfigure(0, weight=1)
        layout_frame.rowconfigure(0, weight=1)
        self.notebook.add(layout_frame, text="光路布局")
        
        self.layout_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.layout_canvas = FigureCanvasTkAgg(self.layout_fig, master=layout_frame)
        self.layout_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页2：误差分析
        error_frame = ttk.Frame(self.notebook)
        error_frame.columnconfigure(0, weight=1)
        error_frame.rowconfigure(0, weight=1)
        self.notebook.add(error_frame, text="误差分析")
        
        self.error_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.error_canvas = FigureCanvasTkAgg(self.error_fig, master=error_frame)
        self.error_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页3：参数关系
        param_frame = ttk.Frame(self.notebook)
        param_frame.columnconfigure(0, weight=1)
        param_frame.rowconfigure(0, weight=1)
        self.notebook.add(param_frame, text="参数关系")
        
        self.param_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.param_canvas = FigureCanvasTkAgg(self.param_fig, master=param_frame)
        self.param_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def get_system(self):
        return StereoRangingSystem(
            baseline=self.baseline_var.get() * 1e-3,  # 转换为米
            focal_length=self.focal_length_var.get() * 1e-3,  # 转换为米
            pixel_size=self.pixel_size_var.get() * 1e-6,  # 转换为米
            image_width=self.image_width_var.get(),
            image_height=self.image_height_var.get(),
        )

    def on_param_change(self):
        try:
            self.get_system()
            self.update_analysis()
        except Exception:
            pass

    def reset_params(self):
        self.baseline_var.set(65.0)
        self.focal_length_var.set(8.0)
        self.pixel_size_var.set(3.45)
        self.image_width_var.set(1920)
        self.image_height_var.set(1080)
        self.update_analysis()

    def update_result_display(self, system):
        result = f"═══ 双目测距系统参数 ═══\n"
        result += f"基线长度: {system.baseline*1e3:.1f} mm\n"
        result += f"焦距:     {system.focal_length*1e3:.1f} mm\n"
        result += f"像素尺寸: {system.pixel_size*1e6:.2f} μm\n"
        result += f"分辨率:   {system.image_width}x{system.image_height}\n"
        result += f"水平视场角: {np.degrees(system.fov_horizontal()):.1f}°\n"
        result += f"垂直视场角: {np.degrees(system.fov_vertical()):.1f}°\n"
        result += f"最小测距:   {system.min_measurable_distance():.2f} m\n"
        result += f"最大测距:   {system.max_measurable_distance():.2f} m\n\n"

        result += f"═══ 视差与误差分析 ═══\n"
        for d in [1, 2, 5, 10, 20]:
            disp = system.disparity_from_distance(d)
            err = system.range_error(d)
            result += f"@ {d}m: 视差={disp:.1f}px, 误差={err:.3f}m ({err/d*100:.1f}%)\n"

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)

    def update_analysis(self):
        system = self.get_system()
        
        # 更新标签页1：光路布局
        self.layout_fig.clear()
        ax1 = self.layout_fig.add_subplot(111)
        plot_optical_layout(system, target_distance=5.0, save_path=None, ax=ax1)
        self.layout_fig.suptitle(f'双目测距光路布局\n基线长度: {system.baseline*1e3:.1f}mm, 焦距: {system.focal_length*1e3:.1f}mm', fontsize=12, fontweight='bold')
        self.layout_canvas.draw()

        # 更新标签页2：误差分析
        self.error_fig.clear()
        ax2 = self.error_fig.add_subplot(111)
        plot_error_analysis(system, save_path=None, ax=ax2)
        self.error_fig.suptitle('测距误差分析', fontsize=12, fontweight='bold')
        self.error_canvas.draw()

        # 更新标签页3：参数关系
        self.param_fig.clear()
        gs = self.param_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. 基线长度与测距范围
        ax3 = self.param_fig.add_subplot(gs[0, 0])
        baseline_range = np.linspace(10, 200, 50) * 1e-3  # 转换为米
        min_dist = []
        max_dist = []
        for b in baseline_range:
            temp_system = StereoRangingSystem(
                baseline=b,
                focal_length=system.focal_length,
                pixel_size=system.pixel_size,
                image_width=system.image_width,
                image_height=system.image_height,
            )
            min_dist.append(temp_system.min_measurable_distance())
            max_dist.append(temp_system.max_measurable_distance())
        ax3.plot(baseline_range*1e3, min_dist, label='最小测距', linewidth=2)
        ax3.plot(baseline_range*1e3, max_dist, label='最大测距', linewidth=2)
        ax3.set_xlabel('基线长度 (mm)', fontsize=10)
        ax3.set_ylabel('测距范围 (m)', fontsize=10)
        ax3.set_title('基线长度与测距范围', fontsize=11, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)

        # 2. 焦距与视场角
        ax4 = self.param_fig.add_subplot(gs[0, 1])
        focal_range = np.linspace(1, 50, 50) * 1e-3  # 转换为米
        fov_h = []
        fov_v = []
        for f in focal_range:
            temp_system = StereoRangingSystem(
                baseline=system.baseline,
                focal_length=f,
                pixel_size=system.pixel_size,
                image_width=system.image_width,
                image_height=system.image_height,
            )
            fov_h.append(np.degrees(temp_system.fov_horizontal()))
            fov_v.append(np.degrees(temp_system.fov_vertical()))
        ax4.plot(focal_range*1e3, fov_h, label='水平视场角', linewidth=2)
        ax4.plot(focal_range*1e3, fov_v, label='垂直视场角', linewidth=2)
        ax4.set_xlabel('焦距 (mm)', fontsize=10)
        ax4.set_ylabel('视场角 (°)', fontsize=10)
        ax4.set_title('焦距与视场角关系', fontsize=11, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)

        # 3. 像素尺寸与测距精度
        ax5 = self.param_fig.add_subplot(gs[1, 0])
        pixel_range = np.linspace(1, 10, 50) * 1e-6  # 转换为米
        error_at_5m = []
        for p in pixel_range:
            temp_system = StereoRangingSystem(
                baseline=system.baseline,
                focal_length=system.focal_length,
                pixel_size=p,
                image_width=system.image_width,
                image_height=system.image_height,
            )
            error_at_5m.append(temp_system.range_error(5.0))
        ax5.plot(pixel_range*1e6, error_at_5m, linewidth=2, color='green')
        ax5.set_xlabel('像素尺寸 (μm)', fontsize=10)
        ax5.set_ylabel('5米处测距误差 (m)', fontsize=10)
        ax5.set_title('像素尺寸与测距精度', fontsize=11, fontweight='bold')
        ax5.grid(True, alpha=0.3)

        # 4. 距离与视差关系
        ax6 = self.param_fig.add_subplot(gs[1, 1])
        distance_range = np.linspace(0.5, 30, 100)
        disparity = []
        for d in distance_range:
            disparity.append(system.disparity_from_distance(d))
        ax6.plot(distance_range, disparity, linewidth=2, color='purple')
        ax6.set_xlabel('距离 (m)', fontsize=10)
        ax6.set_ylabel('视差 (px)', fontsize=10)
        ax6.set_title('距离与视差关系', fontsize=11, fontweight='bold')
        ax6.grid(True, alpha=0.3)

        self.param_fig.suptitle('系统参数关系分析', fontsize=12, fontweight='bold')
        self.param_canvas.draw()
        
        self.update_result_display(system)

    def save_image(self):
        filepath = filedialog.asksaveasfilename(
            title="保存测距分析图像",
            initialfile=f"stereo_analysis_{self.baseline_var.get():.0f}mm.png",
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("PDF文档", "*.pdf"), 
                      ("SVG矢量图", "*.svg"), ("所有文件", "*.*")]
        )
        if filepath:
            # 获取当前选中的标签页
            current_tab = self.notebook.index(self.notebook.select())
            
            # 根据当前标签页选择对应的figure
            if current_tab == 0:  # 光路布局
                self.layout_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                     facecolor='white', edgecolor='none')
            elif current_tab == 1:  # 误差分析
                self.error_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                     facecolor='white', edgecolor='none')
            else:  # 参数关系
                self.param_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                    facecolor='white', edgecolor='none')
            
            messagebox.showinfo("保存成功", f"图像已保存到:\n{filepath}")


def main():
    root = tk.Tk()
    
    try:
        app = StereoRangingGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("错误", f"程序运行出错:\n{str(e)}")


if __name__ == "__main__":
    main()
