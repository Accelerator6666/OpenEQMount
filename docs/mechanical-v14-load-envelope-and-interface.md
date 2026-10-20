# OpenEQMount V1.4 — ROT 载荷包络与可更换相机安装板（数字 Gate A）

> **NOT FOR CAMERA INSTALLATION, MACHINING RELEASE OR MOTOR ENERGIZATION.**
> 本版本仅改善参数化估算、概念几何、测试与装配预览。不能用计算出的力代替轴承 OEM 许用载荷、刚度、实物跌落测试或工程认证。

## 1. 为什么增加 V1.4

V1.3 有两只 **6808-2RS（40×52×7 mm）** 候选轴承、轴向参考间隔 **30 mm**、概念旋转输出板，但真实相机+镜头质量、重心、镜头脚、夹具和独立防坠都未知。最危险的不只是质量，而是悬臂载荷放大：重心越靠近镜头前端，两只轴承的支撑反力越大。不得默认 3–5 kg 目标已实现。

## 2. 可填写的载荷输入与简化方程

局部 ROT 轴取 **Z**。轴承中心 `z=10.5`、`40.5 mm`，相机安装面 `z=75 mm`。输入：

- `mass_kg`：**含相机、镜头、镜头脚、夹具、线缆附加载荷的合质量**（在实物称重后代入）；
- `cg_from_mount_mm`：安装面到整套装备重心沿光轴方向的距离（mm）；
- `eccentricity_mm`：重心距旋转轴的偏心距离（mm）；
- `illustration_multiplier`：仅用于敏感性比较的 1×/2×等示例，不是结构安全系数。

静力学示意，`F=m*g*k`，`zCG=75+cg_from_mount`，两支撑间距 `L=30mm`：

- 假设重力垂直光轴，且作用于轴向悬臂：上轴承反力大小 `Rupper = F*(zCG-10.5)/L`，另一轴承相反向反力 `Rlower = F*(zCG-40.5)/L`。**这些不是所有姿态下的合成轴承载荷，也未纳入真实内外圈受力分配**；
- 重心相对两轴承中点的倾覆力矩参考上界 `M = F*sqrt(((zCG-25.5)/1000)^2 + (eccentricity/1000)^2)`；
- 光轴滚转静态重力矩估算 `Trot = F*eccentricity/1000`；4:1 同步带传动下的理想电机静态力矩 `Tmotor=Trot/4`。**未包括效率、摩擦、加速转矩和电机工作电流衰减**。

这些独立工况不可简单合并认定为满足额定载荷。任一值不足以决定安全性；轴承静/动许用载荷、倾角刚度、保持架、预紧、座孔、温升、寿命和轴/机架挠度都没有建模。

### 示例（非载荷额定值）

`4 kg / 80 mm 轴向重心距 / 20 mm 偏心 / 1×`：`F=39.23 N`，两轴承相反向径向支撑反力约 **188.94 N 和 149.71 N**，滚转静态重力矩 **0.785 Nm**，4:1 理想电机保持力矩 **0.196 Nm**。实际电机扭矩要求只会更严格，不能据此购买某个步进电机并声明足够。

生成包括 `3/4/5 kg × 40/80/120 mm × 0/20/40 mm × 1/2 倍` 的 **54 个仅供研究的 CSV 载荷工况**：

```bash
python tools/rotator_load_cases.py --out hardware/cad/v14_generated \
  --mass-kg 4 --cg-from-mount-mm 80 --eccentricity-mm 20
python hardware/cad/generate_v14_load_fixture.py --out hardware/cad/v14_generated
python tools/dfam_gate_v14.py --dir hardware/cad/v14_generated
```

## 3. 装配接口与颜色

新增金属 **可更换候选板**：Ø118×8 mm 环形接口，与旧的 6×M4 PCD88 候选 ROT 输出孔相邻；上层候选 2×M6 长孔，名义孔距 50–70 mm。**这是通用板坯的研究尺寸，不等同于 Arca-Swiss、镜头脚或任何厂家夹具真实安装标准。** 旧的 V1.3 2×M6 固定孔板在 V1.4 总装视图中已被替换，不再重叠展示。正式加工须以具体已采购夹具数据、材料、螺纹有效长度和防松方案重新设计。

紫粉色相机/镜头外形是**用于展示占用空间的虚构模型**，绝非可打印或可安装的零件。相机端独立锚点仍未连接实物相机笼；没有完整钢索，也没有通过 ROT ±150°、RA/DEC 全姿态和过中天的走线检查。要维持防坠独立性，钢索一端必须通过独立于相机夹具的可靠连接固定到实际相机/镜头脚/笼，另一端连接经试验的固定金属架；不得将同一失效紧固件作为两条安全路径。

## 4. 真实制造与验证前的阻断门槛

1. 用户称重，并记录真实 **相机机身、镜头、镜头脚、配重和导星附件组合**及 CG 三维偏移；记录三轴正负极限与翻转姿态。
2. 核对 **6808 OEM 图纸**、承载/力矩/寿命、预紧和公差；必要时改用成对角接触/交叉滚子支撑，不能仅凭标准尺寸认定承载能力。
3. 确定真实金属快装夹 / 镜头脚，按其紧固孔系重新出正式 2D 尺寸公差图、锁紧扭矩和防松措施。
4. 将防坠钢索、端头、连接件、双端独立锚点加入 CAD，检查最松/最紧位置的最小弯曲半径、缠绕、滑移和角度范围；执行独立实物防坠试验。
5. 编制实体受力校核、轴承内圈的螺纹/螺母、防松和轴向预紧公差链；现场 Gate B 配合检查、Gate C 静载/冲击/高低温/长期锁紧测试。
6. 通过所有 Gate 后方可进入**无载的受控电机台架**、再最终考虑相机载荷；当前 `safe_to_energize=false` 和 `payload_approved=false`。

## 5. 文件

- `hardware/cad/v14_generated/OpenEQMount_V14_THREE_AXIS_CAMERA_LOAD_ENVELOPE_UNQUALIFIED.step`：68 实体 FreeCAD 总装（含两件虚构外形）；
- `hardware/cad/v14_generated/v14_METAL_SLOTTED_CAMERA_VENDOR_FIXTURE_STOCK_UNQUALIFIED.step`：可调整候选金属板；
- `hardware/cad/v14_generated/rotator_load_cases_ILLUSTRATIVE.csv`：54 个研究工况；
- `hardware/cad/v14_generated/rotator_load_report.json`：参数化模型及明确的不许可标志；
- `hardware/cad/v14_generated/v14_NONLOAD_CG_RANGE_REFERENCE_COUPON_PRINT_FLAT.stl`：非承力 PETG 校准检具；
- `.github/workflows/cad-v14.yml`：可重复生成和 GitHub CI。*通过 Gate A 绝不等于能用。*
