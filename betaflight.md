# Betaflight 刷机与起步调参

适用于 Whoop-65B（1S 有刷 AIO）。不同品牌 AIO 的目标名（target）不同，**以商家说明书 / 板面丝印为准**。

## 1. 软件准备

1. 安装 [Betaflight Configurator](https://github.com/betaflight/betaflight-configurator/releases)（建议较新稳定版）。  
2. 驱动：Windows 下部分 F411/AT32 需安装 DFU 或厂商 USB 驱动；插上 AIO 后设备管理器能识别串口或 DFU。  
3. 准备匹配的 USB 线（须能传数据，非仅充电线）。

## 2. 刷固件

1. Configurator → **Firmware Flasher**。  
2. 选择与你的 AIO 一致的 **Target**（商家文档会写，例如某 `CRAZYBEEF4` / `BETAFPVF411` / AT32 系列名等——**不要猜错**）。  
3. 勾选需要的协议支持（ELRS/CRSF 通常已含）；Cloud build 按提示选 IMU 等选项（若商家给了 cloud build 链接，优先用）。  
4. 按板子进入 DFU/Boot（常见：按住 Boot 再插 USB，或双击复位）。  
5. Load Firmware → Flash。  
6. 刷完重新 Connect。

若商家提供「已刷好 ELRS + 有刷」固件包，可按其文档刷入，再按下文检查配置。

## 3. 首次连接检查

连接后确认：

- 顶部电池图标在插电池时可读取电压（USB 供电时可能无 VBAT）。  
- Setup 页 3D 模型随倾斜正确运动；不对则调整 board alignment 或重装方向。  
- 加速度计：**Calibrate Accelerometer**（机身水平、静止）。

## 4. 端口与接收机（ELRS / CRSF）

### 板载 ELRS

1. 按 AIO 说明书绑定：遥控器与板载 RX 使用相同 binding phrase，或按键进入对码。  
2. Betaflight → **Receiver**：协议选 **CRSF**（ELRS 走 CRSF）。  
3. 确认 Channel Map 为默认 AETR 或按你的手台调整。  
4. 摇杆移动时通道条应平滑变化。

### 外挂 ELRS RX

1. **Ports**：给焊接 RX 的 UART 打开 **Serial RX**。  
2. **Receiver**：Provider = CRSF。  
3. 供电与交叉线见 [assembly.md](assembly.md)。

### 通道与模式建议

| 模式槽 | 建议 |
|--------|------|
| Arm | 拨杆开关，上锁/解锁 |
| Angle（或 Horizon） | 新手用自稳；熟悉前勿用纯 Acro 外出 |
| Beeper（可选） | 寻机 |

**Failsafe**：Receiver 页或 Failsafe 页设为丢信号时**切油门最低并上锁**（Drop / 按 BF 版本推荐的 Stage2 行为）。起飞前务必在关闭遥控器时验证电机停转。

## 5. 电机与桨

1. **Configuration**：Mixer = Quad X；ESC/Motor 协议对有刷板通常选商家指定项（多为 **Brushed** 相关或板载默认，勿选错无刷协议）。  
2. **Motors** 页：  
   - 理解风险提示后，**不装桨**接电池（或按板子允许的方式供电）。  
   - 拖动滑条，确认 M1–M4 位置与 [specs.md](specs.md) / 装配表一致。  
   - 转向：俯视应符合 CW/CCW 表；不对就对调该电机两线或勾选 Reverse。  
3. 装桨后再做系绳试飞，勿在室内无护罩裸奔。

电机顺序以 Configurator 图为准；与文档冲突时**以软件图为准**。

## 6. PID / 滤波起步参数（保守）

以下为**室内 Whoop 保守起点**，不同机架会有差异。先能稳飞再微调。

### 6.1 PID（Angle 模式优先练）

在 **PID Tuning** 中可从较软开始（数值量为常见有刷 whoop 量级，若板子预设已能飞，可先用预设）：

| 轴 | P | I | D |
|----|---|---|---|
| Roll | 40–55 | 40–60 | 25–40 |
| Pitch | 40–55 | 40–60 | 25–40 |
| Yaw | 60–80 | 40–60 | 0–20 |

说明：出厂预设若已针对该 AIO，**优先出厂**，只在明显抖动/迟钝时改。

### 6.2 滤波

- 保持 Gyro 低通滤波开启；抖动大时可适当**加强滤波**或略降 D。  
- 有刷机振动通常大于无刷谁，勿一上来把滤波全关。

### 6.3 调整口诀

| 观感 | 尝试 |
|------|------|
| 高频抖动、齿轮声 | 略降 D；检查桨；略加强滤波 |
| 软、跟手慢、像泡水 | 略增 P；确认 Angle 强度 |
| 油门抬就翻 | 桨/转向/电机顺序，而非先加 PID |
| 悬停乱飘 | 校准 ACC；查风与重心；Angle 模式练习 trim |

不承诺竞赛级手感；目标是**安全系绳悬停与室内缓速**。

## 7. 其它实用设置

- **Voltage meter**：校准或确认分压比，使读数接近万用表（误差大时按 BF 文档校正）。  
- **Min cell voltage** 警告：可设约 3.3–3.5 V，提醒落地。  
- **Motor idle**：有刷 whoop 保持较低怠速即可，避免解锁后猛转。  
- **Arm 条件**：关闭「忽略电压」类危险选项；电量过低禁止解锁更安全。

## 8. CLI 备份

调通后：

```
diff all
```

复制保存到文本文件（如 `whoop65b-backup.txt`），方便刷机后恢复。

恢复时可使用 `resource` / 自定义 diff 粘贴（按你 BF 版本习惯操作），或重新按本文配置。

## 9. 推荐试飞进度

1. 无桨：Motors 测试 + 绑定 + Failsafe。  
2. 装桨系绳：Angle 模式离地悬停 10 s → 1 min。  
3. 解绳：前后左右各 1 m 平移。  
4. 再谈 Yaw 转弯与小高度变化。  

出现失控征兆立即收油门、上锁。

## 10. 相关文档

- [assembly.md](assembly.md) · [specs.md](specs.md) · [bom.md](bom.md)
