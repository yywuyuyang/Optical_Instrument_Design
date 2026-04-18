# 光学仪器设计仿真软件

基于 Python 的光学仪器设计与仿真平台，涵盖菲涅尔透镜设计、光栅衍射分析、F-P腔透射分析、Zernike像差仿真和双目测距模块设计五大核心功能。

## 功能模块

### 1. 菲涅尔透镜设计 (`src/fresnel/`)

针对波长 632nm 的激光，设计焦距 100mm 的菲涅尔透镜。

- 计算环带半径分布
- 生成相位分布图（连续/量化）
- 可视化环带结构
- 计算刻蚀深度、F数、焦点光斑尺寸等关键参数
- **交互式GUI**：支持参数实时修改、Plotly WebGL加速3D可视化

### 2. 平面光栅衍射分析 (`src/grating/`)

根据入射角、波长、光栅周期计算衍射角和衍射效率。

- 多衍射级次的衍射角计算
- 正弦相位光栅和振幅型光栅的效率计算
- 矩形相位光栅的傅里叶级数效率公式
- 衍射角/效率随入射角、波长、光栅周期的变化曲线

### 3. F-P腔透射分析 (`src/interferometry/`)

分析 Fabry-Perot 腔的透射光场特性。

- 不同反射率下的透射率曲线
- 不同光谱范围的透射率分析
- 精细度、自由光谱范围(FSR)、半高全宽(FWHM)、Q值计算
- 共振波长定位
- **GUI交互工具**：支持参数实时修改、多R值对比、光谱分析

### 4. Zernike像差仿真 (`src/wavefront/`)

基于 Zernike 多项式（前36项）的像差表征与可视化。

- 前36项 Zernike 多项式的空间分布
- 2D 热力图与 3D 曲面图可视化
- 涵盖离焦、像散、彗差、球差等经典像差类型
- **GUI交互工具**：支持单项显示、多像差叠加、自定义保存路径

### 5. 双目测距模块设计 (`src/imaging/`)

基于人眼视觉感知距离原理的双成像单元测距模块。

- 视差-距离关系计算
- 测距误差分析（绝对误差/相对误差）
- 基线长度对视差的影响
- 光路布局可视化

## 项目结构

```
Optical_Instrument_Design/
├── config/                     # 配置文件
│   ├── default_params.yaml     # 默认参数配置
│   └── optics_style.mplstyle   # Matplotlib 样式（中文字体）
├── dist/                       # 打包后的可执行文件
│   ├── FPCavityAnalyzer.exe   # F-P腔分析 GUI 独立程序
│   └── ZernikeViewer.exe       # Zernike GUI 独立程序
├── examples/                   # 示例脚本
│   ├── example1_fresnel.py     # 菲涅尔透镜示例
│   ├── example2_grating.py     # 光栅衍射示例
│   ├── example3_fp_cavity.py   # F-P腔示例
│   ├── example4_zernike_interactive.py  # Zernike CLI交互工具
│   ├── example5_stereo.py      # 双目测距示例
│   ├── zernike_gui.py          # Zernike GUI交互工具
│   └── fresnel_gui.py          # 菲涅尔透镜设计GUI（Plotly渲染）
├── figures/                    # 输出图像
│   ├── fresnel/
│   ├── grating/
│   ├── imaging/
│   ├── interferometry/
│   └── wavefront/
├── src/                        # 核心源代码
│   ├── fresnel/                # 菲涅尔透镜模块
│   ├── grating/                # 光栅衍射模块
│   ├── interferometry/         # F-P腔模块
│   ├── wavefront/              # Zernike像差模块
│   └── imaging/                # 双目测距模块
├── requirements.txt            # Python 依赖
├── ZernikeViewer.spec          # PyInstaller 打包配置
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
| hcipy      | >=0.7.0  | 光学仿真工具             |
| LightPipes | >=2.0    | 光束传播仿真             |
| PyYAML     | >=6.0    | 配置文件解析             |
| tqdm       | >=4.60   | 进度条显示               |
| pytest     | >=7.0    | 单元测试                 |

## 快速开始

### 运行示例

```bash
# 激活环境
conda activate optics_sim

# 运行各个模块的示例
python examples/example1_fresnel.py     # 菲涅尔透镜设计
python examples/example2_grating.py     # 光栅衍射分析
python examples/example3_fp_cavity.py   # F-P腔透射分析
python examples/example4_zernike_interactive.py  # Zernike CLI交互
python examples/example5_stereo.py      # 双目测距模块

# 运行Zernike GUI交互工具
python examples/zernike_gui.py

# 运行菲涅尔透镜设计GUI（Plotly 3D渲染）
python examples/fresnel_gui.py
```

运行后生成的图像将保存在 `figures/` 目录下对应的子文件夹中。

### F-P腔分析GUI

#### 启动方式

**方式一：Python脚本**

```bash
python examples/fp_cavity_gui.py
```

**方式二：独立可执行文件**
直接双击运行 `dist/FPCavityAnalyzer.exe`（无需安装Python环境）

#### 功能说明

1. **参数设置**

   - 反射率 R：镜面反射率(0~1)，越高精细度越大
   - 腔长 h：两镜面间距，决定FSR
   - 折射率 n：腔内介质折射率
   - 入射角 theta：光线入射角度
   - 点击"?"按钮查看参数说明
2. **多R值对比**

   - 勾选多个反射率值进行对比
   - 查看不同反射率下的透射光谱
   - R值越高，透射峰越尖锐，精细度越大
3. **光谱分析**

   - 精细度与反射率的关系曲线
   - 可见光范围(400-800nm)透射特性
   - 窄带范围±2%透射特性
   - 近红外范围(1000-2000nm)透射特性
4. **计算结果**

   - 精细度 F
   - 自由光谱范围(FSR)
   - 半高全宽(FWHM)
   - Q值
   - 共振波长定位
5. **保存图像**

   - 点击"保存当前图像"按钮
   - 支持PNG和PDF格式，300 DPI高清输出

### Zernike GUI 使用说明

#### 启动方式

**方式一：Python脚本**

```bash
python examples/zernike_gui.py
```

**方式二：独立可执行文件**
直接双击运行 `dist/ZernikeViewer.exe`（无需安装Python环境）

#### 功能说明

1. **单项显示模式**

   - 从列表中选择Zernike项（Z1-Z36）
   - 支持2D热力图、3D曲面图、2D+3D组合显示
2. **叠加显示模式**

   - 点击"+ 添加项"添加叠加项
   - 下拉框选择像差类型，输入框填写系数
   - 支持多像差线性叠加，结果自动归一化
   - 点击"加载预设"快速加载球差+离焦组合
3. **参数说明**

   - **编号**：Zernike多项式序号(Z1-Z36)，代表不同像差类型
   - **系数**：该项像差的权重，决定其在总波前中的贡献比例
   - **注**：结果自动归一化到[-1,1]，系数仅反映相对比例
4. **保存图像**

   - 点击"保存图像"按钮
   - 选择本地路径和文件名
   - 支持PNG格式，300 DPI高清输出

#### 常见叠加组合

| 组合类型      | 项           | 系数            | 说明             |
| ------------- | ------------ | --------------- | ---------------- |
| 初级球差+离焦 | Z4 + Z11     | 1.0 + 0.5       | 模拟最佳焦面     |
| 彗差+像散     | Z7 + Z5      | 0.8 + 0.3       | 模拟轴外像差     |
| 复杂像差      | Z4+Z5+Z7+Z11 | 1.0+0.5+0.3+0.2 | 接近实际光学系统 |

### 菲涅尔透镜设计GUI

#### 启动方式

```bash
python examples/fresnel_gui.py
```

#### 功能说明

1. **参数输入**

   - 波长 λ (nm)：激光波长，决定相位周期和刻蚀深度
   - 焦距 f (mm)：焦点到透镜的距离
   - 直径 D (mm)：透镜通光孔径
   - 折射率 n：透镜材料折射率（如玻璃~1.5）
   - 点击"?"按钮查看参数说明
2. **实时可视化（Plotly WebGL 加速）**

   - **3D透镜结构图**：采用 Plotly WebGL 渲染，GPU硬件加速
   - **流畅交互**：鼠标拖拽旋转、滚轮缩放、右键平移，全程60fps无卡顿
   - **浏览器打开**：点击按钮在浏览器中打开完整交互式3D模型
   - **HTML导出**：支持导出为独立HTML文件，无需Python环境即可查看
   - **设计总览图**：包含参数面板、环带半径曲线、相位分布、截面结构、2D相位热力图
3. **设计结果**

   - 自动计算：理论环带数、刻蚀深度、F数、光斑尺寸等
   - 制造约束分析：可制造环带数（基于最小加工间距）、有效半径占比
4. **图像说明**

   - 左侧面板提供每张图像的详细解释
   - 包括物理意义、数学公式、制造约束说明
5. **保存功能**

   - 支持保存3D结构和设计总览为PNG图片
   - 可选择本地路径和文件名
   - 支持导出 Plotly 交互式 HTML 文件

各模块支持自定义参数，例如：

```python
from src.fresnel.lens import FresnelLens

# 自定义菲涅尔透镜参数
lens = FresnelLens(
    focal_length=0.1,      # 焦距 (m)
    wavelength=632e-9,     # 波长 (m)
    radius=0.0125,         # 半径 (m)
    n=1.5,                 # 折射率
)

# 查看设计参数
print(f"环带数量: {lens.num_rings()}")
print(f"刻蚀深度: {lens.etch_depth()*1e9:.1f} nm")
```

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
- 菲涅尔透镜GUI的3D功能依赖 Plotly 和浏览器环境，首次使用需安装 plotly 包
