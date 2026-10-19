# V0.8 — 单文件整机概念装配 (FreeCAD STEP)

**版本说明：仅整机布局预览，未取得制造、负载或通电许可。**

## 为什么有这个文件

V0.4–V0.7 原来是各个子组件、零件和检具的独立 STEP。首次查看时，它们各有局部坐标系，不能直接将文件全选拖进 FreeCAD 并认为已经完成真实装配。本版本统一转换坐标，提供 **一个 FreeCAD 可以直接打开的 STEP**，内含分名可选择的零件。

## 文件

- [`hardware/cad/v08_generated/OpenEQMount_V08_WHOLE_MOUNT_CONCEPT_UNQUALIFIED.step`](../hardware/cad/v08_generated/OpenEQMount_V08_WHOLE_MOUNT_CONCEPT_UNQUALIFIED.step) — 35° 纬度时的整机概念装配视图（单个 STEP，多个可选择实体）
- [`hardware/cad/v08_generated/OpenEQMount_V08_WHOLE_MOUNT_CONCEPT.png`](../hardware/cad/v08_generated/OpenEQMount_V08_WHOLE_MOUNT_CONCEPT.png) — 可快速浏览的三维预览图
- [`hardware/cad/v08_generated/manifest.json`](../hardware/cad/v08_generated/manifest.json) — 采用/替代的零件及未解决的工程风险
- `hardware/cad/generate_v08_concept_assembly.py` — 参数化整机摆位生成器

## 坐标与版本选择

- 以 V0.5 的三脚架底板坐标作为全局基准：平台在 XY 平面，铰点为 `(-61,0,29) mm`。
- V0.6 的金属锁紧板、销轴和改进方位底座代替原来的 V0.5 方位板。
- V0.7 的**开有新增孔位的极轴顶板**代替原版 V0.5 顶板，RA 固定机壳支座随极轴台以 35° 角旋转。
- V0.4 正交框架的 RA 输出面 `Z=0` 对齐至 V0.7 RA 减速器空间包络的末端 `Z=138 mm`，然后同样绕极轴铰点旋转。
- DEC 减速器仅以直径/长度近似包络显示；不表示其真实安装界面已确定。
- 避免把 V0.5 和 V0.7 重复的顶板、两个备选三脚架转接板一起装入；没有通过装配验证的 V0.7 两套独立同步带试验台架**不放入整机**。
- 平板试片、孔位检具、离机护盖等**不会**被错误放置进整机；其 STL 仍在各自的 v04~v07 文件夹内。

## Windows / FreeCAD 使用

1. 从 GitHub 下载 `hardware/cad/v08_generated/OpenEQMount_V08_WHOLE_MOUNT_CONCEPT_UNQUALIFIED.step`。
2. FreeCAD → 文件 → 打开 → 选择 `.step`。
3. 按 `V,F`（依次按下两个键）或使用“适合全部”将整机居中。
4. 展开左侧模型树即可逐项选择、隐藏部件或测量尺寸。
5. 如果需要将工作空间保存为 FreeCAD 文件，选择“另存为” `.FCStd`。

## 安全边界

这个视图**不是已经解决全部装配关系的完整机**：未选型/核对减速器后法兰的孔角、波发生器输入轴、同步带与电机轴、RA 输出和 DEC 安装过渡、防坠连接、工具及螺栓操作空间、各极端角度下整机干涉、实际 FDM Gate B/C。**不得依据该视图采购全部零件、投入加工或挂相机负载。**

所有结构打印件继续受 [`docs/dfam-design-standard.md`](dfam-design-standard.md) 约束。这里的 `.step` 是综合预览，不是 FDM 打印 STL。
