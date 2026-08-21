# V5｜Platform-Specific Prompt Compilers

## Purpose
将同一套导演 IR（Intermediate Representation）编译为不同视频生成平台更适合的表达，而不是把一套 Prompt 原样复制到所有平台。

核心原则：**导演决策不变，表达方式随平台变化。**

统一 IR 至少包含：

```yaml
shot:
  duration: 3s
  aspect_ratio: 16:9
  platform: Kling
scene:
  dominant_scene: CREATURE
  risk_level: HIGH
  visual_anchor: phoenix
  scale_reference: palace
locks:
  - composition
  - architecture
  - subject_count
  - identity
  - text_texture
camera:
  primary: slow_forward_glide
  secondary: subtle_tilt_up
  amplitude: very_low
primary_motion:
  subject: phoenix
  action: one_weighted_downstroke_then_glide
secondary_motion:
  - outer_feathers_delayed_flex
  - tail_feathers_inertial_drag
ambient_motion:
  - low_frequency_cloud_drift
physics:
  wind_direction: rear_right
  wind_strength: gentle
light:
  preserve_direction: true
  preserve_exposure: true
negative_focus:
  - extra_wings
  - roof_distortion
  - camera_shake
  - flicker
```

---

# 1. Kling / 可灵 Compiler

## 编译目标
强调：结构锁定、单一明确动作、摄影机运动、物理响应、负面约束。

## 顺序
1. Preservation / Structural Lock
2. Primary Motion
3. Camera
4. Secondary Physical Response
5. Ambient Motion
6. Light / Look
7. Negative Constraints

## 语言风格
- 动作写得具体
- 速度、幅度、方向、惯性明确
- 短句优先
- 结构锁定放最前
- 风格词放最后

## Kling 模板
```text
基于原始图片生成[时长]图转视频。严格保持[锁定对象]的原始构图、比例、透视、数量与空间关系，不重新设计、不变形、不漂移。

主运动：[主体]以[速度/幅度]完成[唯一核心动作]，[惯性/延续说明]。

镜头：[主镜头]，[可选极弱辅助运动]，整体稳定，不大幅改变视角，不暴露大量原图不可见结构。

物理响应：[1–2项因果响应]。环境仅保留[低频微运动]，所有受风对象遵循同一风向。

保持原始主光方向、色温与曝光，只允许连续细微材质高光变化。真实重量感、自然运动模糊、时间一致性、电影级空间层次。

负面：[8–16个当前场景高风险失败项]。
```

## Kling 自动降级
若 risk = HIGH：
- orbit → static / slow push-in
- 2个主动作 → 1个
- 环境动态减半
- camera amplitude × 0.5
- 强化 architectural deformation / duplicate subject / flicker 等负面词

---

# 2. Veo Compiler

## 编译目标
强调：完整镜头语义、摄影语言、时空连续性、真实物理与场景叙事。

## 顺序
1. Shot Description
2. Subject & Action
3. Camera Language
4. Physical World Behavior
5. Lighting / Atmosphere
6. Preservation Constraints
7. Temporal Continuity

## 语言风格
- 使用完整自然语言
- 可描述镜头意图与视觉结果
- 允许更长上下文
- 不堆标签
- 更重视“为什么这样动”

## Veo 模板
```text
A single continuous [duration] cinematic shot based strictly on the source image. Preserve the original composition, architecture, subject identity, scale relationships, lighting direction and overall color palette.

The visual anchor is [subject]. It performs [single restrained action] with [speed, weight, inertia]. The motion remains physically coherent and does not change the subject's design or proportions.

The camera uses [camera move], with only a very subtle [secondary move if needed]. Parallax should remain realistic and the shot must avoid revealing large unseen areas that would require invented geometry.

Secondary motion is caused by the primary action: [cause -> response]. Ambient elements move only at low frequency. All wind-driven elements follow one consistent wind field.

Keep lighting stable and temporally continuous. No sudden exposure shift, no color-temperature jump, no object popping, no geometry drift, no flicker. The shot should feel like a natural excerpt from a longer film scene rather than an animation loop.
```

## Veo 特别规则
- 优先“single continuous shot”
- 明确 temporal continuity
- 高风险场景避免多段动作和突然转场
- 更适合把情绪转换为摄影语言而非形容词

---

# 3. Runway Compiler

## 编译目标
强调：主体、动作、摄影机、视觉连续性。输出应更紧凑，避免过多层级说明。

## 顺序
1. Subject + Core Action
2. Camera
3. Preservation
4. Environment Response
5. Visual Tone
6. Negative / Avoidance

## 语言风格
- 简洁
- 主谓明确
- 一个句子只承担一个关键动作
- 避免多重从句

## Runway 模板
```text
[Subject] performs [one core action] slowly and naturally, with realistic weight and inertia. Camera: [single camera move], very stable, subtle parallax only. Preserve the original composition, architecture, identity, proportions, object count and lighting. [Secondary physical response]. [Ambient micro-motion]. Cinematic but restrained, physically coherent, temporally stable. Avoid [core failure items].
```

## Runway 特别规则
- 超过2个明显动作时必须压缩
- Prompt 过长时优先保留动作与摄影机，删除装饰性形容词
- 建筑/文字复杂场景优先静机或极慢推镜

---

# 4. Hailuo / 海螺 Compiler

## 编译目标
强调：可见动作、镜头行为、节奏与整体氛围，语言可更直观。

## 顺序
1. 场景锁定
2. 主体动作
3. 镜头
4. 环境响应
5. 氛围
6. 禁止项

## Hailuo 模板
```text
保持原图构图、人物/动物造型、建筑结构、比例和光线不变。主角[主体]只做[核心动作]，动作缓慢、有重量、连续自然。镜头采用[镜头运动]，幅度很小，画面稳定。由主动作带动[二级响应]，环境仅保留[微运动]。整体[情绪]，但不增加新元素、不改变建筑和主体设计。禁止[核心失败项]。
```

## Hailuo 特别规则
- 中文动作要明确，不写“自然动起来”
- 不把多个环境动态并列成同等级动作
- 3秒场景优先单一视觉事件

---

# 5. 即梦 Compiler

## 编译目标
强调：中文短句、动作层级、场景保真、镜头节奏。

## 顺序
1. 原图保持
2. 主体动作
3. 镜头运动
4. 次级响应
5. 光影与氛围
6. 负面约束

## 即梦模板
```text
严格保持原图人物、建筑、构图、比例、透视和综合色彩。主体[主体]缓慢完成[唯一核心动作]，[惯性说明]。镜头[主镜头]，幅度克制，保持真实视差。次级运动只有[响应1]、[响应2]，环境低频变化，不抢主体。光线方向和曝光稳定。整体[情绪对应摄影语言]。禁止建筑变形、主体增生、身份变化、画面闪烁、物体跳变、镜头突转。
```

## 即梦特别规则
- 先写保真，再写动作
- 3秒内不安排复杂动作链
- 有书法/纹样时必须显式锁定文字与纹理

---

# 6. Platform Router

根据用户输入自动选择：

```yaml
if platform in [Kling, 可灵]: compiler = KLING
elif platform == Veo: compiler = VEO
elif platform == Runway: compiler = RUNWAY
elif platform in [Hailuo, 海螺]: compiler = HAILUO
elif platform == 即梦: compiler = JIMENG
else: compiler = PLATFORM_NEUTRAL
```

若用户未指定平台：
- 默认输出 Platform-Neutral Director Prompt
- 同时给出一句“若使用 Kling，可按 Kling Compiler 压缩”
- 不擅自假定某个平台

---

# 7. Cross-Platform Invariants
无论平台如何，以下内容绝对不允许被编译器改变：

1. Structural Lock
2. 主运动主体
3. 主运动的物理逻辑
4. Camera risk decision
5. 风场方向
6. 时间轴
7. Auto Degrade 结果
8. Negative Focus

平台差异只允许发生在：
- 语言长度
- 表达顺序
- 句式
- 术语密度
- 是否显式描述时间连续性

---

# 8. Multi-Platform Output Mode
当用户说“给我 Kling、Veo、Runway 三版”时：

1. 只进行一次导演分析
2. 只生成一份 IR
3. 分别送入三个 Compiler
4. 不重新决定动作
5. 不重新决定摄影机
6. 三个平台输出必须共享同一主运动逻辑

这样可以避免不同平台版本之间剧情、动作和构图控制互相矛盾。

---

# 9. Compiler Quality Check
每个平台输出前检查：

- 是否先保留了核心锁定信息
- 主运动是否只有一个清晰核心事件
- 摄影机是否与 risk level 匹配
- 是否保留因果响应
- 是否保留统一风场
- 是否删除无关风格词
- 是否针对平台调整语言，而不是改变导演决策
- 是否包含当前画面的核心负面约束
- 是否满足时长预算
- 是否可直接复制到目标平台

若任一平台版本改变了主运动、镜头风险判断或 Structural Lock，视为 Compiler Failure，必须重新编译。