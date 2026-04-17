import sys
import os

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.wavefront.zernike import zernike_grid, NOLL_TO_NM, ABERRATION_NAMES

style_path = os.path.join(BASE_DIR, "config", "optics_style.mplstyle")
if os.path.exists(style_path):
    plt.style.use(style_path)


class ZernikeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zernike多项式可视化工具")
        self.root.geometry("1400x900")
        
        self.current_j = tk.IntVar(value=4)
        self.resolution = tk.IntVar(value=256)
        self.view_mode = tk.StringVar(value="combined")
        self.mode_type = tk.StringVar(value="single")
        
        self.superpose_items = []
        
        self.setup_ui()
        self.update_plot()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        mode_type_frame = ttk.LabelFrame(control_frame, text="模式", padding="5")
        mode_type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(mode_type_frame, text="单项显示", variable=self.mode_type, 
                       value="single", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_type_frame, text="叠加显示", variable=self.mode_type, 
                       value="superpose", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        
        self.single_frame = ttk.Frame(control_frame)
        self.single_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Label(self.single_frame, text="选择Zernike项:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        list_frame = ttk.Frame(self.single_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.zernike_listbox = tk.Listbox(list_frame, height=12, width=35, yscrollcommand=scrollbar.set)
        self.zernike_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.config(command=self.zernike_listbox.yview)
        
        for i, (name, (n, m)) in enumerate(zip(ABERRATION_NAMES, NOLL_TO_NM)):
            self.zernike_listbox.insert(tk.END, f"Z{i+1:2d}: {name} (n={n}, m={m:+d})")
        
        self.zernike_listbox.selection_set(3)
        self.zernike_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        self.superpose_frame = ttk.Frame(control_frame)
        
        param_desc = ttk.LabelFrame(self.superpose_frame, text="参数说明", padding="5")
        param_desc.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(param_desc, text="编号: Zernike多项式序号(Z1-Z36)，代表不同像差类型", 
                 wraplength=300, justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Label(param_desc, text="系数: 该项像差的权重，决定其在总波前中的贡献比例", 
                 wraplength=300, justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Label(param_desc, text="注: 结果自动归一化到[-1,1]，系数仅反映相对比例", 
                 wraplength=300, justify=tk.LEFT).pack(anchor=tk.W)
        
        ttk.Label(self.superpose_frame, text="叠加项设置:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.superpose_list_frame = ttk.Frame(self.superpose_frame)
        self.superpose_list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        header_frame = ttk.Frame(self.superpose_list_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="编号", width=10).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="像差名称", width=20).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="系数", width=10).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="", width=5).pack(side=tk.LEFT)
        
        self.items_container = ttk.Frame(self.superpose_list_frame)
        self.items_container.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(self.superpose_list_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="+ 添加项", command=self.add_superpose_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="加载预设", command=self.load_preset).pack(side=tk.LEFT)
        
        ttk.Label(control_frame, text="分辨率:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        resolution_combo = ttk.Combobox(control_frame, textvariable=self.resolution, 
                                       values=[128, 256, 512], state="readonly", width=10)
        resolution_combo.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        resolution_combo.bind("<<ComboboxSelected>>", lambda e: self.update_plot())
        
        ttk.Label(control_frame, text="显示模式:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        mode_frame = ttk.Frame(control_frame)
        mode_frame.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="2D热力图", variable=self.view_mode, 
                       value="2d", command=self.update_plot).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="3D曲面图", variable=self.view_mode, 
                       value="3d", command=self.update_plot).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="2D+3D组合", variable=self.view_mode, 
                       value="combined", command=self.update_plot).pack(anchor=tk.W)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(20, 10))
        
        ttk.Button(button_frame, text="更新显示", command=self.update_plot).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="保存图像", command=self.save_image).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="显示全部36项", command=self.show_all).pack(fill=tk.X, pady=(0, 5))
        
        self.info_label = ttk.Label(control_frame, text="", wraplength=280)
        self.info_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 0))
        
        plot_frame = ttk.LabelFrame(main_frame, text="可视化", padding="10")
        plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        
        self.fig = plt.figure(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def add_superpose_item(self, j=4, coeff=1.0):
        item_frame = ttk.Frame(self.items_container)
        item_frame.pack(fill=tk.X, pady=(0, 5))
        
        j_var = tk.StringVar(value=f"Z{j:2d}: {ABERRATION_NAMES[j-1]}")
        coeff_var = tk.DoubleVar(value=coeff)
        
        zernike_names = [f"Z{i+1:2d}: {name}" for i, name in enumerate(ABERRATION_NAMES)]
        combo = ttk.Combobox(item_frame, textvariable=j_var, values=zernike_names, 
                            state="readonly", width=28)
        combo.current(j - 1)
        combo.pack(side=tk.LEFT, padx=(0, 5))
        
        coeff_entry = ttk.Entry(item_frame, textvariable=coeff_var, width=8)
        coeff_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        def remove():
            item_frame.destroy()
            self.superpose_items = [item for item in self.superpose_items if item["frame"] != item_frame]
            self.update_plot()
        
        ttk.Button(item_frame, text="×", width=3, command=remove).pack(side=tk.LEFT)
        
        def on_change(*args):
            self.update_plot()
        
        j_var.trace_add("write", on_change)
        coeff_var.trace_add("write", on_change)
        
        self.superpose_items.append({"frame": item_frame, "j_var": j_var, "coeff_var": coeff_var})
    
    def on_mode_change(self):
        mode = self.mode_type.get()
        if mode == "single":
            self.single_frame.grid()
            self.superpose_frame.grid_remove()
        else:
            self.single_frame.grid_remove()
            self.superpose_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.update_plot()
    
    def load_preset(self):
        for item in self.superpose_items:
            item["frame"].destroy()
        self.superpose_items.clear()
        
        self.add_superpose_item(j=4, coeff=1.0)
        self.add_superpose_item(j=11, coeff=0.5)
        self.update_plot()
    
    def on_listbox_select(self, event):
        selection = self.zernike_listbox.curselection()
        if selection:
            self.current_j.set(selection[0] + 1)
            self.update_plot()
    
    def get_superpose_coeffs(self):
        coeffs = {}
        for item in self.superpose_items:
            try:
                name = item["j_var"].get()
                j = int(name.split(":")[0].replace("Z", "").strip())
                c = float(item["coeff_var"].get())
                if 1 <= j <= 36:
                    coeffs[j] = c
            except (ValueError, IndexError):
                continue
        return coeffs
    
    def compute_superposed(self, resolution):
        coeffs = self.get_superpose_coeffs()
        if not coeffs:
            return None, None, None
        
        Z_total = np.zeros((resolution, resolution))
        x = np.linspace(-1, 1, resolution)
        y = np.linspace(-1, 1, resolution)
        X, Y = np.meshgrid(x, y)
        rho = np.sqrt(X**2 + Y**2)
        theta = np.arctan2(Y, X)
        
        from src.wavefront.zernike import zernike_noll
        
        for j, c in coeffs.items():
            Z_j = zernike_noll(j, rho, theta)
            Z_j[rho > 1] = np.nan
            Z_total += c * Z_j
        
        mask = np.isnan(Z_total)
        if not np.all(mask):
            max_val = np.nanmax(np.abs(Z_total))
            if max_val > 0:
                Z_total = Z_total / max_val
        
        return Z_total, X, Y
    
    def update_plot(self):
        mode_type = self.mode_type.get()
        resolution = self.resolution.get()
        mode = self.view_mode.get()
        
        self.fig.clear()
        
        if mode_type == "single":
            j = self.current_j.get()
            n, m = NOLL_TO_NM[j - 1]
            name = ABERRATION_NAMES[j - 1]
            self.info_label.config(text=f"当前: Z{j} {name}\n径向阶数 n={n}, 角向阶数 m={m:+d}")
            
            Z = zernike_grid(j, resolution)
            x = np.linspace(-1, 1, resolution)
            y = np.linspace(-1, 1, resolution)
            X, Y = np.meshgrid(x, y)
        else:
            coeffs = self.get_superpose_coeffs()
            if not coeffs:
                self.info_label.config(text="请添加叠加项")
                ax = self.fig.add_subplot(111)
                ax.text(0.5, 0.5, "请添加叠加项", ha="center", va="center", transform=ax.transAxes)
                ax.axis("off")
                self.canvas.draw()
                return
            
            coeff_str = ", ".join([f"Z{j}={c}" for j, c in coeffs.items()])
            self.info_label.config(text=f"叠加: {coeff_str}")
            
            Z, X, Y = self.compute_superposed(resolution)
            if Z is None:
                return
        
        if mode == "2d":
            ax = self.fig.add_subplot(111)
            im = ax.imshow(Z, cmap="RdBu_r", extent=[-1, 1, -1, 1], vmin=-1, vmax=1)
            if mode_type == "single":
                n, m = NOLL_TO_NM[self.current_j.get() - 1]
                name = ABERRATION_NAMES[self.current_j.get() - 1]
                ax.set_title(f"Z{self.current_j.get()} {name} (n={n}, m={m})\n2D热力图", fontsize=14)
            else:
                ax.set_title("叠加波前 2D热力图", fontsize=14)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_aspect("equal")
            self.fig.colorbar(im, ax=ax, label="Zernike值")
            
        elif mode == "3d":
            ax = self.fig.add_subplot(111, projection="3d")
            mask = np.isnan(Z)
            Z_masked = np.ma.array(Z, mask=mask)
            surf = ax.plot_surface(X, Y, Z_masked, cmap="RdBu_r", vmin=-1, vmax=1, alpha=0.9)
            if mode_type == "single":
                n, m = NOLL_TO_NM[self.current_j.get() - 1]
                name = ABERRATION_NAMES[self.current_j.get() - 1]
                ax.set_title(f"Z{self.current_j.get()} {name} (n={n}, m={m})\n3D曲面图", fontsize=14)
            else:
                ax.set_title("叠加波前 3D曲面图", fontsize=14)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_zlabel("Zernike值")
            self.fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="Zernike值")
            
        elif mode == "combined":
            ax1 = self.fig.add_subplot(121)
            im = ax1.imshow(Z, cmap="RdBu_r", extent=[-1, 1, -1, 1], vmin=-1, vmax=1)
            if mode_type == "single":
                n, m = NOLL_TO_NM[self.current_j.get() - 1]
                name = ABERRATION_NAMES[self.current_j.get() - 1]
                ax1.set_title(f"Z{self.current_j.get()} {name} (n={n}, m={m})\n2D热力图", fontsize=12)
            else:
                ax1.set_title("叠加波前 2D热力图", fontsize=12)
            ax1.set_xlabel("x")
            ax1.set_ylabel("y")
            ax1.set_aspect("equal")
            self.fig.colorbar(im, ax=ax1, label="Zernike值")
            
            ax2 = self.fig.add_subplot(122, projection="3d")
            mask = np.isnan(Z)
            Z_masked = np.ma.array(Z, mask=mask)
            surf = ax2.plot_surface(X, Y, Z_masked, cmap="RdBu_r", vmin=-1, vmax=1, alpha=0.9)
            if mode_type == "single":
                ax2.set_title("3D曲面图", fontsize=12)
            else:
                ax2.set_title("叠加波前 3D曲面图", fontsize=12)
            ax2.set_xlabel("x")
            ax2.set_ylabel("y")
            ax2.set_zlabel("Zernike值")
        
        self.canvas.draw()
    
    def save_image(self):
        mode_type = self.mode_type.get()
        mode = self.view_mode.get()
        
        if mode_type == "single":
            j = self.current_j.get()
            default_name = f"zernike_{mode}_Z{j}.png"
        else:
            default_name = f"zernike_superpose_{mode}.png"
        
        filepath = filedialog.asksaveasfilename(
            title="保存图像",
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("所有文件", "*.*")]
        )
        
        if filepath:
            self.fig.savefig(filepath, dpi=300, bbox_inches="tight")
            messagebox.showinfo("保存成功", f"图像已保存到:\n{filepath}")
    
    def show_all(self):
        from src.wavefront.zernike import plot_zernike_modes
        os.makedirs("figures/wavefront", exist_ok=True)
        plot_zernike_modes(noll_max=36, resolution=256, 
                         save_path="figures/wavefront/zernike_36.png")
        messagebox.showinfo("完成", "36项概览图已生成并保存")


def main():
    root = tk.Tk()
    app = ZernikeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
