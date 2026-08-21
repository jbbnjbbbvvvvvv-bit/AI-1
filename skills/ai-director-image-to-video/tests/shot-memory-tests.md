# V9｜Shot Memory & Style Consistency Tests

## Purpose
验证连续镜头是否保持同一摄影机语法、角色身份、风场、光线、色彩、巨物尺度和建筑结构，并确认只有通过 Quality Gate 的稳定结果才写入 Memory。

---

## Test 01｜同一人物连续三镜头
输入：同一女性角色，镜头1远景、镜头2中景、镜头3近景。

应保持：
- face identity 一致
- hairstyle / costume / accessories 一致
- camera_family 不随机跳变
- 风向一致
- 色温一致

允许：景别变化导致表演细节增加。

Fail：人物脸型、服装或发型被重新设计。

---

## Test 02｜古建筑连续镜头
输入：同一宫殿建筑群，多角度但仍为单张图转视频镜头序列。

应保持：
- roof geometry
- ridge direction
- material family
- palette
- architecture_motion_budget = 0

Fail：第二镜头屋檐比例改变或建筑产生呼吸感。

---

## Test 03｜凤凰连续镜头
镜头1：巨型凤凰滑翔。
镜头2：凤凰继续飞过宫殿。

应保持：
- wing count
- tail structure
- feather color family
- giant scale
- slow weighted motion

Fail：第二镜头变成高频小鸟扑翼。

---

## Test 04｜统一风场
连续场景中人物发丝、飘带、旗帜、尾羽均受风。

应保持主风向 family 一致。

Fail：镜头1向右，镜头2无剧情理由改向左。

---

## Test 05｜光线连续
连续时间段内保持：
- key light direction family
- color temperature family
- exposure range
- contrast range

Fail：无时间跳跃却从冷白晨光突然变橙色黄昏。

---

## Test 06｜Camera Style Drift
项目 camera_family = slow_push_in / subtle_crane / static。

连续镜头如果出现：rapid orbit + handheld shake + fast zoom，应触发 `CAMERA_STYLE_DRIFT` 并修复。

---

## Test 07｜Motion Intensity Drift
上一镜头 motion_intensity = LOW。
下一镜头无剧情理由直接 HIGH。

应触发 `MOTION_INTENSITY_DRIFT`，将强度限制为 MEDIUM 或更低。

---

## Test 08｜时间跳跃 override
镜头1白天，镜头2明确“多年后黄昏”。

应允许创建新 Memory Segment，而不是强制继承旧色温和曝光。

Pass 条件：明确记录 `TIME_JUMP`。

---

## Test 09｜失败结果不得污染 Memory
若某镜头状态：
- DRAFT
- REJECT

不得写入动作和视觉变化到 Memory。

SAFE_FALLBACK 只允许写入结构锁定与稳定风格，不写入失败动作。

---

## Test 10｜Sequence Handoff
镜头1结尾：人物继续抬头看向天空。
镜头2开头：应继承 gaze_up_continues，而不是无原因低头。

应通过 handoff 保留 ending_state。

---

## Test 11｜多平台一致
同一连续镜头分别编译为 Kling / Veo / Runway。

应保持：
- same primary motion
- same camera family
- same wind family
- same lighting family
- same continuity anchors

Fail：平台 Compiler 改变剧情或主体动作。

---

## Test 12｜Continuity Drift Threshold
若新镜头同时触发：
- CAMERA_STYLE_DRIFT
- LIGHTING_DRIFT

必须执行 Continuity Repair。

若只出现一个轻微 drift，可先标记并保留，但不得影响 Structural Lock。

---

## Acceptance
V9 通过条件：

- 连续镜头 identity drift = 0
- architecture drift = 0
- 风向无无理由反转
- 相邻镜头运动强度最多变化一个等级
- camera_family 保持稳定
- 只有 RELEASE 状态写入 Memory
- 命中2个以上 drift tag 必须自动修复
- 平台编译不得改变 continuity memory
