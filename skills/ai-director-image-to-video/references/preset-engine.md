# V8｜Adaptive Parameter Preset Engine

## Purpose
把时长、画幅、风险等级、主体类型和目标平台转换成稳定的默认参数组合，减少每次从零设计镜头。

V8 不替代 Auto Director、Adaptive Shot Planner、Platform Compiler 或 Self-Repairer。它只提供“参数起点”。最终参数仍必须经过风险判断、候选选择和质量门槛。

核心原则：**Preset 是默认值，不是硬编码；结构风险始终可以覆盖预设。**

---

## 1. Preset Input
Preset Router 至少读取：

```yaml
duration: 3s | 5s | 8-10s
aspect_ratio: 9:16 | 16:9 | 2.39:1 | source
risk_level: LOW | MEDIUM | HIGH
dominant_scene: HUMAN | CREATURE | ARCHITECTURE | WATER | ATMOSPHERE | ENTITY | TEXTURE_LOCK | MIXED
platform: Kling | Veo | Runway | Hailuo | Jimeng | Neutral
mood: optional
```

---

## 2. Duration Presets

### DUR_3S
适用于短镜头和高稳定性输出。

```yaml
primary_event_count: 1
primary_motion_count: 1
secondary_motion_max: 2
ambient_motion_max: 2
camera_primary_count: 1
camera_secondary_max: 1
timeline:
  establish: 0.0-0.5
  action: 0.5-2.3
  continuation: 2.3-3.0
new_action_after: 2.3s_forbidden
```

规则：不追求完整动作闭环，只保留“动作正在发生”的可信片段。

### DUR_5S
```yaml
primary_event_count: 1
primary_motion_count: 1
secondary_motion_max: 2
ambient_motion_max: 2
camera_primary_count: 1
camera_secondary_max: 1
timeline:
  establish: 0-1
  development: 1-4
  continuation: 4-5
```

允许主动作有“启动 → 发展 → 惯性”三个阶段，但不默认增加第二剧情事件。

### DUR_8_10S
```yaml
primary_event_count: 1
primary_motion_count: 1
secondary_motion_max: 3
ambient_motion_max: 3
camera_primary_count: 1
camera_secondary_max: 1
narrative_phases: 3
```

可以出现同一主事件的前后阶段，不自动扩展为多镜头蒙太奇。

---

## 3. Aspect Ratio Presets

### AR_9_16
竖屏优先保护人物、纵向建筑、瀑布和上下尺度关系。

- 横向 truck / orbit 幅度自动降低
- 优先 push-in / pull-back / crane / tilt
- 主体尽量保持在安全中心区
- 大型翼展若横跨画面，进一步减少横向镜头运动

### AR_16_9
通用电影叙事画幅。

- 允许适度横向层次与前后景视差
- 可使用 slow dolly / glide / tiny truck
- 仍遵守 1 主镜头原则

### AR_2_39_1
超宽画幅强调横向空间与尺度。

- 可利用横向层次、负空间与远景
- 近景主体位于边缘时禁止大幅 lateral move
- 复杂建筑依然优先 slow push / static
- 不因为宽画幅就默认做 orbit

---

## 4. Risk Presets

### RISK_LOW
```yaml
shot_profile: BALANCED
camera_strength: 0.65
primary_strength: 0.70
secondary_density: 0.60
ambient_density: 0.50
lighting_variation: 0.25
safety_reserve: 0.10
```

仅在结构简单、隐藏面少、无文字锁定时允许 EXPRESSIVE。

### RISK_MEDIUM
```yaml
shot_profile: BALANCED
camera_strength: 0.45
primary_strength: 0.60
secondary_density: 0.45
ambient_density: 0.35
lighting_variation: 0.15
safety_reserve: 0.20
```

若包含古建 / 文字 / 透明灵体 / 巨型羽毛之一，shot_profile 回退 SAFE。

### RISK_HIGH
```yaml
shot_profile: SAFE
camera_strength: 0.25
primary_strength: 0.45
secondary_density: 0.30
ambient_density: 0.20
lighting_variation: 0.05
safety_reserve: 0.35
orbit: false
```

---

## 5. Scene Presets

### HUMAN_MICRO
适用：人物占画面 <10%。

```yaml
camera: slow_push_in | static
primary_motion: breathing | micro_head_raise | subtle_gaze_shift
body_translation: none
hand_complexity: minimal
cloth_hair: subtle
```

### HUMAN_MEDIUM
适用：人物约10–30%。

```yaml
camera: slow_push_in | tiny_dolly
primary_motion: gaze_shift | head_turn | wrist_adjustment | small_weight_shift
step_distance: <= half_step
finger_complexity: low
```

### CREATURE_GIANT_WING
适用：凤凰、巨鸟、仙鹤近景或翼展明显。

```yaml
camera: micro_pull_back | slow_glide | subtle_tilt
primary_motion: one_weighted_downstroke_then_glide
wingbeat_3s_max: 1
feather_response: delayed_flex
secondary: tail_inertia
```

### ARCHITECTURE_LOCKED
```yaml
camera: static | slow_push_in | tiny_crane
architecture_motion_budget: 0
allowed_soft_motion: flags | curtains | hanging_elements
hidden_geometry_expansion: minimal
```

### WATER_GRAVITY
```yaml
camera: slow_glide | static | tiny_crane
primary_motion: gravity_driven_flow
secondary: mist | ripple | spray
flow_direction_lock: true
```

### ATMOSPHERE_LOW_FREQ
```yaml
camera: static | slow_push | slow_glide
primary_or_ambient: low_frequency_drift
frequency: low
opacity_change: subtle
```

### ENTITY_INTERNAL_FLOW
```yaml
camera: static | slow_crane | micro_push
macro_shape: locked
primary_motion: internal_medium_flow
limb_action: avoid
opacity_change: subtle_continuous
```

### TEXTURE_HARD_LOCK
```yaml
camera: static | tiny_push
surface_deformation: forbidden
text_regeneration: forbidden
reflection_change: minimal
```

---

## 6. Mood Presets

### MOOD_OPPRESSIVE
- low angle
- slow push-in
- foreground compression
- strong scale contrast
- low motion frequency

### MOOD_EPIC
- layered depth
- slow weighted motion
- atmospheric perspective
- controlled crane / glide

### MOOD_BEAUTIFUL
- soft secondary motion
- restrained highlight variation
- no decorative particle overload

### MOOD_CALM
- static / very slow camera
- low-frequency subject motion
- minimal environment motion

### MOOD_MYSTERIOUS
- partial occlusion
- slow reveal
- fog depth
- restrained exposure

### MOOD_TENSE
- micro push
- limited FOV
- restrained subject motion
- no chaotic shake by default

---

## 7. Preset Merge Order
参数合并必须遵守：

`STRUCTURAL LOCK > RISK PRESET > SCENE PRESET > DURATION PRESET > ASPECT PRESET > MOOD PRESET > PLATFORM EXPRESSION`

冲突示例：

- 2.39:1 允许横向空间，但 HIGH RISK 禁止大幅 lateral move → 以 HIGH RISK 为准。
- EPIC 建议 crane，但 TEXTURE_HARD_LOCK + 强透视 → 回退 tiny push / static。
- LOW RISK 允许 EXPRESSIVE，但复杂书法出现 → 强制 SAFE。

---

## 8. Preset Router

```yaml
preset_selection:
  duration_preset: DUR_3S
  aspect_preset: AR_16_9
  risk_preset: RISK_HIGH
  scene_preset: CREATURE_GIANT_WING
  mood_preset: MOOD_EPIC
  resulting_shot_profile: SAFE
```

Router 只提供候选默认值，随后交给 `adaptive-shot-planner.md` 生成 SAFE / BALANCED / EXPRESSIVE 候选并评分。

---

## 9. Parameter Clamp
所有数值化强度最终约束在 0–1：

- camera_strength
- primary_strength
- secondary_density
- ambient_density
- lighting_variation
- safety_reserve

规则：

```text
HIGH risk: camera_strength <= 0.30
MEDIUM risk: camera_strength <= 0.55
LOW risk: camera_strength <= 0.75

TEXTURE_LOCK: lighting_variation <= 0.10
ARCHITECTURE: architecture_motion_budget = 0
ENTITY: limb_action_complexity <= 0.20
GIANT_CREATURE_3S: wingbeat_count <= 1
```

---

## 10. Preset Output Object

```yaml
preset_output:
  duration: 3s
  aspect_ratio: 16:9
  risk: HIGH
  shot_profile: SAFE
  camera:
    type: slow_glide
    strength: 0.22
  primary:
    subject: phoenix
    action: one_weighted_downstroke_then_glide
    strength: 0.45
  secondary:
    max_count: 2
    density: 0.30
  ambient:
    max_count: 1
    density: 0.18
  lighting:
    variation: 0.05
  safety_reserve: 0.35
```

默认不向用户展示该对象；只有用户要求查看参数时才输出。

---

## 11. V8 Final Rule
Preset 的价值是让系统快速落到“稳定起点”，而不是把导演判断机械模板化。

最终顺序：

**先锁结构 → 再识别风险 → 再套 Preset → 再生成候选 → 再评分 → 再编译 → 再自修复。**