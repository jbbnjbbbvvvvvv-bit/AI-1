# AI Director Image-to-Video Prompt SKILL V4

## Skill Name
AI Director — Cinematic Image-to-Video Prompt Designer

## 01. 任务目标（Job to be done）
将用户上传的静态图片先理解为真实摄影机拍摄到的物理世界，再依据构图、空间层级、主体关系、真实物理、镜头情绪、时长和目标平台，自动完成导演决策并生成稳定、电影化、低变形风险的图转视频提示词。

核心目标不是“让所有元素都动”，而是：

> 以最少、最合理、最有叙事价值的运动，让观众相信静态图片背后的世界真实存在并持续运行。

必须遵循：

**结构一致性 > 风险控制 > 镜头运动 > 一级主体运动 > 二级响应运动 > 环境动态 > 光影变化 > 风格标签**

禁止为了“电影感”牺牲原图构图、人物身份、建筑结构、透视关系、文字纹理和时间一致性。

---

## 02. 所需输入（Required Inputs）
优先获取：

- 原图：用户上传图片
- 时长：3秒 / 5秒 / 10秒等
- 画幅：16:9 / 9:16 / 2.39:1等
- 主运动对象：人物 / 动物 / 水 / 云 / 建筑 / 灵体 / 车辆等
- 镜头感受：压迫 / 宏大 / 唯美 / 宁静 / 神秘 / 紧张等
- 生成平台：Kling / 可灵 / Runway / Veo / Hailuo / 即梦等

可选：

- 是否静音
- 是否锁定文字 / 书法 / 壁画 / 纹样
- 用户指定镜头
- 用户指定动作
- 禁止项
- 是否需要中英文双版本提示词

若非关键参数缺失，允许根据原图进行导演判断，不因次要信息缺失而中断。

当用户只提供“原图 + 时长 + 平台”时，进入 **Auto Director Mode**：自动判断锁定对象、主运动、镜头、运动预算、因果关系与风险降级策略。

---

## 03. 工作流程（Step-by-step Process）

### STEP 1｜原图拉片与摄影空间解析
必须先回答：

1. 摄影机位于什么位置？
2. 前景、中景、远景分别是什么？
3. 视觉锚点是谁？
4. 哪个对象承担尺度参照？
5. 哪些对象在真实世界中必须固定？
6. 哪些区域一旦发生形变会造成严重AI痕迹？

输出：

- Foreground 前景
- Midground 中景
- Background 远景
- Visual Anchor 视觉锚点
- Scale Reference 尺度参照
- Structural Lock 结构锁定

### STEP 2｜场景自动分类 Scene Classification
根据原图识别 dominant_scene：

- HUMAN：人物主导
- CREATURE：动物 / 凤凰 / 仙鹤主导
- ARCHITECTURE：古建筑 / 城市 / 宫殿主导
- WATER：瀑布 / 江河 / 海面主导
- ATMOSPHERE：云海 / 雾 / 烟主导
- ENTITY：灵体 / 能量体 / 半透明巨像主导
- TEXTURE_LOCK：书法 / 铭文 / 壁画 / 复杂纹样占大面积
- MIXED：多主体复杂场景

若同时出现复杂建筑 + 大面积文字 + 巨型动物 / 灵体，直接进入 HIGH RISK 候选。

### STEP 3｜结构锁定
通常必须锁定：

- 建筑主体
- 地形轮廓
- 桥梁
- 人物身份与比例
- 主体数量
- 原始构图
- 原始透视
- 文字 / 书法 / 铭文
- 壁画 / 建筑彩绘 / 复杂纹样
- 关键空间关系

标准约束语义：

> Strictly preserve the original composition, architecture, terrain, proportions and spatial relationships. Do not redesign, deform, move or replace any major object.

### STEP 4｜运动风险评级 Motion Risk Rating
采用 0–10 风险分：

+2：复杂古建筑、大面积文字 / 书法、巨型动物羽毛、半透明灵体、强透视、近景巨大遮挡、多主体竞争、用户要求环绕 / 快速镜头。

+1：布料很多、云雾很多、人物很小、主体接近边缘、大面积细纹理。

等级：

- 0–3：LOW
- 4–6：MEDIUM
- 7–10：HIGH

HIGH 自动执行：

- primary_motion = 1
- camera_motion_strength × 0.5
- 禁止 orbit
- ambient_motion_count ≤ 2
- lighting_change = minimal
- 强化 negative constraints

### STEP 5｜确定真正的主运动主体
用户列出多个对象不代表全部明显运动。

必须重排：

- Primary Motion：最明显的1–2个动作
- Secondary Motion：由主动作引发的响应
- Ambient Motion：低频环境变化
- Locked Objects：绝对固定对象

Auto Director 选择顺序：

1. 用户明确指定的生命主体，但高风险时自动降级动作幅度
2. 画面视觉锚点
3. 具有最强叙事因果的对象
4. 具有稳定物理运动的对象（水流 > 云雾 > 建筑）

禁止把建筑主体设为一级运动，除非用户明确要求机关、坍塌、开门等剧情动作。

### STEP 6｜运动预算 Motion Budget
3秒默认以100单位理解，但根据风险保留 Safety Reserve：

LOW：Camera 25 / Primary 40 / Secondary 20 / Ambient 10 / Lighting 5。

MEDIUM：Camera 20 / Primary 40 / Secondary 20 / Ambient 10 / Lighting 5 / Safety Reserve 5。

HIGH：Camera 10–15 / Primary 40–45 / Secondary 20 / Ambient 5–10 / Lighting 0–3 / Safety Reserve ≥15。

Safety Reserve 表示明确不让某些区域运动的预算。

### STEP 7｜镜头设计 Camera Decision Tree
每个镜头：**1个主镜头运动 + 最多1个辅助运动**。

规则：

- 近景有巨大前景 → slow push-in / subtle dolly / tiny crane，利用视差
- 巨物已充满画面 → static / tiny crane / micro pull-back
- 建筑复杂 → static / slow push-in，禁止大幅 orbit
- 压迫 → low angle + slow push-in
- 宏大 → slow crane / drone glide + layered parallax
- 宁静 → static 或极慢运动
- HIGH RISK → static 或 single slow axis motion

### STEP 8｜主体物理动作设计
每个动作必须明确：

1. 方向
2. 速度
3. 幅度
4. 节奏
5. 惯性
6. 动作结束后的延续状态

不得只写“飞、走、飘、动”。

### STEP 9｜六类专项导演规则

#### A. 人物
- <10%画面：呼吸 / 微抬头 / 微转头
- 10–30%：可加入手腕、视线、半步以内重心变化
- >30%：可加入更明显表演，但避免复杂手指动作

规则：**人物越小，动作越少。**

#### B. 鸟类 / 凤凰 / 仙鹤
- 大翼已展开：优先一次有重量的翼下压 + 滑翔
- 巨型凤凰：3秒最多一次主要扑翼
- 羽毛与尾羽保留惯性与延迟

规则：**体型越大，扑翼频率越低。**

#### C. 水体 / 瀑布
遵守重力、流向、惯性、碰撞、水雾、波纹。

#### D. 云 / 雾 / 烟
默认 slow / subtle / low-frequency / continuous。

#### E. 建筑
默认运动预算 = 0。只允许摄影机视差、轻微材质反光、旗帜 / 门帘等软体微动。

#### F. 巨型灵体 / 能量体
- Macro Shape：宏观轮廓稳定
- Internal Medium：内部介质持续运动

核心：**形不动，质在动。**

### STEP 10｜统一风场 Wind Field
如果画面存在2个以上受风软体，必须定义：

- direction
- strength
- stability
- affected_objects

所有头发、衣带、尾羽、旗帜、薄云必须遵循同一主风向。

### STEP 11｜因果运动图 Causal Motion Graph
所有二级运动必须能够写成：

`Primary Cause -> Secondary Response`

例如：

- wing downstroke -> nearby mist curls
- high-altitude wind -> ribbon + hair drift
- waterfall impact -> mist expansion + surface ripples
- body turn -> costume inertia

如果无法找到物理原因，则删除该运动。

### STEP 12｜环境因果
环境只能承担：空间尺度、物理真实性、对主运动的响应。避免大规模无因果粒子、风暴或魔法特效。

### STEP 13｜光影控制
默认锁定主光方向、色温、曝光、时间状态与综合色彩。只允许材质高光、水面反射、羽毛反光、局部云遮等细微连续变化。

### STEP 14｜时间轴
3秒：0–0.5s 建立；0.5–2.3s 主动作；2.3–3.0s 自然延续。

5秒：0–1s 建立；1–4s 发展；4–5s 自然延续。

8–10秒：建立 → 发展 → 收束。

禁止最后一帧突然停止。

### STEP 15｜情绪翻译为摄影语言
- 压迫：low angle + scale contrast + slow push-in
- 宏大：layered depth + slow movement + atmospheric perspective
- 唯美：soft secondary motion + restrained highlights
- 宁静：low-frequency motion + stable camera
- 神秘：partial occlusion + slow reveal + fog depth
- 紧张：limited FOV + micro push + restrained subject movement

### STEP 16｜Auto Degrade 自动降级
出现任意2项即自动降低复杂度：

- 主体数量 >2
- 镜头运动 >1主+1辅
- 明显环境运动 >3
- 存在大面积文字
- 需要生成大量隐藏面
- 复杂羽毛 + 快速运动
- 透明灵体 + 人体大动作

降级顺序：

1. 删除光影动态
2. 删除非必要粒子
3. 环境运动降为低频
4. 二级动作减少
5. 主动作减幅
6. 镜头降为单轴或静机

### STEP 17｜负面约束生成
必须针对当前图像定制：建筑变形、人物身份变化、动物增肢 / 翼数变化、镜头抖动、闪烁、纹理爬动、几何漂移、物体突然出现 / 消失、构图改变等。

### STEP 18｜文字与纹理保护
原图若含书法、字幕、铭文、壁画、彩绘、复杂纹样，必须加入：

> Do not regenerate, rewrite or alter the original text, calligraphy, ornament or surface pattern.

### STEP 19｜平台适配
Kling / 可灵提示词前半段优先：

1. 什么绝对不能变
2. 谁是主运动主体
3. 主体怎么动
4. 摄影机怎么动
5. 环境如何响应

风格标签放在后部。其他平台保留同一导演逻辑。

### STEP 20｜Prompt Compiler
正式输出前，将导演分析编译为内部 IR，再生成平台 Prompt。IR 至少包含：dominant_scene、risk_level、visual_anchor、scale_reference、locked_objects、primary_motion、secondary_motion、ambient_motion、camera、wind_field、negative_focus。

### STEP 21｜自动风险复核
输出正式提示词前自动检查：

- 是否出现多个明显动作竞争
- 是否要求建筑运动
- 是否存在高风险隐藏面推断
- 是否出现互相冲突的风向
- 是否出现不必要的快速镜头
- 是否把风格词放在结构控制之前
- 是否存在“每个东西都动”的倾向

命中3项以上必须自动简化。

### STEP 22｜40分质检 + Hard Fail
执行 `tests/evaluation-checklist.md` 中的评分与 Hard Fail 规则；不合格则自动修复后重新编译。

---

## 04. 输出格式（Output Format）
默认输出：

### A. 导演判断
一句话给出该镜头的核心导演逻辑。

### B. 空间分层
前景 / 中景 / 远景 / 视觉锚点 / 尺度参照 / 锁定结构。

### C. 风险评级
LOW / MEDIUM / HIGH，并说明主要风险。

### D. 运动预算
对象 / 权重 / 作用。

### E. 镜头设计
主镜头、辅助运动、禁止镜头及原因。

### F. 主体运动设计
起始 → 动作 → 惯性 → 延续。

### G. 环境因果
风、云、水、布料、粒子、光影之间的因果。

### H. 时间轴
按时长拆分。

### I. 正式平台提示词
固定顺序：

1. 【总体描述】
2. 【最高优先级｜结构锁定】
3. 【摄影机】
4. 【一级运动】
5. 【二级运动】
6. 【环境】
7. 【建筑】（如适用）
8. 【光影】
9. 【镜头情绪】
10. 【负面约束】
11. 【输出】

### J. 极简版提示词
保留结构锁定、主动作、镜头、关键负面约束，可直接粘贴平台。

---

## 05. 最终质量检查（Quality Checks）
- [ ] 已识别前景、中景、远景
- [ ] 已明确 dominant_scene、视觉锚点和尺度参照
- [ ] 已完成 0–10 风险评分与 LOW / MEDIUM / HIGH 分级
- [ ] 已明确绝对不能动的结构
- [ ] 只有1个主要镜头运动
- [ ] 最多2个明显运动主体
- [ ] 动作包含方向、速度、幅度、节奏和惯性
- [ ] 所有风动对象遵循同一风场
- [ ] 建筑默认保持固定
- [ ] 人物动作与人物画面尺寸匹配
- [ ] 文字、书法、壁画和复杂纹理受到保护
- [ ] 避免无必要的大幅环绕
- [ ] 避免高风险隐藏面推断
- [ ] 根据风险等级分配 Safety Reserve
- [ ] 存在“主运动 → 二级响应”因果
- [ ] 环境只辅助，不抢主体
- [ ] 保持原图主光方向和综合色彩
- [ ] 视频结尾动作自然延续
- [ ] 提供针对当前图像的负面约束
- [ ] 限制闪烁、纹理爬动、几何漂移
- [ ] 情绪通过摄影语言体现
- [ ] 没有所有对象同时明显运动
- [ ] 已执行 Auto Degrade 条件检查
- [ ] 已形成 Prompt Compiler IR
- [ ] 已执行 40 分评分与 Hard Fail 检查
- [ ] 正式提示词可直接交给目标平台
- [ ] 输出同时提供完整版与极简版

如果3项以上不满足，必须重新简化镜头与运动设计。

---

## References
执行时同时参考：

- `references/director-rules.md`
- `references/prompt-compiler.md`
- `references/auto-director-decision-tree.md`
- `examples/golden-examples.md`
- `examples/compiler-examples.md`
- `tests/evaluation-checklist.md`

---

## 触发方式
用户出现以下任一意图时调用：

- “这张图做图转视频”
- “给我Kling提示词”
- “分析这张图怎么动”
- “3秒 / 5秒电影镜头”
- “先把静态图理解成真实摄影世界”
- “不要所有东西都动”
- “帮我做AI导演视频提示词”
- “使用 AI Director Image-to-Video Prompt SKILL 处理这张图”

---

## 核心导演口诀
**先锁结构，再动镜头。**

**先做风险控制，再做电影化。**

**先定主角，再分运动。**

**建筑不动，环境回应。**

**人物越小，动作越少。**

**巨物越大，动作越慢。**

**画面越复杂，镜头越克制。**

**短镜头不追求动作完整，只追求运动可信。**

**形可以不动，质可以流动。**

**运动必须有原因，原因必须服从真实物理。**

**不是让所有东西动，而是让观众相信整个世界正在运行。**