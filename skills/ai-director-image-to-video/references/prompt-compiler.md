# V3 Prompt Compiler — Director Analysis → Production Prompt

## 目标
把导演分析自动编译为可直接粘贴到图转视频平台的成品提示词。Compiler 不重新创作场景，只压缩、排序、消歧和约束已有导演决策。

## 编译优先级

`STRUCTURE LOCK > PRIMARY SUBJECT > PRIMARY ACTION > CAMERA > SECONDARY RESPONSE > AMBIENT MOTION > LIGHT > STYLE > NEGATIVE`

任何风格词不得覆盖结构锁定和物理运动规则。

## Intermediate Representation（IR）

在生成最终 Prompt 前，内部先形成：

```yaml
shot:
  duration: 3s
  aspect_ratio: 16:9
  platform: Kling
  risk: HIGH
locks:
  composition: true
  architecture: true
  identity: true
  count: true
  text_texture: true
camera:
  primary: slow_push_in
  secondary: subtle_drift
  amplitude: very_low
primary_motion:
  subject: phoenix
  action: one_weighted_downstroke_then_glide
  speed: slow
  amplitude: low
secondary_motion:
  - tail_feathers_follow_with_delayed_inertia
  - nearby_thin_clouds_roll_slightly_from_wing_pressure
ambient:
  - distant_clouds_slow_drift
wind:
  direction: consistent
  strength: light
light:
  lock_direction: true
  variation: subtle_material_highlight_only
negative:
  - extra_wings
  - architectural_deformation
  - camera_shake
  - flicker
```

IR 不必默认展示给用户，但最终提示词必须与 IR 一致。

## Kling 编译顺序

### Block A — Preservation
一句话明确原图必须保持不变的内容。复杂建筑、书法、人物身份和主体数量优先锁定。

### Block B — Primary Motion
只描述最重要的主体和动作。必须包含速度、幅度、方向、惯性或节奏中的关键项。

### Block C — Camera
原则上只允许 1 个主摄影机运动 + 1 个极弱辅助运动。HIGH risk 禁止大幅 orbit。

### Block D — Physical Response
只保留与主动作存在因果关系的二级运动。例如翼压→云雾局部卷动；瀑布→水雾扩散。

### Block E — Ambient
最多 2–3 个低频微运动。环境不能与主体争夺注意力。

### Block F — Light & Look
锁定主光方向、曝光、色温，只允许连续微弱材质高光变化。电影质感词放最后。

### Block G — Negative
只保留当前场景最可能发生的 8–16 个失败项，禁止堆砌无关负面词。

## 3秒压缩规则

3秒视频默认执行：

- 一个视觉事件
- 一个主摄影机运动
- 一个一级主体
- 最多两个明显动作阶段
- 最多三个环境微运动
- 不在最后 0.2 秒增加新动作

若原始导演方案超过预算，Compiler 按以下顺序删除：

1. 装饰性粒子
2. 无因果环境运动
3. 光影变化
4. 第二辅助镜头运动
5. 第二主体动作

不得删除结构锁定。

## Motion Verbs

优先使用可执行、可观察的动词：

- slowly raises
- subtly turns
- glides forward
- completes one weighted wing downstroke
- drifts continuously
- follows with delayed inertia
- expands outward after impact
- remains structurally fixed

避免空泛词：dynamic, amazing movement, cinematic motion, magical movement。

## 物理修饰词

需要时加入：weighted, restrained, low-frequency, continuous, subtle, inertia-driven, gravity-driven, physically coherent, temporally consistent。

## 中文 Kling 成品模板

```text
基于原始图片进行3秒图转视频。严格保持[结构锁定对象]的原始构图、比例、透视、数量与空间关系，不重新设计、不变形、不漂移。

主运动：[主体]以[速度/幅度]完成[唯一核心动作]，[惯性/节奏说明]。

镜头：[一个主镜头运动]，[可选极弱辅助运动]，整体稳定，不大幅改变视角，不暴露大量原图不可见结构。

物理响应：[由主动作直接引发的1–2项响应]。环境仅有[低频微运动]，所有受风对象遵循同一风向。

保持原始主光方向、色温与曝光，只允许连续细微的材质高光变化。真实摄影、自然空气透视、真实重量感、电影级光影、自然运动模糊、时间一致性。

负面：[...]。
```

## 极简版模板

```text
锁定[结构]。主运动只有[主体+动作]。镜头[主镜头]。仅保留[物理响应]和[环境微动]。真实重量、统一风场、稳定光线、时间连续。禁止[核心失败项]。
```

## 自动降级

出现任一情况时自动降低运动强度：

- HIGH risk
- 人物面部占比很小但要求复杂表演
- 大量书法/纹样
- 复杂斗拱/屋檐
- 巨型羽翼横跨画面
- 强透视且隐藏面很多
- 透明巨型灵体

降级方法：camera amplitude × 0.5；主体动作减少为一个；环境运动减少一半；orbit → push-in/static；复杂肢体动作 → 呼吸/凝视/滑翔/介质内部流动。

## Compiler 最终自检

输出前逐项回答 YES：

1. 第一段是否先锁结构？
2. 是否能一句话指出唯一主运动？
3. 摄影机是否只有一个主要运动？
4. 二级运动是否有物理原因？
5. 是否存在方向冲突？
6. 3秒内动作是否真的做得完？
7. 是否要求模型生成原图不可见的大量隐藏面？
8. 负面词是否针对当前画面？
9. 是否避免让建筑主体运动？
10. 最终 Prompt 是否可以直接复制到平台？

若第 3、4、6、7 任一项不合格，必须先自动简化，再输出。