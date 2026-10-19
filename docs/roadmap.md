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
