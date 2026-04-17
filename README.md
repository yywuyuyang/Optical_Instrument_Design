# 光学仪器设计仿真软件

基于 Python 的光学仪器设计与仿真平台，涵盖菲涅尔透镜设计、光栅衍射分析、F-P腔透射分析、Zernike像差仿真和双目测距模块设计五大核心功能。

## 功能模块

### 1. 菲涅尔透镜设计 (`src/fresnel/`)

针对波长 632nm 的激光，设计焦距 100mm 的菲涅尔透镜。

- 计算环带半径分布
- 生成相位分布图（连续/量化）
- 可视化环带结构
- 计算刻蚀深度、F数、焦点光斑尺寸等关键参数

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

### 4. Zernike像差仿真 (`src/wavefront/`)

基于 Zernike 多项式（前36项）的像差表征与可视化。

- 前36项 Zernike 多项式的空间分布
- 2D 热力图与 3D 曲面图可视化
- 涵盖离焦、像散、彗差、球差等经典像差类型

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
├── examples/                   # 示例脚本
│   ├── example1_fresnel.py     # 菲涅尔透镜示例
│   ├── example2_grating.py     # 光栅衍射示例
│   ├── example3_fp_cavity.py   # F-P腔示例
│   ├── example4_zernike.py     # Zernike像差示例
│   └── example5_stereo.py      # 双目测距示例
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

| 包 | 最低版本 | 用途 |
|---|---|---|
| numpy | >=1.21 | 数值计算 |
| scipy | >=1.7 | 科学计算（Bessel函数等） |
| matplotlib | >=3.5 | 2D/3D 可视化 |
| plotly | >=5.0 | 交互式可视化 |
| hcipy | >=0.7.0 | 光学仿真工具 |
| LightPipes | >=2.0 | 光束传播仿真 |
| PyYAML | >=6.0 | 配置文件解析 |
| tqdm | >=4.60 | 进度条显示 |
| pytest | >=7.0 | 单元测试 |

## 快速开始

### 运行示例

```bash
# 激活环境
conda activate optics_sim

# 运行各个模块的示例
python examples/example1_fresnel.py     # 菲涅尔透镜设计
python examples/example2_grating.py     # 光栅衍射分析
python examples/example3_fp_cavity.py   # F-P腔透射分析
python examples/example4_zernike.py     # Zernike像差仿真
python examples/example5_stereo.py      # 双目测距模块
```

运行后生成的图像将保存在 `figures/` 目录下对应的子文件夹中。

### 自定义参数

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
- 相位分布图（连续/8阶量化）
- 环带结构图

### 光栅衍射
- 衍射角与入射角/波长/光栅周期的关系曲线
- 衍射效率分布图

### F-P腔
- 不同反射率下的透射率曲线
- 精细度与反射率的关系
- 多光谱范围透射率分析

### Zernike像差
- 前36项像差 2D 热力图
- 典型像差（离焦、彗差、像散、球差）3D 曲面图

### 双目测距
- 光路布局图
- 距离-视差关系曲线
- 测距误差分析

## 注意事项

- 图表使用中文字体（SimHei），请确保系统已安装黑体字体
- 所有示例脚本会自动创建 `figures/` 输出目录
- 参数单位统一使用国际单位制（m、rad 等）
