# 固件路线

## Phase 1：OnStepX 生态验证

OnStepX 官方：https://github.com/hjd1964/OnStepX

在自己的仓库仅保留：电控适配方案、自己编写的配置说明、编译步骤、验证记录和版本/commit 固定值。上游源码不要直接复制进来而忽略许可证。应核对上游 GPL-3.0 义务。

示例传动参数（**仅适用于假设的 200 步/转电机、64 微步、100:1 谐波减速器和 3:1 皮带；不是可直接编译的完整 Config.h**）：

```text
# Example (numbers only):
RA steps/degree   = 200 * 64 * 100 * 3 / 360 = 10666.666667
DEC steps/degree  = 200 * 64 * 100 * 3 / 360 = 10666.666667
RA sidereal step/s= 200 * 64 * 100 * 3 / 86164.0905 = 44.566129
```

真实微步设置、引脚映射、加速度、最大速度、限位极性、跟踪方向、固件版本均须在台架上验证。已有非易失性运行时设置可能覆盖编译时默认参数。

## Phase 2：可选自主固件

按实际需要拆成运动学、实时脉冲调度、驱动抽象、坐标变换、协议、状态机/安全、日志模块。初期不应为了原创而牺牲 GoTo 与导星联调速度。

## 后续软件标准

- ASCOM Alpaca: https://ascom-standards.org/（官方建议的跨平台新接口）
- INDI: https://github.com/indilib/indi
- Stellarium/N.I.N.A./KStars/Ekos/PHD2 的实测兼容矩阵待建立。
