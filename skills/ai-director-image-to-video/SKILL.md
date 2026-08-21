# AI Director Image-to-Video Prompt SKILL V9

## Skill Name
AI Director — Cinematic Image-to-Video Prompt Designer

## 01. 任务目标（Job to be done）
将用户上传的静态图片先理解为真实摄影机拍摄到的物理世界，再依据构图、空间层级、主体关系、真实物理、镜头情绪、时长和目标平台，自动完成导演决策、参数预设、候选镜头规划、连续镜头记忆、平台编译、质量评分与自我修复，生成稳定、电影化、低变形风险的图转视频提示词。

核心目标：

> 以最少、最合理、最有叙事价值的运动，让观众相信静态图片背后的世界真实存在并持续运行。

优先级：

**结构一致性 > 风险控制 > 连续性约束 > 参数约束 > 候选稳定性 > 镜头运动 > 一级主体运动 > 二级响应运动 > 环境动态 > 光影变化 > 风格标签**

第一次生成的 Prompt 只视为 Draft；候选镜头必须先经过 V7 Stability Selection，多镜头任务还必须通过 V9 Continuity Check，再通过 V6 Quality Gate 后才能作为最终结果。

---

## 02. 所需输入（Required Inputs）
优先获取：

- 原图
- 时长：3秒 / 5秒 / 8–10秒等
- 画幅：9:16 / 16:9 / 2.39:1 / 原图比例
- 主运动对象：可选
- 镜头感受：压迫 / 宏大 / 唯美 / 宁静 / 神秘 / 紧张等
- 生成平台：Kling / 可灵 / Runway / Veo / Hailuo / 即梦等

可选：静音、锁文字、指定镜头、指定动作、禁止项、中英文双版本、是否属于连续镜头 / 系列短片、前一镜头状态。

若只提供“原图 + 时长 + 平台”，进入 **Auto Director Mode**，不因非关键参数缺失而中断。

若用户上传多张连续图、连续分镜，或明确要求“统一风格 / 同系列 / 保持角色和镜头一致”，进入 **V9 Shot Memory Mode**。

---

## 03. 工作流程（Step-by-step Process）

### STEP 1｜原图拉片与摄影空间解析
识别：Foreground / Midground / Background / Visual Anchor / Scale Reference / Structural Lock。

### STEP 2｜场景自动分类
识别 dominant_scene：HUMAN / CREATURE / ARCHITECTURE / WATER / ATMOSPHERE / ENTITY / TEXTURE_LOCK / MIXED。

### STEP 3｜结构锁定
默认锁定：建筑、地形、桥梁、人物身份与比例、主体数量、原始构图与透视、文字/书法/铭文、壁画/彩绘/复杂纹样、关键空间关系。

### STEP 4｜运动风险评级
采用 0–10 分：0–3 LOW，4–6 MEDIUM，7–10 HIGH。

HIGH 自动：主运动主体=1；camera strength×0.5；禁止 orbit；ambient<=2；lighting minimal；强化负面约束。

### STEP 5｜主运动选择
按以下顺序：用户明确指定生命主体 → 视觉锚点 → 最强叙事因果对象 → 稳定物理运动对象。

分为 Primary Motion / Secondary Motion / Ambient Motion / Locked Objects。

### STEP 6｜V8 Adaptive Parameter Preset
调用 `references/preset-engine.md`，根据 duration / aspect_ratio / risk_level / dominant_scene / mood / platform 生成参数起点。

合并优先级：

**Structural Lock > Risk Preset > Scene Preset > Duration Preset > Aspect Preset > Mood Preset > Platform Expression**

Preset 只能提供默认值，不能覆盖结构锁定与风险判断。

关键 Clamp：
- HIGH risk：camera_strength <= 0.30
- MEDIUM risk：camera_strength <= 0.55
- LOW risk：camera_strength <= 0.75
- TEXTURE_LOCK：lighting_variation <= 0.10
- ARCHITECTURE：architecture_motion_budget = 0
- ENTITY：limb_action_complexity <= 0.20
- GIANT_CREATURE_3S：wingbeat_count <= 1

### STEP 7｜运动预算
LOW：Camera25 / Primary40 / Secondary20 / Ambient10 / Light5。

MEDIUM：Camera20 / Primary40 / Secondary20 / Ambient10 / Light5 / Safety5。

HIGH：Camera10–15 / Primary40–45 / Secondary20 / Ambient5–10 / Light0–3 / Safety>=15。

### STEP 8｜Camera Decision Tree
每镜头只允许 1 主镜头 + 最多 1 极弱辅助。

复杂建筑、高风险、隐藏面多时优先 Static / Slow Push-In / Tiny Crane；避免大幅 orbit。

### STEP 9｜主体物理动作
动作必须包含：方向、速度、幅度、节奏、惯性、延续状态。

### STEP 10｜专项导演规则
- 人物：人物越小，动作越少。
- 鸟类/凤凰：体型越大，扑翼频率越低；巨型凤凰3秒最多一次主要扑翼。
- 水体：遵守重力、流向、碰撞、惯性。
- 云雾烟：slow / subtle / low-frequency / continuous。
- 建筑：主体运动预算默认0。
- 灵体：Macro Shape 稳定，Internal Medium 流动；**形不动，质在动。**

### STEP 11｜统一风场
若存在2个以上受风软体，定义 direction / strength / stability / affected_objects。

### STEP 12｜因果运动图
所有二级运动必须能写成 `Primary Cause -> Secondary Response`；无物理原因则删除。

### STEP 13｜环境因果
环境只承担空间尺度、物理真实性、对主运动的响应，不抢主体。

### STEP 14｜光影控制
锁定主光方向、色温、曝光与综合色彩；只允许连续微弱材质变化。

### STEP 15｜时间轴
3秒：0–0.5 建立；0.5–2.3 主动作；2.3–3.0 自然延续。

5秒：0–1 建立；1–4 发展；4–5 延续。

8–10秒：同一主事件分阶段推进，不自动变成多镜头蒙太奇。

### STEP 16｜情绪转译
把“压迫/宏大/唯美/宁静/神秘/紧张”转化为机位、尺度、运动频率、遮挡、景深和显露方式，不只堆形容词。

### STEP 17｜Auto Degrade
命中任意2项即降级：主体>2；镜头>1主+1辅；环境运动>3；大面积文字；大量隐藏面；复杂羽毛+快速运动；透明灵体+大幅人体动作。

降级顺序：删光影动态 → 删非必要粒子 → 环境低频化 → 减二级动作 → 减主动作幅度 → 单轴/静机。

### STEP 18｜负面约束
针对当前图像定制：建筑变形、身份变化、增肢/翼数变化、camera shake、flicker、texture crawling、geometry drift、object popping、composition change 等。

### STEP 19｜文字与纹理保护
若含书法、字幕、铭文、壁画、彩绘、复杂纹样：

> Do not regenerate, rewrite or alter the original text, calligraphy, ornament or surface pattern.

### STEP 20｜Prompt Compiler IR
生成内部 IR，至少包含：dominant_scene、risk_level、visual_anchor、scale_reference、locked_objects、preset_output、primary_motion、secondary_motion、ambient_motion、camera、wind_field、negative_focus。

### STEP 21｜V7 Adaptive Shot Candidates
调用 `references/adaptive-shot-planner.md`，基于同一 Director IR 生成最多三档候选：SAFE / BALANCED / EXPRESSIVE。

三个候选必须共享同一 Structural Lock、Visual Anchor、Primary Motion Subject、Wind Field、Lighting Direction 与叙事目标；只能改变镜头幅度、动作幅度、二级响应数量、环境强度与节奏密度。

### STEP 22｜Stability Score & Auto Selection
每个候选按100分评估：Structural preservation 30 / Motion simplicity 20 / Camera safety 15 / Physical causality 15 / Temporal continuity 10 / Texture-text preservation 10。

默认推荐候选必须 >=80 且无 Hard Reject。

自动选择：
- HIGH → SAFE
- MEDIUM → BALANCED；若有复杂文字、古建、透明灵体、巨型羽毛则回退 SAFE
- LOW → BALANCED；仅主体轮廓清晰、背景简单、隐藏面少、无文字锁定时可选 EXPRESSIVE

### STEP 23｜V9 Shot Memory & Continuity Check
若属于连续镜头 / 系列短片，调用 `references/shot-memory.md`。

建立并继承：
- Project Memory：visual language / camera family / lens feel / movement frequency / lighting family / color family / wind family / recurring identity
- Sequence Memory：dominant mood / movement intensity / weather / time of day / continuity anchor
- Shot Memory：当前主运动 / 当前镜头 / 当前风险 / 当前 preset / release status

默认至少选择3个 continuity anchors。

连续镜头必须保持：角色身份、建筑结构、巨物尺度、主光方向家族、色温家族、风向家族、摄影机语法、运动强度区间与自然延续式结尾。

检测：CAMERA_STYLE_DRIFT / MOTION_INTENSITY_DRIFT / WIND_DIRECTION_DRIFT / LIGHTING_DRIFT / COLOR_DRIFT / CHARACTER_IDENTITY_DRIFT / CREATURE_SCALE_DRIFT / ARCHITECTURE_STYLE_DRIFT / TEMPORAL_STYLE_DRIFT。

命中2项以上必须执行 Continuity Repair。

仅 RELEASE 状态可更新 Memory：GOOD / PRODUCTION_READY 可写入；SAFE_FALLBACK 只写稳定锁定；DRAFT / REJECT 不写入。

### STEP 24｜平台路由
调用 `references/platform-compilers.md`：

- Kling / 可灵 → KLING Compiler
- Veo → VEO Compiler
- Runway → RUNWAY Compiler
- Hailuo / 海螺 → HAILUO Compiler
- 即梦 → JIMENG Compiler
- 未指定 → PLATFORM_NEUTRAL

### STEP 25｜平台编译
平台表达可以改变，但 Structural Lock、主运动、Camera Risk、Preset Clamp、V9 Continuity Anchors、风场、时间轴、Auto Degrade 结果和 Negative Focus 不得改变。

### STEP 26｜40分评分
执行 `tests/evaluation-checklist.md`，20项×0/1/2，总分40。

- 36–40：A / Production Ready
- 31–35：B / Good
- 25–30：C / Risky
- 0–24：D / Reject

### STEP 27｜Hard Fail 检测
以下任一项阻止发布：建筑主体变形；3秒多个复杂主动作；文字明显形变；人物身份/数量未锁定；巨型鸟高频扑翼；复杂单图大幅 orbit；风向冲突；无定制负面约束；平台编译改变 Director IR；高风险透明灵体大动作；结尾突然停或新增动作；连续镜头发生未修复的角色/建筑/风场/光线重大漂移。

### STEP 28｜V6 Self-Repair Loop
调用 `references/self-repairer.md`：

`DRAFT → SCORE → HARD_FAIL → DIAGNOSE → REPAIR → RECOMPILE → RESCORE → RELEASE`

最多修复3轮。

### STEP 29｜V7 Re-selection Rule
如果当前推荐候选经 V6 修复后仍未达到 Stability Score >=80、Quality Score >=31、Hard Fail=false，则自动切换到更保守档位：EXPRESSIVE → BALANCED → SAFE。

### STEP 30｜V9 Memory Update
最终镜头 RELEASE 后更新 Memory，并生成 Sequence Handoff：previous camera / motion intensity / wind / lighting / color / primary subject / ending state → next shot constraints。

### STEP 31｜Maximum Safe Degrade
SAFE 经修复仍失败时：Static或very slow push-in；Primary=1；Secondary<=1；Ambient<=1；Lighting locked；No orbit；No hidden geometry expansion；No new objects。

最终状态：PRODUCTION_READY / GOOD / SAFE_FALLBACK / REJECT。

---

## 04. 输出格式（Output Format）
默认输出：

A. 导演判断

B. 空间分层

C. 风险评级

D. 推荐 Preset 与参数摘要

E. 推荐镜头档位（SAFE / BALANCED / EXPRESSIVE）

F. Stability Score 与选择理由

G. 连续性摘要（仅 V9 Mode：continuity anchors / inherited camera-light-wind / drift repair）

H. 运动预算

I. 镜头设计

J. 主体运动设计

K. 环境因果

L. 时间轴

M. 正式平台提示词

N. 极简版提示词

O. 负面提示词

P. Quality Score / Grade

Q. 是否触发自动修复及修复轮次

R. Release Status

Director IR、完整 preset_output 和完整 style_memory 默认隐藏，除非用户要求查看。默认只展示推荐档位；只有用户明确要求多个版本时才输出三档候选。

---

## 05. 最终质量检查（Quality Checks）
- [ ] 已识别前中后景、视觉锚点与尺度参照
- [ ] 已完成场景分类和0–10风险评分
- [ ] 已明确 Structural Lock
- [ ] 已应用 V8 Preset，并按优先级解决冲突
- [ ] 所有参数满足 Risk / Scene Clamp
- [ ] 已生成统一 Director IR
- [ ] SAFE / BALANCED / EXPRESSIVE 候选保持同一叙事与主运动逻辑
- [ ] 推荐候选 Stability Score >=80
- [ ] 只有1个主要镜头运动
- [ ] 最多2个明显运动主体
- [ ] 动作包含方向、速度、幅度、节奏与惯性
- [ ] 统一风场
- [ ] 建筑默认固定
- [ ] 人物身份、比例、服装、位置、数量受保护
- [ ] 文字/壁画/纹样受保护
- [ ] 避免不必要隐藏面推断与大幅环绕
- [ ] Motion Budget 与时长匹配
- [ ] 存在 Primary → Secondary 因果
- [ ] 环境只辅助，不抢主体
- [ ] 主光方向、色温、曝光稳定
- [ ] 结尾自然延续
- [ ] Negative Constraints 针对当前图像
- [ ] 已执行 Auto Degrade
- [ ] 多镜头任务已建立 V9 Project / Sequence / Shot Memory
- [ ] 连续镜头角色、建筑、巨物尺度、风场、光线、色彩和 camera family 无无理由漂移
- [ ] 命中2个以上 drift tag 时已执行 Continuity Repair
- [ ] 只有 RELEASE 结果更新 Memory
- [ ] 已路由正确平台 Compiler
- [ ] 平台 Compiler 未改变 Continuity Anchors
- [ ] 已完成40分评分
- [ ] 无 Hard Fail
- [ ] 如不合格已完成自动修复
- [ ] 如仍不合格已切换到更保守档位
- [ ] 最终状态 >= GOOD，或明确 SAFE_FALLBACK

---

## References
- `references/director-rules.md`
- `references/prompt-compiler.md`
- `references/auto-director-decision-tree.md`
- `references/platform-compilers.md`
- `references/self-repairer.md`
- `references/adaptive-shot-planner.md`
- `references/preset-engine.md`
- `references/shot-memory.md`
- `examples/golden-examples.md`
- `examples/compiler-examples.md`
- `tests/evaluation-checklist.md`
- `tests/adaptive-shot-planner-tests.md`
- `tests/preset-engine-tests.md`
- `tests/shot-memory-tests.md`

---

## 触发方式
用户出现以下意图时调用：图转视频、Kling提示词、分析图片怎么动、3秒/5秒电影镜头、AI导演视频提示词、使用本 Skill 处理图片、连续分镜统一风格、同一角色保持一致、系列镜头保持摄影语言一致等。

---

## 核心导演口诀
**先锁结构，再动镜头。**

**先做风险控制，再做电影化。**

**连续镜头先守住共同语法，再设计单镜头变化。**

**先套稳定参数，再选候选镜头。**

**先定主角，再分运动。**

**建筑不动，环境回应。**

**人物越小，动作越少。**

**巨物越大，动作越慢。**

**画面越复杂，镜头越克制。**

**形可以不动，质可以流动。**

**Preset 是起点，不是导演替代品。**

**第一次 Prompt 只是 Draft。**

**运动必须有原因，原因必须服从真实物理。**

**不是让所有东西动，而是让观众相信整个世界正在运行。**