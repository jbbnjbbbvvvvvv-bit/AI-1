# V7｜Adaptive Shot Planner Acceptance Tests

## 目标
验证 SAFE / BALANCED / EXPRESSIVE 三档候选是否真正降低失败风险，而不是简单生成三个不同风格 Prompt。

---

## Test 1｜复杂古建筑 + 小人物
**输入特征**：复杂屋檐、斗拱、人物占画面 <10%、3秒。

期望：
- risk = HIGH 或 MEDIUM-HIGH
- 推荐 SAFE
- Camera = static / very slow push-in
- Primary Motion = 人物微抬头或呼吸，仅1个
- 建筑结构 hard lock
- 禁止 orbit

Hard Fail：建筑呼吸、屋檐变形、人物大步移动。

---

## Test 2｜巨型凤凰 + 宫殿
**输入特征**：凤凰为视觉锚点，巨型羽毛，宫殿为尺度参照。

期望：
- 推荐 SAFE 或 BALANCED
- Primary Motion = 一次有重量的翼下压后滑翔
- Secondary = 外侧飞羽延迟弯曲 / 尾羽惯性
- Camera = slow glide / micro pull-back
- extra wings / feather melting 写入负面约束

Hard Fail：高频扑翼、快速环绕、宫殿漂移。

---

## Test 3｜人物近景简单背景
**输入特征**：人物占画面 >30%，背景简单，无文字。

期望：
- risk = LOW
- 默认 BALANCED
- 可生成 EXPRESSIVE 候选
- Camera 可使用轻微 dolly / truck
- 人物可有轻微表演，但不做复杂手指动作

Hard Fail：人物身份改变、五官漂移、服装重构。

---

## Test 4｜书法巨幕
**输入特征**：大面积书法、布幕、人物、建筑。

期望：
- risk = HIGH
- 推荐 SAFE
- 书法区域 hard lock
- 布幕仅允许边缘毫米级微动
- Camera = static / tiny push

Hard Fail：文字重绘、书法笔画漂移、布幕大幅摆动。

---

## Test 5｜透明巨型灵体
**输入特征**：半透明人物形灵体 + 建筑。

期望：
- risk = HIGH
- Macro Shape locked
- Primary Motion = Internal Medium Flow
- Camera = static / slow crane
- 禁止灵体大幅转身、迈步、挥手

Hard Fail：肢体结构变化、透明体与背景融合断裂。

---

## Test 6｜云海 + 瀑布
**输入特征**：无复杂建筑，水体为主要可动物理介质。

期望：
- risk = LOW / MEDIUM
- Primary Motion = 瀑布持续下落
- Secondary = 水雾扩散 / 波纹
- Ambient = 低频云雾漂移
- 可选 BALANCED，LOW RISK 时允许 EXPRESSIVE

Hard Fail：瀑布逆流、云层高速沸腾、无因果大浪。

---

## Candidate Consistency Check
三档候选必须共享：

- 同一 visual anchor
- 同一 structural lock
- 同一主运动主体
- 同一风向
- 同一光线方向
- 同一叙事事件

只允许改变：摄影机幅度、主动作幅度、二级响应数量、环境强度、节奏密度。

若 SAFE / BALANCED / EXPRESSIVE 之间出现剧情变化，判定失败。

---

## Stability Threshold
- >=90：Excellent
- 80–89：Usable
- 70–79：必须降级重做
- <70：Reject

默认推荐候选必须 >=80，且不得包含任何 Hard Fail。

---

## Auto Repair Interaction
若推荐候选在 V6 Quality Gate 中低于发布阈值：

1. 先执行 V6 Repair Loop
2. 修复后重新进行 Stability Score
3. 若仍低于 80，强制切换到 SAFE
4. SAFE 仍失败时执行 Maximum Safe Degrade

V7 不替代 V6；V7 负责“选方案”，V6 负责“修方案”。