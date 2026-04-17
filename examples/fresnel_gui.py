import sys
import os
import tempfile
import webbrowser
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio

plt.style.use("config/optics_style.mplstyle")

from src.fresnel.lens import FresnelLens


class FresnelLensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("菲涅尔透镜设计工具 - Optical Instrument Design")
        self.root.geometry("1500x950")
        
        self.lens = None
        self.plotly_html_path = None
        
        self.create_widgets()
        self.update_design()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(main_frame, width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        param_frame = ttk.LabelFrame(left_panel, text="透镜设计参数", padding=10)
        param_frame.pack(fill=tk.X, pady=(0, 8))
        
        params = [
            ("波长 λ (nm)", "632", "激光波长，决定相位周期和刻蚀深度"),
            ("焦距 f (mm)", "100", "焦点到透镜的距离"),
            ("直径 D (mm)", "25.0", "透镜通光孔径"),
            ("折射率 n", "1.5", "透镜材料折射率（如玻璃~1.5）"),
        ]
        
        self.param_vars = {}
        for label, default, tip in params:
            frame = ttk.Frame(param_frame)
            frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(frame, text=label, width=14).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            
            tip_btn = ttk.Button(frame, text="?", width=2,
                                 command=lambda t=tip: messagebox.showinfo("参数说明", t))
            tip_btn.pack(side=tk.LEFT)
            
            self.param_vars[label] = var
        
        btn_frame = ttk.Frame(param_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="更新设计",
                   command=self.update_design).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="重置默认",
                   command=self.reset_params).pack(side=tk.LEFT, padx=2)
        
        info_frame = ttk.LabelFrame(left_panel, text="设计结果", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.info_text = tk.Text(info_frame, height=12, width=36,
                                  font=("Consolas", 9), state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)
        
        explain_frame = ttk.LabelFrame(left_panel, text="图像说明", padding=10)
        explain_frame.pack(fill=tk.BOTH, expand=True)
        
        self.explain_text = tk.Text(explain_frame, height=14, width=36,
                                     font=("Microsoft YaHei", 9), wrap=tk.WORD,
                                     state=tk.DISABLED)
        self.explain_text.pack(fill=tk.BOTH, expand=True)
        
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        tab_3d = ttk.Frame(notebook)
        notebook.add(tab_3d, text=" 3D透镜结构 (Plotly) ")
        
        toolbar_3d = ttk.Frame(tab_3d)
        toolbar_3d.pack(fill=tk.X, padx=5, pady=(5, 0))
        ttk.Label(toolbar_3d, text="提示: 点击下方按钮在浏览器中打开交互式3D图",
                  font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        ttk.Button(toolbar_3d, text="🌐 浏览器中打开交互3D",
                   command=self.open_plotly_browser).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar_3d, text="💾 导出HTML",
                   command=self.export_plotly_html).pack(side=tk.RIGHT, padx=2)
        
        self.preview_label = tk.Label(tab_3d, text="点击上方按钮在浏览器中查看\n流畅的WebGL交互式3D模型\n\n支持：鼠标拖拽旋转 / 滚轮缩放 / 右键平移",
                                      font=("Microsoft YaHei", 11),
                                      justify=tk.CENTER, fg="#555555")
        self.preview_label.pack(expand=True)
        
        tab_overview = ttk.Frame(notebook)
        notebook.add(tab_overview, text=" 设计总览 ")
        self.fig_ov = Figure(figsize=(9, 6), dpi=100, constrained_layout=True)
        self.canvas_ov = FigureCanvasTkAgg(self.fig_ov, master=tab_overview)
        self.canvas_ov.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        save_frame = ttk.Frame(right_panel)
        save_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(save_frame, text="保存总览图",
                   command=self.save_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(save_frame, text="保存3D图像",
                   command=self.save_3d_image).pack(side=tk.LEFT, padx=2)
        self.save_var = tk.StringVar(value="figures/fresnel/菲涅尔透镜设计.png")
        ttk.Entry(save_frame, textvariable=self.save_var, width=40).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def get_lens_params(self):
        try:
            wavelength = float(self.param_vars["波长 λ (nm)"].get()) * 1e-9
            focal_length = float(self.param_vars["焦距 f (mm)"].get()) * 1e-3
            diameter = float(self.param_vars["直径 D (mm)"].get()) * 1e-3
            n = float(self.param_vars["折射率 n"].get())
            
            if wavelength <= 0 or focal_length <= 0 or diameter <= 0 or n <= 1:
                raise ValueError("参数必须为正数")
            return wavelength, focal_length, diameter / 2, n
        except Exception as e:
            messagebox.showerror("参数错误", f"请输入有效的数值参数:\n{e}")
            return None
    
    def update_design(self):
        params = self.get_lens_params()
        if params is None:
            return
        
        wavelength, focal_length, radius, n = params
        self.lens = FresnelLens(
            focal_length=focal_length,
            wavelength=wavelength,
            radius=radius,
            n=n,
        )
        
        radii = self.lens.ring_radii()
        n_total = len(radii)
        
        min_spacing = np.min(np.diff(radii)) * 1e6 if len(radii) > 1 else 0
        n_mfg = int(min(n_total, max(20, int(radius * 1e3 / 0.02))))
        
        self.n_manufacture = n_mfg
        self.radii_mfg = radii[:n_mfg]
        
        info = (
            f"{'='*32}\n"
            f"   菲涅尔透镜设计结果\n"
            f"{'='*32}\n\n"
            f"  波长:     {wavelength*1e9:.0f} nm\n"
            f"  焦距:     {focal_length*1e3:.0f} mm\n"
            f"  直径:     {radius*2*1e3:.1f} mm\n"
            f"  F数:      {self.lens.f_number():.2f}\n"
            f"  折射率:   {n}\n"
            f"\n{'─'*30}\n"
            f"  理论环带数:  {n_total}\n"
            f"  刻蚀深度:   {self.lens.etch_depth()*1e9:.1f} nm\n"
            f"  光斑尺寸:   {self.lens.focal_spot_size()*1e6:.1f} μm\n"
            f"\n{'─'*30}\n"
            f"  可制造环带:  {n_mfg}\n"
            f"  有效半径:   {radii[n_mfg-1]*1e3:.2f} mm\n"
            f"  最小环间距:  {min_spacing:.2f} μm\n"
            f"{'='*32}"
        )
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
        
        self.build_plotly_figure()
        self.plot_overview()
        
        explanation = (
            "【3D透镜结构 (Plotly)】\n"
            "使用WebGL渲染的交互式3D模型。\n"
            "点击\"浏览器中打开\"即可操作：\n"
            "- 左键拖拽: 旋转视角\n"
            "- 滚轮: 缩放\n"
            "- 右键拖拽: 平移\n"
            "蓝白交替同心圆环代表阶梯状\n"
            "刻蚀结构，高度差h=λ/(n-1)。\n\n"
            "【设计总览图】\n"
            "包含5个子图的综合分析：\n\n"
            "① 参数面板 - 核心设计规格\n"
            "② 环带半径曲线 - r=√(nλf)\n"
            "③ 相位分布剖面 - 锯齿状包裹相位\n"
            "④ 截面结构 - 阶梯状物理形态\n"
            "⑤ 2D相位热力图 - 同心圆对称性\n\n"
            "【制造约束】\n"
            f"理论{n_total}环，内环间距过小\n"
            f"(<{min_spacing:.1f}μm)，实际可制造\n"
            f"{n_mfg}环。内环区域需用平面替代。"
        )
        
        self.explain_text.config(state=tk.NORMAL)
        self.explain_text.delete(1.0, tk.END)
        self.explain_text.insert(tk.END, explanation)
        self.explain_text.config(state=tk.DISABLED)
    
    def build_plotly_figure(self):
        radii_mfg = self.radii_mfg
        n_mfg = self.n_manufacture
        r_cut = radii_mfg[-1]
        h_step = self.lens.etch_depth() * 1e9
        
        N_theta = 120
        theta = np.linspace(0, 2 * np.pi, N_theta)
        
        fig = go.Figure()
        
        for i in range(n_mfg):
            r_inner = 0 if i == 0 else radii_mfg[i-1] * 1e3
            r_outer = radii_mfg[i] * 1e3
            
            theta_full = np.concatenate([theta, theta[::-1]])
            r_full = np.concatenate([np.full(N_theta, r_outer),
                                      np.full(N_theta, r_inner)])
            
            x_ring = r_full * np.cos(theta_full)
            y_ring = r_full * np.sin(theta_full)
            
            z_top = np.where(np.arange(len(theta_full)) < N_theta,
                             h_step if i % 2 == 0 else h_step * 0.92, 0)
            z_bottom = np.zeros_like(z_top)
            
            color_top = "#42A5F5" if i % 2 == 0 else "#90CAF9"
            color_side = "#1565C0" if i % 2 == 0 else "#64B5F6"
            
            fig.add_trace(go.Mesh3d(
                x=np.concatenate([x_ring, x_ring]),
                y=np.concatenate([y_ring, y_ring]),
                z=np.concatenate([z_top, z_bottom]),
                i=list(range(0, 2*N_theta)),
                j=list(range(1, 2*N_theta+1)),
                k=list(range(2*N_theta, 4*N_theta)),
                color=color_top,
                opacity=0.92,
                name=f"环{i+1}",
                showlegend=False,
            ))
        
        theta_circle = np.linspace(0, 2*np.pi, N_theta)
        x_c = np.cos(theta_circle) * r_cut * 1e3
        y_c = np.sin(theta_circle) * r_cut * 1e3
        z_c_base = np.full(N_theta, -h_step * 0.05)
        
        fig.add_trace(go.Scatter3d(
            x=x_c, y=y_c, z=z_c_base,
            mode='lines',
            line=dict(color="#90CAF9", width=2),
            name="边缘",
            showlegend=False,
        ))
        
        fig.update_layout(
            title=dict(
                text=f"菲涅尔透镜3D结构 ({n_mfg}环) | λ={self.lens.wavelength*1e9:.0f}nm "
                      f"f={self.lens.focal_length*1e3:.0f}mm D={self.lens.radius*2*1e3:.1f}mm",
                font=dict(size=16, family="Microsoft YaHei"),
                x=0.5,
            ),
            scene=dict(
                xaxis=dict(title="x (mm)", tickfont=dict(size=11)),
                yaxis=dict(title="y (mm)", tickfont=dict(size=11)),
                zaxis=dict(title="高度 (nm)", tickfont=dict(size=11)),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.12),
                camera=dict(
                    eye=dict(x=-1.5, y=-1.5, z=0.8),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1),
                ),
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor="white",
            font=dict(family="Microsoft YaHei"),
        )
        
        tmp_dir = tempfile.mkdtemp(prefix="fresnel_")
        self.plotly_html_path = os.path.join(tmp_dir, "fresnel_3d.html")
        pio.write_html(fig, self.plotly_html_path,
                        include_plotlyjs=True, auto_open=False,
                        config={"displayModeBar": True, "scrollZoom": True})
        
        ring_info = f"已生成: {n_mfg}个环带 | "
        ring_info += f"有效半径: {r_cut:.2f}mm | "
        ring_info += f"刻蚀深度: {h_step:.0f}nm"
        self.preview_label.config(text=f"{ring_info}\n\n点击上方按钮在浏览器中查看\n流畅的WebGL交互式3D模型\n\n支持：鼠标拖拽旋转 / 滚轮缩放 / 右键平移")
    
    def open_plotly_browser(self):
        if self.plotly_html_path and os.path.exists(self.plotly_html_path):
            webbrowser.open("file://" + os.path.abspath(self.plotly_html_path))
        else:
            messagebox.showwarning("提示", "请先更新设计生成3D模型")
    
    def export_plotly_html(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html"), ("所有文件", "*.*")],
            initialfile="菲涅尔透镜3D.html",
        )
        if path and self.plotly_html_path:
            import shutil
            shutil.copy2(self.plotly_html_path, path)
            messagebox.showinfo("成功", f"Plotly 3D HTML 已导出至:\n{path}")
    
    def plot_overview(self):
        self.fig_ov.clear()
        
        lens = self.lens
        radii = lens.ring_radii()
        n_rings = len(radii)
        
        ax1 = self.fig_ov.add_subplot(2, 3, 1)
        ax1.text(0.5, 0.92, "设计参数", fontsize=11, fontweight="bold",
                 ha="center", transform=ax1.transAxes)
        params_text = (
            f"λ={lens.wavelength*1e9:.0f}nm\n"
            f"f={lens.focal_length*1e3:.0f}mm\n"
            f"D={lens.radius*2*1e3:.1f}mm\n"
            f"F/{lens.f_number():.1f}\n"
            f"n={lens.n}\n"
            f"环带={n_rings}\n"
            f"h={lens.etch_depth()*1e9:.0f}nm"
        )
        ax1.text(0.5, 0.45, params_text, fontsize=9, ha="center", va="center",
                 transform=ax1.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#E3F2FD",
                           edgecolor="#1565C0"))
        ax1.set_xlim(0, 1); ax1.set_ylim(0, 1); ax1.axis("off")
        
        ax2 = self.fig_ov.add_subplot(2, 3, 2)
        ring_nums = np.arange(1, min(n_rings, 200) + 1)
        ax2.plot(ring_nums, radii[:len(ring_nums)] * 1e3, "b-", lw=1.2)
        ax2.set_xlabel("环带序号 n"); ax2.set_ylabel("半径 (mm)")
        ax2.set_title("r = √(nλf)", fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        ax3 = self.fig_ov.add_subplot(2, 3, 3)
        x_radial = np.linspace(-lens.radius, lens.radius, 500)
        y_zero = np.zeros_like(x_radial)
        phase_radial = lens.wrapped_phase(x_radial.reshape(-1, 1),
                                           y_zero.reshape(1, -1))[0, :]
        ax3.plot(x_radial * 1e3, phase_radial, "b-", lw=1.2)
        ax3.set_xlabel("径向位置 (mm)"); ax3.set_ylabel("相位 (rad)")
        ax3.set_title("包裹相位 (0~2π)", fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        ax4 = self.fig_ov.add_subplot(2, 3, (4, 5))
        r_plot = lens.radius * 1e3
        step_height = lens.etch_depth() * 1e9
        n_show = min(n_rings, 60)
        for i in range(n_show):
            r_inner = 0 if i == 0 else radii[i-1] * 1e3
            r_outer = radii[i] * 1e3
            color = "#42A5F5" if i % 2 == 0 else "#BBDEFB"
            ax4.fill_between([r_inner, r_outer], [0, 0],
                             [step_height if i % 2 else step_height*0.9,
                              step_height if i % 2 else step_height*0.9],
                             color=color, edgecolor="#1565C0", linewidth=0.3)
        if n_show < n_rings:
            ax4.fill_between([radii[n_show-1]*1e3, r_plot], [0, 0],
                             [step_height/2, step_height/2], color="#BDBDBD",
                             edgecolor="gray", linewidth=0.5, hatch="//")
            ax4.text((radii[n_show-1]+lens.radius)/2*1e3, step_height/2,
                     f"...{n_rings}环", ha="center", va="center", fontsize=8)
        ax4.annotate("", xy=(0, -step_height*0.12),
                     xytext=(r_plot, -step_height*0.12),
                     arrowprops=dict(arrowstyle="<->", lw=1.2, color="black"))
        ax4.text(r_plot/2, -step_height*0.2, f"D={lens.radius*2*1e3:.1f}mm",
                ha="center", fontsize=9, fontweight="bold")
        ax4.set_xlim(-r_plot*0.2, r_plot*1.08)
        ax4.set_ylim(-step_height*0.3, step_height*1.25)
        ax4.set_xlabel("径向位置 (mm)"); ax4.set_ylabel("高度 (nm)")
        ax4.set_title("截面结构 (阶梯状)", fontsize=10)
        ax4.grid(True, alpha=0.2, axis="y")
        
        ax5 = self.fig_ov.add_subplot(2, 3, 6)
        x = np.linspace(-lens.radius, lens.radius, 200)
        y = np.linspace(-lens.radius, lens.radius, 200)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        mask = R <= lens.radius
        phase_2d = np.zeros_like(R)
        phase_2d[mask] = lens.wrapped_phase(X[mask], Y[mask])
        im = ax5.imshow(phase_2d,
                        extent=[-lens.radius*1e3, lens.radius*1e3,
                                -lens.radius*1e3, lens.radius*1e3],
                        cmap="hsv", vmin=0, vmax=2*np.pi, origin="lower")
        ax5.set_xlabel("x (mm)"); ax5.set_ylabel("y (mm)")
        ax5.set_title("2D相位分布", fontsize=10)
        ax5.set_aspect("equal")
        self.fig_ov.colorbar(im, ax=ax5, label="rad", shrink=0.75)
        
        self.canvas_ov.draw()
    
    def reset_params(self):
        self.param_vars["波长 λ (nm)"].set("632")
        self.param_vars["焦距 f (mm)"].set("100")
        self.param_vars["直径 D (mm)"].set("25.0")
        self.param_vars["折射率 n"].set("1.5")
        self.update_design()
    
    def save_image(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("所有文件", "*.*")],
            initialfile=os.path.basename(self.save_var.get()),
        )
        if path:
            self.fig_ov.savefig(path, dpi=300, bbox_inches="tight")
            messagebox.showinfo("成功", f"设计总览已保存至:\n{path}")
    
    def save_3d_image(self):
        if not self.plotly_html_path or not os.path.exists(self.plotly_html_path):
            messagebox.showwarning("提示", "请先更新设计生成3D模型")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html"), ("PNG图像", "*.png")],
            initialfile="菲涅尔透镜3D.html",
        )
        if path:
            if path.endswith(".png"):
                try:
                    fig = pio.read_html(self.plotly_html_path)
                    pio.write_image(fig, path, engine="kaleido", scale=2)
                    messagebox.showinfo("成功", f"3D图像已保存至:\n{path}")
                except Exception as e:
                    messagebox.showerror("错误",
                        f"导出PNG需要安装kaleido:\npip install kaleido\n\n"
                        f"或选择.html格式直接保存交互式3D。\n原始错误: {e}")
            else:
                import shutil
                shutil.copy2(self.plotly_html_path, path)
                messagebox.showinfo("成功", f"Plotly 3D HTML 已保存至:\n{path}")


def main():
    root = tk.Tk()
    app = FresnelLensGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
