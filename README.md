# 光学仪器设计仿真软件

基于 Python 的光学仪器设计与仿真平台，涵盖菲涅尔透镜设计、光栅衍射分析、F-P腔透射分析、Zernike像差仿真和双目测距模块设计五大核心功能。

## 项目结构

```
Optical_Instrument_Design/
├── config/                     # 配置文件
│   ├── default_params.yaml     # 默认参数配置
│   └── optics_style.mplstyle   # Matplotlib 样式（中文字体）
├── dist/                       # 打包后的可执行文件
│   ├── FPCavityAnalyzer.exe    # F-P腔分析 GUI 独立程序
│   ├── FresnelLensAnalyzer.exe # 菲涅尔透镜设计 GUI 独立程序
│   ├── GratingAnalyzer.exe     # 光栅衍射分析 GUI 独立程序
│   ├── StereoRangingAnalyzer.exe # 双目测距分析 GUI 独立程序
│   └── ZernikeViewer.exe       # Zernike GUI 独立程序
├── examples/                   # 示例脚本
│   ├── example1_fresnel.py     # 菲涅尔透镜示例
│   ├── example2_grating.py     # 光栅衍射示例
│   ├── example3_fp_cavity.py   # F-P腔示例
│   ├── example4_zernike_interactive.py  # Zernike CLI交互工具
│   ├── example5_stereo.py      # 双目测距示例
│   ├── fp_cavity_gui.py        # F-P腔分析GUI
│   ├── fresnel_gui.py          # 菲涅尔透镜设计GUI（Plotly渲染）
│   ├── grating_gui.py          # 光栅衍射分析GUI
│   ├── stereo_gui.py           # 双目测距系统分析GUI
│   └── zernike_gui.py          # Zernike GUI交互工具
├── figures/                    # 输出图像
├── src/                        # 核心源代码
│   ├── fresnel/                # 菲涅尔透镜模块
│   ├── grating/                # 光栅衍射模块
│   ├── interferometry/         # F-P腔模块
│   ├── wavefront/              # Zernike像差模块
│   └── imaging/                # 双目测距模块
├── requirements.txt            # Python 依赖
└── README.md
```

## 环境配置

### 使用 Conda 虚拟环境

```bash
# 创建虚拟环境
conda create -n optics_sim python=3.10 -y

# 激活环境
conda activate optics_sim

# 安装依赖（使用清华源加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 依赖项

| 包         | 最低版本 | 用途                     |
| ---------- | -------- | ------------------------ |
| numpy      | >=1.21   | 数值计算                 |
| scipy      | >=1.7    | 科学计算（Bessel函数等） |
| matplotlib | >=3.5    | 2D 可视化               |
| plotly     | >=5.0    | WebGL交互式3D可视化      |
| PyYAML     | >=6.0    | 配置文件解析             |
| tqdm       | >=4.60   | 进度条显示               |
| pytest     | >=7.0    | 单元测试                 |
| pyinstaller| >=6.0    | 打包为可执行文件         |

## 快速开始

### 运行示例脚本

```bash
# 激活环境
conda activate optics_sim

# 运行各个模块的示例
python examples/example1_fresnel.py     # 菲涅尔透镜设计
python examples/example2_grating.py     # 光栅衍射分析
python examples/example3_fp_cavity.py   # F-P腔透射分析
python examples/example4_zernike_interactive.py  # Zernike CLI交互
python examples/example5_stereo.py      # 双目测距模块
```

### 运行 GUI 工具

```bash
# F-P腔分析GUI
python examples/fp_cavity_gui.py

# 菲涅尔透镜设计GUI（Plotly 3D渲染）
python examples/fresnel_gui.py

# 光栅衍射分析GUI
python examples/grating_gui.py

# 双目测距系统分析GUI
python examples/stereo_gui.py

# Zernike GUI交互工具
python examples/zernike_gui.py
```

### 使用独立可执行文件

直接双击运行 `dist/` 目录下的 `.exe` 文件，无需安装 Python 环境。

---

## 模块一：菲涅尔透镜设计

### 数学与光学原理

**菲涅尔透镜**是一种将传统透镜的连续曲面分解为一系列同心环带的平面光学元件。每个环带相当于原透镜的一个局部，通过阶梯状刻蚀实现相位调制。

#### 1. 环带半径公式

菲涅尔透镜的环带半径由以下公式给出：

```
r_n = √(n · λ · f)
```

其中：
- `r_n`：第 n 个环带的半径
- `n`：环带序号（1, 2, 3, ...）
- `λ`：工作波长
- `f`：焦距

#### 2. 刻蚀深度

为了实现 2π 相位调制，刻蚀深度为：

```
h = λ / (n - 1)
```

其中 `n` 为透镜材料的折射率。

#### 3. F数与光斑尺寸

```
F/# = f / D
d_spot ≈ 2.44 · λ · F/#
```

其中 `D` 为透镜直径，`d_spot` 为艾里斑直径。

#### 4. 相位分布

菲涅尔透镜的相位分布为包裹相位：

```
φ(r) = mod(π · r² / (λ · f), 2π)
```

### 使用方式

```python
from src.fresnel.lens import FresnelLens

lens = FresnelLens(
    focal_length=0.1,      # 焦距 (m)
    wavelength=632e-9,     # 波长 (m)
    radius=0.0125,         # 半径 (m)
    n=1.5,                 # 折射率
)

print(f"环带数量: {lens.num_rings()}")
print(f"刻蚀深度: {lens.etch_depth()*1e9:.1f} nm")
```

---

## 模块二：平面光栅衍射分析

### 数学与光学原理

**衍射光栅**是一种具有周期性结构的光学元件，能够将入射光分解为多个衍射级次。

#### 1. 光栅方程

```
d · sin(θ_m) = m · λ + d · sin(θ_i)
```

其中：
- `d`：光栅周期
- `θ_m`：第 m 级衍射角
- `m`：衍射级次（整数）
- `λ`：入射光波长
- `θ_i`：入射角

#### 2. 正弦相位光栅效率

对于正弦相位光栅，第 m 级衍射效率为：

```
η_m = J_m²(δ/2)
```

其中 `J_m` 为 m 阶贝塞尔函数，`δ` 为相位调制深度。

#### 3. 振幅型光栅效率

对于振幅型光栅（矩形透过率函数）：

```
η_m = sinc²(m · a/d)
```

其中 `a` 为透光部分宽度，`d` 为光栅周期。

#### 4. 矩形相位光栅效率

对于矩形相位光栅（二元光学元件）：

```
η_m = sinc²(m · a/d) · sin²(δ/2) / (π · m)²
```

### 使用方式

```python
from src.grating.analysis import DiffractionGrating

grating = DiffractionGrating(
    period=1e-6,           # 光栅周期 (m)
    wavelength=632e-9,     # 波长 (m)
    incidence_angle=0.0,   # 入射角 (rad)
    max_order=5,           # 最大衍射级次
)

# 计算衍射角
angles = grating.diffraction_angles()

# 计算效率（正弦相位光栅）
efficiencies = grating.efficiency_sine_phase(phase_depth=np.pi)
```

---

## 模块三：F-P腔透射分析

### 数学与光学原理

**法布里-珀罗（Fabry-Perot）腔**由两块平行的高反射率镜面组成，利用多光束干涉实现波长选择。

#### 1. 透射率公式（Airy公式）

```
T = 1 / [1 + F · sin²(δ/2)]
```

其中：
- `F = 4R / (1-R)²`：精细度系数
- `R`：镜面反射率
- `δ = 4πnh·cos(θ) / λ`：相邻光束的相位差
- `n`：腔内介质折射率
- `h`：腔长
- `θ`：入射角

#### 2. 自由光谱范围（FSR）

```
FSR = λ² / (2nh)
```

#### 3. 半高全宽（FWHM）

```
FWHM = FSR / ℱ
```

其中 `ℱ = π√F / 2` 为精细度。

#### 4. 品质因数（Q值）

```
Q = λ / FWHM = 2πnh / [λ(1-R)]
```

### 使用方式

```python
from src.interferometry.fp_cavity import FabryPerotCavity

cavity = FabryPerotCavity(
    reflectivity=0.95,     # 反射率
    cavity_length=1e-3,    # 腔长 (m)
    refractive_index=1.0,  # 折射率
    wavelength=632e-9,     # 工作波长 (m)
)

print(f"精细度: {cavity.finesse():.1f}")
print(f"FSR: {cavity.fsr()*1e9:.2f} nm")
print(f"FWHM: {cavity.fwhm()*1e9:.4f} nm")
```

---

## 模块四：Zernike像差仿真

### 数学与光学原理

**Zernike多项式**是一组在单位圆上正交的多项式，广泛用于光学波前像差的表征。

#### 1. Zernike多项式定义

Zernike多项式在极坐标下表示为：

```
Z_n^m(ρ, θ) = R_n^m(ρ) · cos(mθ)  或  R_n^m(ρ) · sin(mθ)
```

其中径向多项式为：

```
R_n^m(ρ) = Σ [(-1)^k · (n-k)! / (k! · ((n+m)/2-k)! · ((n-m)/2-k)!)] · ρ^(n-2k)
```

#### 2. 常见像差类型

| 序号 | 名称 | Zernike项 | 数学表达式 |
|------|------|-----------|------------|
| Z1 | 平移 | Z(0,0) | 常数 |
| Z2 | 倾斜X | Z(1,1) | ρ·cos(θ) |
| Z3 | 倾斜Y | Z(1,-1) | ρ·sin(θ) |
| Z4 | 离焦 | Z(2,0) | 2ρ²-1 |
| Z5 | 像散X | Z(2,-2) | ρ²·cos(2θ) |
| Z6 | 像散Y | Z(2,2) | ρ²·sin(2θ) |
| Z7 | 彗差X | Z(3,-1) | (3ρ³-2ρ)·cos(θ) |
| Z8 | 彗差Y | Z(3,1) | (3ρ³-2ρ)·sin(θ) |
| Z9 | 三叶草X | Z(3,-3) | ρ³·cos(3θ) |
| Z10 | 三叶草Y | Z(3,3) | ρ³·sin(3θ) |
| Z11 | 球差 | Z(4,0) | 6ρ⁴-6ρ²+1 |

#### 3. 波前叠加

任意波前可以表示为 Zernike 多项式的线性组合：

```
W(ρ, θ) = Σ a_i · Z_i(ρ, θ)
```

### 使用方式

```python
from src.wavefront.zernike import ZernikePolynomial

# 计算单个Zernike项
zernike = ZernikePolynomial(n=4, m=0)  # 球差
wavefront = zernike.evaluate(rho, theta)

# 多项叠加
from src.wavefront.visualization import plot_zernike_superposition
coefficients = {4: 1.0, 11: 0.5}  # Z4离焦 + Z11球差
plot_zernike_superposition(coefficients)
```

---

## 模块五：双目测距模块设计

### 数学与光学原理

**双目测距**基于三角测量原理，通过两个相机从不同视角观察同一目标，利用视差计算目标距离。

#### 1. 三角测量公式

```
Z = (B · f) / d
```

其中：
- `Z`：目标距离
- `B`：基线长度（两相机间距）
- `f`：相机焦距
- `d`：视差（同一目标在两像面上的像素差）

#### 2. 视差计算

```
d = (x_L - x_R) · (w / W_sensor)
```

其中 `x_L`、`x_R` 为目标在左右像面上的位置，`w` 为图像宽度（像素），`W_sensor` 为传感器宽度。

#### 3. 测距误差

对三角测量公式求微分，得到距离误差：

```
ΔZ = (B · f / d²) · Δd = Z² · Δd / (B · f)
```

相对误差为：

```
ΔZ/Z = Z · Δd / (B · f)
```

#### 4. 视场角

```
FOV_h = 2 · arctan(w · p / (2f))
FOV_v = 2 · arctan(h · p / (2f))
```

其中 `p` 为像素尺寸，`w`、`h` 为图像宽高（像素）。

#### 5. 可测距范围

- **最小测距**（视差 = 1像素）：`Z_min = B · f / p`
- **最大测距**（视差 = 0.1像素精度）：`Z_max = B · f / (0.1 · p)`

### 使用方式

```python
from src.imaging.stereo import StereoRangingSystem

system = StereoRangingSystem(
    baseline=0.065,        # 基线长度 (m)
    focal_length=0.008,    # 焦距 (m)
    pixel_size=3.45e-6,    # 像素尺寸 (m)
    image_width=1920,      # 图像宽度 (px)
    image_height=1080,     # 图像高度 (px)
)

# 计算视差
disparity = system.disparity_from_distance(5.0)

# 计算测距误差
error = system.range_error(5.0)
```

---

## 输出示例

### 菲涅尔透镜

| 文件名 | 说明 |
| ------ | ---- |
| `透镜设计总览.png` | 2×3布局总览：参数面板、环带半径曲线、相位剖面、截面结构、2D相位热力图 |
| `连续相位分布.png` | 连续包裹相位 2D 热力图 |
| `量化相位分布.png` | 8阶量化相位 2D 热力图 |
| `环带结构.png` | 菲涅尔透镜环带俯视图（蓝白交替） |

### 光栅衍射

| 文件名 | 说明 |
| ------ | ---- |
| `衍射角分布.png` | 衍射角与入射角/波长/光栅周期的关系曲线 |
| `衍射效率.png` | 衍射效率分布图 |

### F-P腔

| 文件名 | 说明 |
| ------ | ---- |
| `透射率与反射率.png` | 不同反射率下的透射率曲线 |
| `多光谱透射率.png` | 多光谱范围透射率分析 |

### Zernike像差

| 文件名 | 说明 |
| ------ | ---- |
| `Zernike36项概览.png` | 前36项像差 2D 热力图 |
| `Z4离焦3D.png` | 离焦像差 3D 曲面图 |
| `Z7彗差3D.png` | 彗差 3D 曲面图 |
| `Z8像散3D.png` | 像散 3D 曲面图 |
| `Z11球差3D.png` | 球差 3D 曲面图 |

### 双目测距

| 文件名 | 说明 |
| ------ | ---- |
| `光路布局.png` | 双成像单元光路布局图 |
| `测距误差分析.png` | 距离-视差关系与测距误差曲线 |

## 注意事项

- 图表使用中文字体（Microsoft YaHei），请确保系统已安装微软雅黑字体
- 所有示例脚本会自动创建 `figures/` 输出目录
- 参数单位统一使用国际单位制（m、rad 等）
- GUI程序运行时会阻塞终端，关闭窗口即可释放
- 菲涅尔透镜GUI的3D功能依赖 Plotly 和浏览器环境
