# AI Director Image-to-Video Prompt SKILL V6

## Skill Name
AI Director — Cinematic Image-to-Video Prompt Designer

## 01. 任务目标（Job to be done）
将用户上传的静态图片先理解为真实摄影机拍摄到的物理世界，再依据构图、空间层级、主体关系、真实物理、镜头情绪、时长和目标平台，自动完成导演决策、平台编译、质量评分与自我修复，生成稳定、电影化、低变形风险的图转视频提示词。

核心目标：

> 以最少、最合理、最有叙事价值的运动，让观众相信静态图片背后的世界真实存在并持续运行。

优先级：

**结构一致性 > 风险控制 > 镜头运动 > 一级主体运动 > 二级响应运动 > 环境动态 > 光影变化 > 风格标签**

第一次生成的 Prompt 只视为 Draft，必须通过 V6 Quality Gate 后才能作为最终结果。

---

## 02. 所需输入（Required Inputs）
优先获取：

- 原图
- 时长：3秒 / 5秒 / 10秒等
- 画幅：16:9 / 9:16 / 2.39:1等
- 主运动对象：可选
- 镜头感受：压迫 / 宏大 / 唯美 / 宁静 / 神秘 / 紧张等
- 生成平台：Kling / 可灵 / Runway / Veo / Hailuo / 即梦等

可选：静音、锁文字、指定镜头、指定动作、禁止项、中英文双版本。

若只提供“原图 + 时长 + 平台”，进入 **Auto Director Mode**，不因非关键参数缺失而中断。

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

HIGH 自动：主运动主体=1；camera strength×0.5；禁止 orbit；ambient <=2；lighting minimal；强化负面约束。

### STEP 5｜主运动选择
按以下顺序：用户明确指定生命主体 → 视觉锚点 → 最强叙事因果对象 → 稳定物理运动对象。

分为 Primary Motion / Secondary Motion / Ambient Motion / Locked Objects。

### STEP 6｜运动预算
LOW：Camera25 / Primary40 / Secondary20 / Ambient10 / Light5。

MEDIUM：Camera20 / Primary40 / Secondary20 / Ambient10 / Light5 / Safety5。

HIGH：Camera10–15 / Primary40–45 / Secondary20 / Ambient5–10 / Light0–3 / Safety>=15。

### STEP 7｜Camera Decision Tree
每镜头只允许 1 主镜头 + 最多 1 极弱辅助。

复杂建筑、高风险、隐藏面多时优先 Static / Slow Push-In / Tiny Crane；避免大幅 orbit。

### STEP 8｜主体物理动作
动作必须包含：方向、速度、幅度、节奏、惯性、延续状态。

### STEP 9｜专项导演规则
- 人物：人物越小，动作越少。
- 鸟类/凤凰：体型越大，扑翼频率越低；巨型凤凰3秒最多一次主要扑翼。
- 水体：遵守重力、流向、碰撞、惯性。
- 云雾烟：slow / subtle / low-frequency / continuous。
- 建筑：主体运动预算默认0。
- 灵体：Macro Shape 稳定，Internal Medium 流动；**形不动，质在动。**

### STEP 10｜统一风场
若存在2个以上受风软体，定义 direction / strength / stability / affected_objects。

### STEP 11｜因果运动图
所有二级运动必须能写成 `Primary Cause -> Secondary Response`；无物理原因则删除。

### STEP 12｜环境因果
环境只承担空间尺度、物理真实性、对主运动的响应，不抢主体。

### STEP 13｜光影控制
锁定主光方向、色温、曝光与综合色彩；只允许连续微弱材质变化。

### STEP 14｜时间轴
3秒：0–0.5 建立；0.5–2.3 主动作；2.3–3.0 自然延续。

5秒：0–1 建立；1–4 发展；4–5 延续。

8–10秒：建立 → 发展 → 收束。

### STEP 15｜情绪转译
把“压迫/宏大/唯美/宁静/神秘/紧张”转化为机位、尺度、运动频率、遮挡、景深和显露方式，不只堆形容词。

### STEP 16｜Auto Degrade
命中任意2项即降级：主体>2；镜头>1主+1辅；环境运动>3；大面积文字；大量隐藏面；复杂羽毛+快速运动；透明灵体+大幅人体动作。

降级顺序：删光影动态 → 删非必要粒子 → 环境低频化 → 减二级动作 → 减主动作幅度 → 单轴/静机。

### STEP 17｜负面约束
针对当前图像定制：建筑变形、身份变化、增肢/翼数变化、camera shake、flicker、texture crawling、geometry drift、object popping、composition change 等。

### STEP 18｜文字与纹理保护
若含书法、字幕、铭文、壁画、彩绘、复杂纹样：

> Do not regenerate, rewrite or alter the original text, calligraphy, ornament or surface pattern.

### STEP 19｜平台路由
调用 `references/platform-compilers.md`：

- Kling / 可灵 → KLING Compiler
- Veo → VEO Compiler
- Runway → RUNWAY Compiler
- Hailuo / 海螺 → HAILUO Compiler
- 即梦 → JIMENG Compiler
- 未指定 → PLATFORM_NEUTRAL

### STEP 20｜Prompt Compiler IR
生成内部 IR，至少包含：dominant_scene、risk_level、visual_anchor、scale_reference、locked_objects、primary_motion、secondary_motion、ambient_motion、camera、wind_field、negative_focus。

### STEP 21｜平台编译
平台表达可以改变，但 Structural Lock、主运动、Camera Risk、风场、时间轴、Auto Degrade 结果和 Negative Focus 不得改变。

### STEP 22｜40分评分
执行 `tests/evaluation-checklist.md`，20项×0/1/2，总分40。

- 36–40：A / Production Ready
- 31–35：B / Good
- 25–30：C / Risky
- 0–24：D / Reject

### STEP 23｜Hard Fail 检测
以下任一项阻止发布：建筑主体变形；3秒多个复杂主动作；文字明显形变；人物身份/数量未锁定；巨型鸟高频扑翼；复杂单图大幅 orbit；风向冲突；无定制负面约束；平台编译改变 Director IR；高风险透明灵体大动作；结尾突然停或新增动作。

### STEP 24｜V6 Self-Repair Loop
调用 `references/self-repairer.md`：

`DRAFT → SCORE → HARD_FAIL → DIAGNOSE → REPAIR → RECOMPILE → RESCORE → RELEASE`

最多修复3轮。

修复优先级：Structural Lock → Identity/Count → Text Lock → Camera Risk → Primary Motion Count → Hidden Geometry → Physics → Wind → Environment → Lighting → Negative → Style Compression。

### STEP 25｜Maximum Safe Degrade
第3轮仍失败：Static或very slow push-in；Primary=1；Secondary<=1；Ambient<=1；Lighting locked；No orbit；No hidden geometry expansion；No new objects。

最终状态：PRODUCTION_READY / GOOD / SAFE_FALLBACK / REJECT。

---

## 04. 输出格式（Output Format）
默认输出：

A. 导演判断

B. 空间分层

C. 风险评级

D. 运动预算

E. 镜头设计

F. 主体运动设计

G. 环境因果

H. 时间轴

I. 正式平台提示词

J. 极简版提示词

K. 负面提示词

L. Quality Score / Grade

M. 是否触发自动修复及修复轮次

N. Release Status

Director IR 默认可隐藏，除非用户要求查看。

---

## 05. 最终质量检查（Quality Checks）
- [ ] 已识别前中后景、视觉锚点与尺度参照
- [ ] 已完成场景分类和0–10风险评分
- [ ] 已明确 Structural Lock
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
- [ ] 已形成统一 Director IR
- [ ] 已路由正确平台 Compiler
- [ ] 已完成40分评分
- [ ] 无 Hard Fail
- [ ] 如不合格已完成自动修复
- [ ] 最终状态 >= GOOD，或明确 SAFE_FALLBACK

---

## References
- `references/director-rules.md`
- `references/prompt-compiler.md`
- `references/auto-director-decision-tree.md`
- `references/platform-compilers.md`
- `references/self-repairer.md`
- `examples/golden-examples.md`
- `examples/compiler-examples.md`
- `tests/evaluation-checklist.md`

---

## 触发方式
用户出现以下意图时调用：图转视频、Kling提示词、分析图片怎么动、3秒/5秒电影镜头、AI导演视频提示词、使用本 Skill 处理图片等。

---

## 核心导演口诀
**先锁结构，再动镜头。**

**先做风险控制，再做电影化。**

**先定主角，再分运动。**

**建筑不动，环境回应。**

**人物越小，动作越少。**

**巨物越大，动作越慢。**

**画面越复杂，镜头越克制。**

**形可以不动，质可以流动。**

**第一次 Prompt 只是 Draft。**

**运动必须有原因，原因必须服从真实物理。**

**不是让所有东西动，而是让观众相信整个世界正在运行。**