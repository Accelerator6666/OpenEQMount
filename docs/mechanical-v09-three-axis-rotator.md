# V0.9 — 三轴联动 RA + DEC + ROT（DfAM Gate A）

> 该版本包含运动学仿真、相机旋转器空间 CAD 和完整三轴概念总装 STEP。**没有可实际通电的三轴控制器或通过承载验证的相机旋转器**。任何 STEP 不得直接作为加工批准图纸；所有打印 STL 为非承力检具。

## 运动学定义

- **RA**：赤经极轴旋转，补偿地球自转。恒星时角速度 `360/86164.0905 deg/s`，只作为理想参考。实际驱动、纠偏、导星与恒星坐标转换尚未实现。
- **DEC**：赤纬轴旋转，轴线与 RA 极轴垂直。
- **ROT**：绕**相机光轴**的滚转，用于目标构图角度（Position Angle, PA）。**ROT 光轴与 DEC 轴互相垂直**，不是共轴。DEC 姿态改变时光轴也随之倾转。
- 正确极轴对准的德式赤道仪不需要把 ROT 当作恒星跟踪的持续消旋轴；不能把 ALT-AZ 使用的消旋速率套用到 GEM。
- 自动翻中天（meridian flip）后需重新核对镜像与目标 PA；不得无校准直接假设相机角度不变。

`tools/three_axis_motion.py` 是无硬件 IO 的软件模拟器。它支持 `JointPose(RA,DEC,ROT)`、同步平滑位置插值、三轴速度上限及规划前的 homed/enabled 前置检查。同步平滑运动的**最大速度**通过 `1.5 × 距离 / 轴速度上限` 限制；不保证加速度、扭矩、步进丢步或电子安全。

ROT 机械角暂按 `[-160°, +160°]` 规划；**绝不能在传给硬件时按 360° 取模以规避线缆限制**。PA 与 ROT 机械角需要通过实际构图/解算标定正反转、零位、跨 0° 别名及中天翻转。

## ROT 机械布局（全部为候选尺寸，不是已购产品的真实接口）

| 项目 | 空间概念尺寸 / 方案 | 状态 |
|---|---|---|
| 金属固定座外径/中空孔 | Ø138 / Ø92 mm, 厚 6 mm | 参考占位 |
| 金属转动法兰外径/中空孔 | Ø118 / Ø76 mm, 厚 6 mm | 参考占位 |
| 旋转轴承空间包络 | Ø112 / Ø82 mm, 厚 11 mm | **没有选定轴承规格** |
| 金属独立防坠保持环 | Ø134 / Ø110 mm, 厚 4 mm | 尚未完成受力/间隙设计 |
| 同步带节圆示意 | GT2 180T / 20T = 9:1 | 仅节圆、非齿形、非可制造带轮 |
| 相机滚转行程 | ±160° 软件候选 | 未装实体硬限位/线缆测试 |
| 3D 打印件 | 非承力标尺圈、走线试片、孔径试片（共 3 件） | PETG 打印公差验证 |

## 3D 打印 DfAM 条款

- 每个打印件平放于 XY 平面，STL 底面 Z=0，不把层间粘结作为相机、光学镜筒或旋转轴承的承载/防坠路径。
- 所有相机固定、轴承夹持、带轮扭矩与防坠路径必须经过设计的**金属件**，且有独立冗余防坠与紧固件防松方案。
- 打印件只允许用于实际尺寸标定、模型摆位和走线样板；不允许作为通电驱动的护罩，直到切片审查、干涉验证及实体隔离方案完成。
- Gate A 测试检查封闭 STL、单体网格、Z=0 打印方向、220×220 台面和每件 DfAM 记录。Gate B 切片和装配、Gate C 载荷/振动/温度/蠕变和失效保护仍为 **Pending**。

## 三轴接口及安全先决条件

1. 选定真实 DEC 减速器，确认**旋转输出端**的安装面与连接孔位（不可使用 DEC 固定机壳充当转动端）。
2. 明确相机/镜头承载方式、镜头重心、光轴高度与 ROT 的轴承负荷；光轴不等于 DEC 转轴。
3. 选定带完整数据手册的薄截面轴承/交叉滚子轴承，设计金属独立轴向防坠与末端限位。
4. 根据电机扭矩和速度选步进驱动，完成真实节圆带轮、皮带包角/张紧、护罩、零点开关、双向限位和安全断电。
5. 供电/USB/相机控制线需要足够的独立应力释放与弯曲余量；无限旋转必须有经测试的滑环/穿轴走线系统。
6. 将物理 HOME / LIMIT / ESTOP / WATCHDOG 加入电机控制固件后，才考虑无载台架通电；模拟器的 homed=True 不代表物理检测。
7. 参考软件接口：[ASCOM Alpaca Rotator](https://ascom-standards.org/alpyca/alpaca.rotator.html)、[INDI Rotator](https://docs.indilib.org/interfaces/indirotatorinterface.html)；本仓库尚**没有实现标准驱动**。

## Windows 上使用 FreeCAD

- 用 FreeCAD 打开 `hardware/cad/v09_generated/OpenEQMount_V09_THREE_AXIS_MOUNT_CONCEPT_UNQUALIFIED.step` 可看到 RA、DEC、ROT **概念总装**。这里 ROT 悬浮在尚未设计的 DEC-相机鞍座位置，不能误认为螺栓连接已完成。
- `OpenEQMount_V09_ROT_AXIS_ONLY_UNQUALIFIED.step` 仅显示 ROT 模块，不包含真正相机转接环。
- STL 仅可导入 OrcaSlicer 做 DfAM Gate B 前的尺寸与切片审查。

## 测试 / 构建

```bash
python -m pip install 'cadquery>=2.5,<3' pytest trimesh
python -m pytest -q tests/test_v09_three_axis_motion.py tests/test_v09_rotator_cad.py
python hardware/cad/generate_v09_rotator.py --latitude 35 --out hardware/cad/v09_generated
python tools/dfam_gate_v09.py --dir hardware/cad/v09_generated --report hardware/cad/v09_generated/dfam-gate-report.json
```
