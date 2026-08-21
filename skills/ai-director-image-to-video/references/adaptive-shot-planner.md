# V6｜Adaptive Shot Planner

## Purpose
在完成 V4 Auto Director 与 V5 Platform Compiler 之后，再增加一层“镜头方案选择器”。同一张图不再只生成一个镜头方案，而是先生成 3 个不同风险档位的候选镜头，再根据原图风险自动选出最合适的一版。

目标不是增加复杂度，而是提高稳定率：**先生成候选，再淘汰高风险方案。**

---

## 1. Three-Tier Shot Candidates
对每张原图最多生成三种候选：

### SAFE｜稳定版
适用于 HIGH RISK 或结构极复杂画面。

- 摄影机：static / very slow push-in / tiny crane
- 主动作：1 个
- 二级动作：1–2 个
- 环境：极低频
- 光影：基本锁定
- 隐藏面推断：最小

### BALANCED｜平衡版
适用于 MEDIUM RISK。

- 摄影机：1 主 + 最多 1 极弱辅助
- 主动作：1 个核心动作
- 二级动作：2 个以内
- 环境：1–2 个低频响应
- 光影：轻微连续变化

### EXPRESSIVE｜表现版
仅适用于 LOW RISK 且构图稳定。

- 摄影机：允许更明显的 dolly / crane / truck
- 主动作：仍保持 1 个核心事件
- 二级动作：最多 2–3 个
- 环境：可增强空间层次
- 仍禁止为了“炫”而引入无因果运动

---

## 2. Candidate Generation Rules
三个候选必须共享：

- Structural Lock
- Visual Anchor
- 主运动主体
- 风场方向
- 光线方向
- 主体身份 / 数量 / 比例
- 叙事目标

它们只能在以下维度变化：

- 摄影机幅度
- 主动作幅度
- 二级响应数量
- 环境动态强度
- 节奏密度

禁止三个候选生成三套不同剧情。

---

## 3. Auto Selection
### risk = HIGH
默认选择 SAFE。

### risk = MEDIUM
默认选择 BALANCED；若包含文字、复杂古建、透明灵体、巨型羽毛任一项，则回退 SAFE。

### risk = LOW
默认选择 BALANCED；只有当主体轮廓清晰、背景简单、无文字锁定、无复杂隐藏面时才允许 EXPRESSIVE。

---

## 4. Stability Score
每个候选使用 0–100 稳定分：

- Structural preservation：30
- Motion simplicity：20
- Camera safety：15
- Physical causality：15
- Temporal continuity：10
- Texture / text preservation：10

### 结果
- 90–100：Excellent
- 80–89：Usable
- 70–79：Needs Degrade
- <70：Reject

低于 80 分不得作为默认推荐。

---

## 5. Hard Reject Rules
命中任意一项直接 Reject：

- 建筑主体形变作为普通动态
- 3 秒内超过 2 个明显主动作
- 单张图执行大幅 180° / 360° orbit
- 人物身份、脸型或服装发生设计性变化
- 动物出现额外翼、额外肢体风险未约束
- 大面积书法 / 纹样参与明显形变
- 高风险场景同时要求快速镜头 + 大动作
- 最后 0.3 秒突然定格或动作硬停

---

## 6. Duration-Aware Planner
### 3 秒
推荐 SAFE / BALANCED。

- 0–0.5s：稳定建立
- 0.5–2.3s：唯一核心事件
- 2.3–3.0s：惯性延续

### 5 秒
允许 BALANCED，LOW RISK 可 EXPRESSIVE。

- 0–1s：建立
- 1–4s：发展
- 4–5s：延续

### 8–10 秒
可以在同一镜头内加入“主动作前后两个阶段”，但仍保持单一叙事事件，不自动扩展为多镜头蒙太奇。

---

## 7. Camera Safety Matrix
| 场景 | 推荐 | 谨慎 | 禁止/高风险 |
|---|---|---|---|
| 复杂古建 | static, slow push | tiny crane | wide orbit |
| 巨型凤凰 | micro pull-back, glide | subtle tilt | rapid orbit |
| 小人物 | static, slow push | tiny truck | fast zoom |
| 透明灵体 | static, slow crane | micro push | large parallax |
| 书法巨幕 | static | tiny push | fabric-scale deformation |
| 云海瀑布 | slow glide | crane | violent shake |

---

## 8. Default User-Facing Output
默认不把三个方案全部倾倒给用户。

正常输出：

1. 推荐镜头方案
2. 风险等级
3. 为什么选它
4. 最终平台 Prompt
5. 极简 Prompt

仅当用户说“给我多个版本 / 多个镜头方案”时，再输出 SAFE / BALANCED / EXPRESSIVE 三版。

---

## 9. Auto Repair Loop
如果 Quality Check < 80：

1. 删除光影变化
2. 减少环境运动
3. 删除辅助镜头
4. 主动作减幅 20–40%
5. 镜头切换为 slow push / static
6. 强化 Structural Lock
7. 重新评分

最多自动修复 2 轮。两轮后仍 <80，则输出最保守 SAFE 方案。

---

## 10. V6 Final Rule
**导演系统必须优先推荐“最可能生成成功”的镜头，而不是“文字看起来最华丽”的镜头。**

最终排序：

`生成稳定性 > 原图一致性 > 主体可信运动 > 摄影机电影感 > 环境丰富度 > 风格词`