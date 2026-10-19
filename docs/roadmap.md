# Roadmap

## M0 — 项目基础
- [x] 仓库模板与基础 README
- [x] 传动比数学计算和 CI 单元测试
- [ ] 确认摄影器材、载荷、焦距、预算、加工能力
- [ ] 选定代码、硬件、文档许可证

## M1 — 电机/控制台架
- [ ] 最终确定 ESP32 开发板及驱动器
- [ ] 连接 RA、DEC 电机，低速/高速运动测试
- [ ] 单轴恒星时速率稳定性测试
- [ ] 回零、限位、急停基本测试

## M2 — DfAM 受控机械 CAD
- [x] 强制 DfAM 建模规范与逐件审计清单
- [x] V0.3 承力连接盲插孔改为金属贯穿螺栓方案、打印平面归一化
- [x] GitHub Actions 数字几何/元数据 Gate A
- [ ] 所有零件切片悬垂与层间载荷逐件审查 Gate B
- [ ] 标定孔系公差、拆装及螺栓操作空间 Gate B
- [ ] 静载/振动/蠕变/失效保护实测 Gate C

- [ ] 选定减速器、轴承和同轴支撑方案
- [ ] 参数化 RA/DEC 模块建模
- [ ] 极轴高度/方位调节机构
- [ ] 输出 STEP、装配图、BOM

## M3 — 双轴原型
- [ ] 加工/打印并装配机械样机
- [ ] 电控与走线固定
- [ ] GoTo/限位/停车完整测试

## M4 — 软件与实星联调
- [ ] ASCOM/INDI 兼容测试
- [ ] PHD2 导星测试与数据归档
- [ ] 周期误差、振动、负载曲线报告

## M5 — 可复现发布
- [ ] 零件/加工图完整
- [ ] KiCad 自研控制板（可选）
- [ ] Release 包含源文件与物料表
- [ ] 发布完整装配教程与安全声明


## V0.4 — DfAM RA–DEC frame
- [x] Generate provisional orthogonal metal-load path and nonstructural FDM covers.
- [x] Add parameterized STEP/STL and automated Gate A for V0.4.
- [ ] Validate OEM fastener phase, bolt engagement, real angle profiles and shim gaps.
- [ ] Complete Gate B slicer/fit and Gate C mechanical/safety qualification.
- [ ] Design polar wedge, wave-generator shaft, counterweight, camera saddle and independent retention.


## V0.5 Gate A: 2026-10-19

- [x] Prototype polar wedge metal load-path CAD; 25–45° tilt and ±5° azimuth geometry; editable CadQuery and STEP
- [x] 5 bed-aligned DfAM NONSTRUCTURAL FDM STL, Gate A mesh validation, tests, BOM and CAD workflow
- [ ] **V0.6 blocking safety design:** fixed-RA-housing reducer adapter; positive mechanical altitude lock and physical stops; metal redundant retention
- [ ] V0.6 engineering: M8 jack/buckling/preload, axially supported azimuth turntable, actual tripod adapter
- [ ] Gate B slicer, measurement and bench assembly; Gate C structural + creep + shock + fail-safe tests


## V0.6 — 金属锁紧、止挡与通用三脚架接口（Gate A CAD 已完成）

- [x] 独立 M8 锁紧弧槽与 M6 限位弧槽的 25°–45° 数字轨迹验证
- [x] 金属侧板与顶板连接耳座、通用金属三脚架接口参考 CAD
- [x] DfAM 4 件非承力护件、校准检具，自动 Gate A 审核
- [ ] 确认真实三脚架与谐波减速器（尤其 RA 固定机壳端）安装尺寸
- [ ] 金属防坠独立约束、销轴保持、螺栓长度、锁紧力和力矩选型
- [ ] 实物装配、打印公差 Gate B，负载/长期蠕变/温度/振动 Gate C


## V0.7 — RA 机壳侧支座 + RA/DEC 断开动力同步带台架（Gate A 已完成）

- [x] 修正与 V0.6 纬度锁紧耳座冲突的极轴顶板接口；新增 4 个候选金属钻孔
- [x] RA 静止机壳侧法兰 + 双层金属立柱与可重复生成的装配 STEP
- [x] RA/DEC 各一套隔离式 GT2 60T/20T 传动间距参考台架和 NEMA17 可调安装槽
- [x] 3 件非承力 DfAM 打印检具，自动单体 STL Gate A，8 项几何与运动学测试
- [ ] 获取 **真实** CSF-17/14 2UH 波发生器输入接口和固定端角度/预紧要求
- [ ] 设计金属输入联轴器、实际支承轴、滑轮定位与防脱、皮带张力及防尘安全护罩
- [ ] 装配实物、完整干涉检查、完整金属防坠链路以及 DfAM Gate B/C 审核

## V1.0 ROT 金属轴承台架（数字 Gate A）
- [x] 双 6808-2RS 候选轴承、金属中空旋转轴和金属轴承座参考
- [x] NEMA17 张紧板、候选限位板和三个 DfAM 非承力校准件
- [x] STEP/STL、零件测试、DfAM Gate A 自动构建
- [ ] 实际 DEC 输出至旋转器的金属连接、相机镜头夹持及独立防坠
- [ ] 轴承弯矩、倾角、寿命，皮带齿形、限位与电气安全验证
- [ ] Gate B / Gate C 实测通过后方可申请安全载荷
