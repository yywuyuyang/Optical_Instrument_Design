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
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.collections import LineCollection
from scipy.special import jv
from src.grating.analysis import DiffractionGrating

style_path = os.path.join(BASE_DIR, "config", "optics_style.mplstyle")
if os.path.exists(style_path):
    plt.style.use(style_path)


class GratingAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("衍射光栅分析软件 - Diffraction Grating Analyzer")
        self.root.geometry("1400x900")

        # 参数变量
        self.period_var = tk.DoubleVar(value=2.0)
        self.wavelength_var = tk.DoubleVar(value=632.0)
        self.incidence_angle_var = tk.DoubleVar(value=0.0)
        self.max_order_var = tk.IntVar(value=5)
        
        # 光栅类型参数
        self.grating_type_var = tk.StringVar(value="sine_phase")
        self.phase_depth_var = tk.DoubleVar(value=2.0)
        self.duty_cycle_var = tk.DoubleVar(value=0.5)

        # 可视化选项
        self.show_field_pattern = tk.BooleanVar(value=True)
        self.show_efficiency_chart = tk.BooleanVar(value=True)
        self.show_angle_diagram = tk.BooleanVar(value=True)

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
        param_frame = ttk.LabelFrame(parent, text="光栅基本参数", padding="8")
        param_frame.pack(fill=tk.X, pady=(0, 8))

        params = [
            ("光栅周期 d (μm):", self.period_var, 0.5, 10.0, 
             "光栅周期，决定衍射角大小"),
            ("波长 λ (nm):", self.wavelength_var, 300.0, 2000.0,
             "入射光波长"),
            ("入射角 θi (°):", self.incidence_angle_var, -89.0, 89.0,
             "光线与光栅法线的夹角"),
            ("最大级次 m:", self.max_order_var, 1, 10,
             "计算的衍射级次范围"),
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

        # 光栅类型设置
        type_frame = ttk.LabelFrame(parent, text="光栅类型配置", padding="8")
        type_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(type_frame, text="光栅类型:").pack(anchor=tk.W)
        type_combo = ttk.Combobox(type_frame, textvariable=self.grating_type_var,
                                   values=["sine_phase", "amplitude", "rect_phase"],
                                   state="readonly", width=20)
        type_combo.pack(fill=tk.X, pady=(3, 5))
        type_combo.bind("<<ComboboxSelected>>", lambda e: self.on_param_change())

        phase_row = ttk.Frame(type_frame)
        phase_row.pack(fill=tk.X, pady=2)
        ttk.Label(phase_row, text="相位深度 φ (rad):").pack(side=tk.LEFT)
        ttk.Entry(phase_row, textvariable=self.phase_depth_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        self.phase_depth_var.trace_add("write", lambda *args: self.on_param_change())

        duty_row = ttk.Frame(type_frame)
        duty_row.pack(fill=tk.X, pady=2)
        ttk.Label(duty_row, text="占空比 DC:").pack(side=tk.LEFT)
        ttk.Entry(duty_row, textvariable=self.duty_cycle_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        self.duty_cycle_var.trace_add("write", lambda *args: self.on_param_change())

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
        result_frame = ttk.LabelFrame(parent, text="计算结果", padding="8")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.result_text = tk.Text(result_frame, height=15, width=40, font=("Consolas", 9),
                                   state=tk.DISABLED, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 使用说明
        desc_frame = ttk.LabelFrame(parent, text="使用说明", padding="8")
        desc_frame.pack(fill=tk.X)

        desc_text = """【功能说明】
• 实时计算衍射角和效率
• 支持多种光栅类型
• 光学可视化效果展示

【可视化内容】
1. 衍射光场分布图
2. 效率随参数变化曲线  
3. 衍射角度示意图"""

        desc_label = ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT,
                               wraplength=320, font=("Microsoft YaHei", 9))
        desc_label.pack(anchor=tk.W)

    def setup_display_area(self, parent):
        display_frame = ttk.LabelFrame(parent, text="衍射光场可视化分析", padding="10")
        display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)

        # 创建多标签页
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页1：衍射光场分布图
        field_frame = ttk.Frame(self.notebook)
        field_frame.columnconfigure(0, weight=1)
        field_frame.rowconfigure(0, weight=1)
        self.notebook.add(field_frame, text="衍射光场分布")
        
        self.field_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.field_canvas = FigureCanvasTkAgg(self.field_fig, master=field_frame)
        self.field_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页2：效率分析
        efficiency_frame = ttk.Frame(self.notebook)
        efficiency_frame.columnconfigure(0, weight=1)
        efficiency_frame.rowconfigure(0, weight=1)
        self.notebook.add(efficiency_frame, text="效率分析")
        
        self.efficiency_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.efficiency_canvas = FigureCanvasTkAgg(self.efficiency_fig, master=efficiency_frame)
        self.efficiency_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页3：角度关系
        angle_frame = ttk.Frame(self.notebook)
        angle_frame.columnconfigure(0, weight=1)
        angle_frame.rowconfigure(0, weight=1)
        self.notebook.add(angle_frame, text="角度关系")
        
        self.angle_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.angle_canvas = FigureCanvasTkAgg(self.angle_fig, master=angle_frame)
        self.angle_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标签页4：参数扫描
        scan_frame = ttk.Frame(self.notebook)
        scan_frame.columnconfigure(0, weight=1)
        scan_frame.rowconfigure(0, weight=1)
        self.notebook.add(scan_frame, text="参数扫描")
        
        self.scan_fig = plt.figure(figsize=(12, 8), constrained_layout=True)
        self.scan_canvas = FigureCanvasTkAgg(self.scan_fig, master=scan_frame)
        self.scan_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def get_grating(self):
        return DiffractionGrating(
            period=self.period_var.get() * 1e-6,
            wavelength=self.wavelength_var.get() * 1e-9,
            incidence_angle=np.radians(self.incidence_angle_var.get()),
            max_order=int(self.max_order_var.get()),
        )

    def on_param_change(self):
        try:
            self.get_grating()
            self.update_analysis()
        except Exception:
            pass

    def reset_params(self):
        self.period_var.set(2.0)
        self.wavelength_var.set(632.0)
        self.incidence_angle_var.set(0.0)
        self.max_order_var.set(5)
        self.grating_type_var.set("sine_phase")
        self.phase_depth_var.set(2.0)
        self.duty_cycle_var.set(0.5)
        self.update_analysis()

    def update_result_display(self, grating):
        angles = grating.all_diffraction_angles()
        
        result = f"═══ 衍射光栅参数 ═══\n"
        result += f"光栅周期: {grating.period*1e6:.3f} μm\n"
        result += f"波长:     {grating.wavelength*1e9:.1f} nm\n"
        result += f"入射角:   {np.degrees(grating.incidence_angle):.2f}°\n"
        result += f"最大级次: ±{grating.max_order}\n\n"

        result += f"═══ 衍射角计算结果 ═══\n"
        for m, angle in sorted(angles.items()):
            if angle is not None:
                eff = self.calculate_efficiency(grating, m)
                result += f"m={m:+2d}: θ={np.degrees(angle):+7.2f}° | η={eff:.4f}\n"
            else:
                result += f"m={m:+2d}: 蒸发波 (无传播)\n"

        result += f"\n═══ 光栅方程验证 ═══\n"
        result += f"d·sin(θm) = mλ + d·sin(θi)\n"

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)

    def calculate_efficiency(self, grating, order):
        grating_type = self.grating_type_var.get()
        phase_depth = self.phase_depth_var.get()
        duty_cycle = self.duty_cycle_var.get()

        if grating_type == "sine_phase":
            return grating.efficiency_sine_phase(order, phase_depth)
        elif grating_type == "amplitude":
            return grating.efficiency_amplitude(order, duty_cycle)
        else:
            return grating.efficiency_rect_phase(order, duty_cycle, phase_depth)

    def update_analysis(self):
        grating = self.get_grating()
        
        # 更新标签页1：衍射光场分布
        self.field_fig.clear()
        ax1 = self.field_fig.add_subplot(111)
        self.plot_optical_field_pattern(grating, ax1)
        self.field_canvas.draw()

        # 更新标签页2：效率分析
        self.efficiency_fig.clear()
        ax2 = self.efficiency_fig.add_subplot(111)
        self.plot_efficiency_analysis(grating, ax2)
        self.efficiency_canvas.draw()

        # 更新标签页3：角度关系
        self.angle_fig.clear()
        gs = self.angle_fig.add_gridspec(1, 2, wspace=0.3)
        ax3 = self.angle_fig.add_subplot(gs[0, 0])
        ax4 = self.angle_fig.add_subplot(gs[0, 1])
        self.plot_angle_relationships(grating, ax3, ax4)
        self.angle_canvas.draw()

        # 更新标签页4：参数扫描
        self.scan_fig.clear()
        self.plot_parameter_scan(grating)
        self.scan_canvas.draw()
        
        self.update_result_display(grating)

    def plot_optical_field_pattern(self, grating, ax):
        
        period = grating.period
        wavelength = grating.wavelength
        incidence_angle = grating.incidence_angle
        
        # 绘制光栅结构
        y_grating = -0.15
        num_periods = 8
        
        # 绘制光栅刻线
        for i in range(num_periods * 4):
            x_start = i * period / 4 - num_periods * period / 2
            if i % 4 < 2:
                rect = Rectangle((x_start, y_grating - 0.02), period/4, 0.04,
                                 facecolor='steelblue', alpha=0.7, edgecolor='navy')
                ax.add_patch(rect)
        
        # 绘制入射光线
        x_center = 0
        y_incident = 0.4
        
        arrow_props = dict(arrowstyle='->', color='red', lw=2, mutation_scale=20)
        
        # 入射光
        dx_in = np.sin(incidence_angle) * 0.35
        dy_in = -np.cos(incidence_angle) * 0.35
        ax.annotate('', xy=(x_center + dx_in, y_grating + 0.03),
                   xytext=(x_center - dx_in, y_incident),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
        ax.text(x_center - dx_in - 0.05, y_incident + 0.02, '入射光',
               fontsize=11, color='red', ha='right')

        # 绘制各衍射级次
        angles = grating.all_diffraction_angles()
        colors = plt.cm.rainbow(np.linspace(0, 1, len(angles)))
        
        valid_orders = [(m, angle) for m, angle in sorted(angles.items()) 
                       if angle is not None]
        
        for idx, (m, diff_angle) in enumerate(valid_orders):
            color = colors[idx]
            
            dx_out = np.sin(diff_angle) * 0.35
            dy_out = np.cos(diff_angle) * 0.35
            
            eff = self.calculate_efficiency(grating, m)
            
            linewidth = 1.5 + eff * 4
            alpha = 0.4 + eff * 0.6
            
            ax.annotate('', xy=(x_center + dx_out, y_grating - 0.25 + dy_out),
                       xytext=(x_center, y_grating - 0.03),
                       arrowprops=dict(arrowstyle='->', color=color, 
                                     lw=linewidth, alpha=alpha))
            
            label_x = x_center + dx_out * 1.3
            label_y = y_grating - 0.25 + dy_out * 1.3
            ax.annotate(f'm={m:+d}\nη={eff:.2f}', 
                       xy=(label_x, label_y),
                       fontsize=9, color=color, ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                alpha=0.8, edgecolor=color))

        ax.set_xlim(-num_periods * period / 2 - 0.5, num_periods * period / 2 + 0.5)
        ax.set_ylim(-0.45, 0.55)
        ax.set_aspect('equal')
        ax.axhline(y=y_grating, color='navy', linestyle='-', lw=3, alpha=0.8)
        ax.set_xlabel('横向位置 (μm)', fontsize=11)
        ax.set_ylabel('纵向位置 (归一化)', fontsize=11)
        ax.set_title(f'衍射光场分布示意图\n(d={period*1e6:.1f}μm, λ={wavelength*1e9:.0f}nm, θi={np.degrees(incidence_angle):.1f}°)',
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')

    def plot_efficiency_analysis(self, grating, ax):
        
        orders = list(range(-int(self.max_order_var.get()), int(self.max_order_var.get()) + 1))
        efficiencies = [self.calculate_efficiency(grating, m) for m in orders]
        
        grating_type_names = {
            'sine_phase': '正弦相位光栅',
            'amplitude': '振幅型光栅',
            'rect_phase': '矩形相位光栅'
        }
        
        type_name = grating_type_names.get(self.grating_type_var.get(), '未知')
        
        bars = ax.bar(orders, efficiencies, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(orders))),
                     edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('衍射级次 m', fontsize=11)
        ax.set_ylabel('衍射效率 η', fontsize=11)
        ax.set_title(f'{type_name} 效率分布', fontsize=12, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linewidth=0.5)

        for bar, eff in zip(bars, efficiencies):
            if eff > 0.01:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       f'{eff:.3f}', ha='center', va='bottom', fontsize=8)

    def plot_angle_relationships(self, grating, ax1, ax2):
        
        # 入射角与衍射角
        theta_range = np.linspace(-60, 60, 100)
        theta_rad = np.radians(theta_range)
        
        for m in [1, 2, 3]:
            valid_theta, valid_diff = [], []
            for theta_i in theta_rad:
                sin_val = m * grating.wavelength / grating.period + np.sin(theta_i)
                if abs(sin_val) <= 1:
                    valid_theta.append(np.degrees(theta_i))
                    valid_diff.append(np.degrees(np.arcsin(sin_val)))
            if valid_theta:
                ax1.plot(valid_theta, valid_diff, label=f'm={m}', linewidth=2)
        
        ax1.set_xlabel('入射角 (°)', fontsize=10)
        ax1.set_ylabel('衍射角 (°)', fontsize=10)
        ax1.set_title('衍射角与入射角关系', fontsize=11, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)

        # 波长与衍射角
        wl_range = np.linspace(400e-9, 800e-9, 100)
        for m in [1, 2, 3]:
            valid_wl, valid_ang = [], []
            for lam in wl_range:
                sin_val = m * lam / grating.period + np.sin(grating.incidence_angle)
                if abs(sin_val) <= 1:
                    valid_wl.append(lam * 1e9)
                    valid_ang.append(np.degrees(np.arcsin(sin_val)))
            if valid_wl:
                ax2.plot(valid_wl, valid_ang, label=f'm={m}', linewidth=2)
        
        ax2.set_xlabel('波长 (nm)', fontsize=10)
        ax2.set_ylabel('衍射角 (°)', fontsize=10)
        ax2.set_title('衍射角与波长关系', fontsize=11, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)

    def plot_parameter_scan(self, grating):
        """参数扫描分析"""
        gs = self.scan_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. 光栅周期扫描
        ax1 = self.scan_fig.add_subplot(gs[0, 0])
        period_range = np.linspace(0.5e-6, 5e-6, 100)
        for m in [1, 2, 3]:
            valid_period, valid_ang = [], []
            for d in period_range:
                sin_val = m * grating.wavelength / d + np.sin(grating.incidence_angle)
                if abs(sin_val) <= 1:
                    valid_period.append(d * 1e6)
                    valid_ang.append(np.degrees(np.arcsin(sin_val)))
            if valid_period:
                ax1.plot(valid_period, valid_ang, label=f'm={m}', linewidth=2)
        ax1.set_xlabel('光栅周期 (μm)', fontsize=10)
        ax1.set_ylabel('衍射角 (°)', fontsize=10)
        ax1.set_title('衍射角与光栅周期关系', fontsize=11, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)

        # 2. 相位深度扫描
        ax2 = self.scan_fig.add_subplot(gs[0, 1])
        depth_range = np.linspace(0, 4*np.pi, 100)
        for m in [0, 1, 2, -1, -2]:
            efficiencies = [float(jv(m, d/2)**2) for d in depth_range]
            ax2.plot(depth_range/np.pi, efficiencies, label=f'm={m}', linewidth=2)
        ax2.set_xlabel('相位深度 (π rad)', fontsize=10)
        ax2.set_ylabel('衍射效率', fontsize=10)
        ax2.set_title('效率与相位深度关系', fontsize=11, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)

        # 3. 占空比扫描
        ax3 = self.scan_fig.add_subplot(gs[1, 0])
        duty_range = np.linspace(0.1, 0.9, 100)
        for m in [0, 1, 2]:
            efficiencies = []
            for dc in duty_range:
                if m == 0:
                    eff = dc**2
                else:
                    sinc_arg = np.pi * m * dc
                    if sinc_arg == 0:
                        eff = 0
                    else:
                        eff = (dc * np.sin(sinc_arg) / sinc_arg)**2
                efficiencies.append(eff)
            ax3.plot(duty_range, efficiencies, label=f'm={m}', linewidth=2)
        ax3.set_xlabel('占空比', fontsize=10)
        ax3.set_ylabel('衍射效率', fontsize=10)
        ax3.set_title('效率与占空比关系', fontsize=11, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)

        # 4. 入射角扫描的效率变化
        ax4 = self.scan_fig.add_subplot(gs[1, 1])
        theta_range = np.linspace(-60, 60, 100)
        theta_rad = np.radians(theta_range)
        
        for m in [1, -1]:
            valid_theta, valid_eff = [], []
            for theta_i in theta_rad:
                temp_grating = DiffractionGrating(
                    period=grating.period,
                    wavelength=grating.wavelength,
                    incidence_angle=theta_i,
                    max_order=grating.max_order
                )
                sin_val = m * grating.wavelength / grating.period + np.sin(theta_i)
                if abs(sin_val) <= 1:
                    valid_theta.append(np.degrees(theta_i))
                    valid_eff.append(self.calculate_efficiency(grating, m))
            if valid_theta:
                ax4.plot(valid_theta, valid_eff, label=f'm={m}', linewidth=2)
        ax4.set_xlabel('入射角 (°)', fontsize=10)
        ax4.set_ylabel('衍射效率', fontsize=10)
        ax4.set_title('效率与入射角关系', fontsize=11, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)

    def save_image(self):
        filepath = filedialog.asksaveasfilename(
            title="保存衍射分析图像",
            initialfile=f"grating_analysis_{self.wavelength_var.get():.0f}nm.png",
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("PDF文档", "*.pdf"), 
                      ("SVG矢量图", "*.svg"), ("所有文件", "*.*")]
        )
        if filepath:
            # 获取当前选中的标签页
            current_tab = self.notebook.index(self.notebook.select())
            
            # 根据当前标签页选择对应的figure
            if current_tab == 0:  # 衍射光场分布
                self.field_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                     facecolor='white', edgecolor='none')
            elif current_tab == 1:  # 效率分析
                self.efficiency_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                         facecolor='white', edgecolor='none')
            elif current_tab == 2:  # 角度关系
                self.angle_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                     facecolor='white', edgecolor='none')
            else:  # 参数扫描
                self.scan_fig.savefig(filepath, dpi=300, bbox_inches="tight",
                                    facecolor='white', edgecolor='none')
            
            messagebox.showinfo("保存成功", f"图像已保存到:\n{filepath}")


def main():
    root = tk.Tk()
    
    try:
        app = GratingAnalyzerGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("错误", f"程序运行出错:\n{str(e)}")


if __name__ == "__main__":
    main()
