# 总体架构

```text
Stellarium / N.I.N.A. / KStars / Ekos / PHD2
                     |
       ASCOM / INDI (Phase 1: OnStepX)
                     |
             USB / Wi-Fi / UART
                     |
              ESP32 Controller
         +-------------+-------------+
         |                           |
   RA Step/Dir                     DEC Step/Dir
         |                           |
   TMC2209 / TMC5160             TMC2209 / TMC5160
         |                           |
      Stepper                     Stepper
         |                           |
       3:1 Belt                    3:1 Belt
         |                           |
   100:1 Harmonic               100:1 Harmonic
         |                           |
      RA Axis                     DEC Axis
         +---Home/Limit/Safety-------+
```

## 模块接口

- **机械**：RA 壳体、DEC 壳体、轴承/法兰、极轴高度调节座、方位微调座、Vixen 鞍座可独立替换。
- **电机**：步骤/方向接口为第一阶段边界。更换电机/减速器必须更新传动参数并重做限位验证。
- **电路**：电源输入保护、驱动器、主控、传感器、USB/网络分层；针对零位传感器定义默认故障状态。
- **软件**：运动学、设备抽象层、连接协议、可观测性、上位机分离。第一阶段不修改上游 OnStepX 代码。

## 控制与安全原则

- 设备端必须具有可独立于上位机通信正常与否执行的安全停止手段。
- 软件限位 **不替代** 物理碰撞分析，断电保护需要单独评审。
- 断电保持位置、编码器闭环和 PEC 是可选的后期增强，不属于第一版已实现功能。
