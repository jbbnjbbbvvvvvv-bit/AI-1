# V8 Preset Engine Acceptance Tests

## Test Goal
验证 `references/preset-engine.md` 是否能够在不改变导演核心决策的前提下，根据时长、画幅、风险、场景与情绪生成稳定参数起点。

---

## Case 1｜3秒 + 16:9 + HIGH + 巨型凤凰 + 宏大

Expected:
- duration_preset = DUR_3S
- aspect_preset = AR_16_9
- risk_preset = RISK_HIGH
- scene_preset = CREATURE_GIANT_WING
- mood_preset = MOOD_EPIC
- shot_profile = SAFE
- wingbeat_count <= 1
- camera_strength <= 0.30
- orbit = false
- primary_motion_count = 1

Hard fail if:
- 高频扑翼
- 大幅 orbit
- 两个以上主动作

---

## Case 2｜3秒 + 9:16 + MEDIUM + 小人物 + 宁静

Expected:
- scene_preset = HUMAN_MICRO
- camera = static or slow_push_in
- 横向 truck 幅度降低
- body_translation = none
- primary_motion = breathing / micro_head_raise / gaze_shift
- shot_profile = BALANCED

---

## Case 3｜5秒 + 2.39:1 + LOW + 云海瀑布 + 宏大

Expected:
- duration_preset = DUR_5S
- aspect_preset = AR_2_39_1
- scene presets include WATER_GRAVITY + ATMOSPHERE_LOW_FREQ
- camera may use slow_glide / crane
- primary event remains 1
- waterfall flow direction locked
- cloud motion low-frequency

---

## Case 4｜3秒 + 16:9 + MEDIUM + 古建筑 + 书法巨幕

Expected:
- dominant risk escalates toward SAFE
- scene presets include ARCHITECTURE_LOCKED + TEXTURE_HARD_LOCK
- architecture_motion_budget = 0
- surface_deformation = forbidden
- camera = static or tiny_push
- lighting_variation <= 0.10
- EXPRESSIVE not allowed

---

## Case 5｜3秒 + 16:9 + HIGH + 透明巨型灵体 + 神秘

Expected:
- scene_preset = ENTITY_INTERNAL_FLOW
- macro_shape = locked
- primary_motion = internal_medium_flow
- limb_action complexity <= 0.20
- camera = static / slow_crane / micro_push
- shot_profile = SAFE

---

## Case 6｜LOW 风险但出现大面积文字

Expected conflict resolution:
- LOW risk preset originally allows BALANCED / EXPRESSIVE
- TEXTURE_HARD_LOCK overrides expressive behavior
- resulting shot_profile = SAFE or BALANCED with hard texture lock
- text regeneration forbidden

Pass condition: Preset merge order obeys Structural Lock > Risk > Scene > Duration > Aspect > Mood > Platform.

---

## Case 7｜2.39:1 宽画幅 + HIGH 风险复杂建筑

Expected conflict resolution:
- wide aspect may permit lateral composition
- HIGH risk forbids large lateral camera move
- result = static / slow_push / tiny_crane
- no wide orbit

---

## Case 8｜10秒 + LOW + 单人物 + 唯美

Expected:
- duration_preset = DUR_8_10S
- one narrative event with phases
- not automatically converted into montage
- primary_motion_count = 1
- secondary_motion_max <= 3
- camera remains one primary + one weak secondary

---

## Acceptance Criteria
全部测试必须满足：

- Preset 不修改 Structural Lock
- Preset 不重新选择剧情
- Risk 可覆盖 Aspect / Mood 的激进参数
- Scene-specific constraints 可收紧通用参数
- 3秒镜头保持单一视觉事件
- HIGH risk camera_strength <= 0.30
- Architecture motion budget = 0
- Giant creature 3s wingbeat <= 1
- Texture lock lighting variation <= 0.10
- 最终参数仍需送入 V7 Adaptive Shot Planner 与 V6 Self-Repairer

若任一测试失败，不得将 V8 标记为稳定版本。