# V9｜Shot Memory & Style Consistency Engine

## Purpose
让连续镜头、系列短片或同一视觉项目中的多张图保持一致的摄影机语言、动作尺度、风场、光线、色彩、主体身份与节奏，不让每一张图都被重新“发明”一次。

V9 不替代单镜头导演判断。它只在多镜头 / 连续分镜 / 同系列场景中保存和传递稳定的项目级约束。

核心原则：**单镜头可以变化，项目语法不能漂移。**

---

## 1. Memory Scope
Shot Memory 分为三层：

### PROJECT MEMORY｜项目级
跨所有镜头保持：
- visual_language
- camera_family
- lens_feel
- movement_frequency
- lighting_direction_family
- color_temperature_family
- contrast_level
- wind_field_family
- realism_level
- style_constraints
- recurring_character_identity
- recurring_architecture_rules

### SEQUENCE MEMORY｜段落级
跨一组连续镜头保持：
- sequence_goal
- dominant_mood
- movement_intensity
- camera_direction_bias
- environmental_state
- weather_state
- time_of_day
- continuity_anchor

### SHOT MEMORY｜镜头级
只服务当前镜头：
- current_visual_anchor
- current_primary_motion
- current_camera
- current_risk
- current_preset
- current_release_status

---

## 2. Continuity Anchors
每个连续项目至少选择 3 个 continuity anchors。

推荐锚点：
- recurring character face / costume / hairstyle
- palace / roof / bridge geometry
- moon / sun direction
- dominant wind direction
- warm/cool color bias
- camera movement family
- atmospheric density
- creature scale

若用户未指定，自动从最稳定、最容易跨镜头识别的对象中选择。

---

## 3. Style Memory Object
内部使用：

```yaml
style_memory:
  project_id: optional
  visual_language: restrained_cinematic_fantasy
  camera_family:
    preferred:
      - slow_push_in
      - subtle_crane
      - slow_glide
    avoid:
      - rapid_orbit
      - handheld_shake
  motion_frequency: low
  motion_amplitude: restrained
  lens_feel: medium_telephoto_cinematic
  lighting:
    direction_family: upper_left_soft
    temperature: cool_neutral
    exposure: stable
    contrast: medium_low
  wind:
    direction_family: rear_right
    strength: gentle
    stability: steady
  color:
    saturation: low_medium
    palette: cool_gray_jade
  temporal_style:
    ending: natural_continuation
    hard_stop: false
  subject_rules:
    human: micro_motion
    giant_creature: slow_weighted
    architecture: locked
    spirit: macro_shape_locked
```

默认不向用户展示完整对象。

---

## 4. What Must Persist
若连续镜头属于同一时间、地点或叙事段落，以下属性默认继承：

1. 人物身份与服装
2. 建筑材质与结构
3. 主光大方向
4. 色温家族
5. 风向家族
6. 运动频率
7. 相机运动性格
8. 巨物运动重量感
9. 空气透视与雾气密度区间
10. 结尾运动方式

只有剧情明确改变时才允许覆盖。

---

## 5. Camera Language Consistency
项目内摄影机不能每镜头随机换语法。

### Camera Family
选择最多 3 个主摄影机动作作为全片语法：
- slow_push_in
- slow_pull_back
- subtle_crane
- slow_glide
- static
- tiny_truck

连续 3 个镜头内，若出现 3 种以上完全不同的镜头语法，标记 `CAMERA_STYLE_DRIFT`。

### Direction Bias
如果上一镜头总体向前 / 向上运动，下一镜头除非剧情需要，不应突然反向强拉远或快速下坠。

---

## 6. Motion Intensity Memory
定义项目级 motion_intensity：

- VERY_LOW
- LOW
- MEDIUM
- HIGH（仅低风险项目）

若上一镜头 LOW，本镜头没有剧情理由，不得突然升到 HIGH。

最大默认变化：每相邻镜头最多变化一个等级。

例如：
`LOW → MEDIUM` 允许；`LOW → HIGH` 需要剧情理由。

---

## 7. Wind Continuity
同一连续场景：
- 主风向默认继承
- 风力最多小幅变化
- 所有头发 / 飘带 / 羽毛 / 旗帜 / 薄雾继续服从同一风场

若镜头切到室内、背风区或剧情明确风向变化，可创建 wind override，但必须说明原因。

---

## 8. Light & Color Continuity
默认继承：
- key light direction family
- color temperature family
- exposure range
- saturation range
- contrast range

禁止相邻镜头无原因出现：
- 冷暖大跳变
- 正午 → 黄昏
- 曝光突然提升
- 天空综合色突然变化

若时间跳跃明确，则创建 `TIME_JUMP` 并允许新 Memory Segment。

---

## 9. Recurring Character Lock
同一人物跨镜头保持：
- face identity
- hairstyle
- costume structure
- costume color
- body proportion
- age appearance
- accessories

镜头尺度变化只允许改变动作幅度，不允许重新设计人物。

小景别：动作更少；近景：允许更细微表情，但身份必须完全一致。

---

## 10. Recurring Creature Lock
凤凰 / 仙鹤 / 巨兽跨镜头保持：
- wing count
- feather color family
- tail structure
- body scale
- horn / crest / head shape
- movement weight

不得前一镜头巨型凤凰慢扑翼，下一镜头突然变成小鸟式高频扇翅。

---

## 11. Architecture Continuity
同一建筑群：
- roof geometry
- ridge direction
- column rhythm
- material family
- color palette
- scale relationships

所有镜头继续保持建筑运动预算 = 0。

---

## 12. Memory Update Rule
每个镜头发布后，只把稳定且通过 Quality Gate 的属性写入 Memory。

```text
DRAFT 不写入
REJECT 不写入
SAFE_FALLBACK 可写入结构与风格锁定，不写入失败动作
GOOD 可写入
PRODUCTION_READY 可完整写入
```

这能避免把错误输出传递到后续镜头。

---

## 13. Memory Conflict Resolution
冲突优先级：

`用户当前明确指令 > Structural Lock > Story Continuity > Project Memory > Sequence Memory > Shot Preset > Platform Expression`

如果用户明确要求“这一镜头突然狂风”，可以覆盖 wind memory，但只影响当前段落；后续是否延续必须重新判断。

---

## 14. Continuity Drift Detector
每个新镜头输出前检查：

- CAMERA_STYLE_DRIFT
- MOTION_INTENSITY_DRIFT
- WIND_DIRECTION_DRIFT
- LIGHTING_DRIFT
- COLOR_DRIFT
- CHARACTER_IDENTITY_DRIFT
- CREATURE_SCALE_DRIFT
- ARCHITECTURE_STYLE_DRIFT
- TEMPORAL_STYLE_DRIFT

命中 2 项以上必须执行 Continuity Repair。

---

## 15. Continuity Repair
修复顺序：

1. 恢复人物 / 建筑 / 生物身份锁定
2. 恢复主光方向与色温家族
3. 恢复主风向
4. 将相机动作拉回 camera_family
5. 降低运动强度到相邻镜头可接受范围
6. 恢复色彩饱和度 / 对比度区间
7. 恢复自然延续式结尾

---

## 16. Sequence Handoff Object
连续镜头之间可传递：

```yaml
handoff:
  previous_shot:
    release_status: PRODUCTION_READY
    camera: slow_push_in
    camera_direction: forward
    motion_intensity: LOW
    wind_direction: rear_right
    lighting_direction: upper_left
    color_temperature: cool_neutral
    primary_subject: woman
    ending_state: gaze_up_continues
  next_shot_constraints:
    preserve_camera_family: true
    preserve_wind: true
    preserve_light_family: true
    preserve_identity: true
    max_motion_intensity_change: 1_level
```

---

## 17. Multi-Shot Workflow
当用户上传多张连续图或要求“做一组统一风格镜头”时：

1. 第一张图建立 Project Memory
2. 每张图独立进行 V8 Preset + V7 Shot Planner
3. 生成候选后先执行 V9 Continuity Check
4. 再进入 Platform Compiler
5. 再执行 V6 Quality Gate
6. 只有 RELEASE 的镜头更新 Memory
7. 后续镜头继承上一个稳定状态

---

## 18. V9 Final Rule
连续镜头的目标不是“每一镜头都最炫”，而是让观众感觉它们来自同一位摄影指导、同一个物理世界、同一个时间连续体。

最终原则：

**角色一致 > 空间一致 > 光线一致 > 风场一致 > 摄影机语法一致 > 单镜头炫技。**