# V6｜Quality Scoring & Self-Repair Engine

## Purpose
在平台 Prompt 编译完成后，不立即输出。先执行质量评分、Hard Fail 检测和自动修复循环，直到达到可接受阈值或达到最大修复轮次。

核心原则：**先检查，再修复；先降低风险，再保留电影感。**

---

## 1. Quality Gate
每个候选 Prompt 必须进入以下状态机：

```text
DRAFT
  ↓
SCORE
  ↓
HARD_FAIL_CHECK
  ↓
PASS? ── YES ─→ RELEASE
  │
  NO
  ↓
DIAGNOSE
  ↓
REPAIR
  ↓
RECOMPILE
  ↓
RESCORE
```

最多自动修复 3 轮。第 3 轮后仍低于阈值时，输出最安全版本，并明确标注“已执行最大降级”。

---

## 2. Score Model｜40 分
沿用 `tests/evaluation-checklist.md`，20 项，每项 0 / 1 / 2 分。

### A. Scene Understanding｜8分
1. 前 / 中 / 后景识别
2. 视觉锚点识别
3. 尺度参照识别
4. 高风险区域识别

### B. Structural Stability｜8分
5. 建筑 / 地形锁定
6. 人物身份 / 比例 / 数量保护
7. 文字 / 书法 / 纹样保护
8. 隐藏面推断控制

### C. Camera｜8分
9. 单一主镜头运动
10. 镜头与情绪匹配
11. 避免快速推拉 / 剧烈旋转 / 无必要环绕
12. 摄影机服务空间而非炫技

### D. Primary Motion｜8分
13. 一级主体明确
14. 明显运动主体 ≤2
15. 动作包含方向 / 速度 / 幅度 / 节奏 / 惯性
16. 动作幅度与主体画面尺寸匹配

### E. Physics & Environment｜8分
17. 二级运动有一级运动因果
18. 风场统一
19. 水 / 云 / 羽毛 / 布料符合基本物理
20. 环境保持辅助地位

### Grade
- 36–40：A / Production Ready
- 31–35：B / Good
- 25–30：C / Risky
- 0–24：D / Reject

默认发布阈值：**score >= 31 且无 Hard Fail**。
目标阈值：**score >= 36 且无 Hard Fail**。

---

## 3. Hard Fail Detector
出现任一项，直接阻止发布：

- 建筑主体被要求呼吸、弯曲、漂移、重构
- 3 秒内存在多个复杂主动作
- 大面积文字 / 书法发生明显形变
- 人物身份、比例、数量未锁定
- 巨型鸟类高频扑翼
- 单张复杂图大幅 orbit
- 多个互相冲突的风向
- 无针对当前图像的负面约束
- 大量风格词替代真实运动设计
- 平台编译器改变了 Director IR 的主运动或镜头风险判断
- 透明巨型灵体执行高风险大幅人体动作且未降级
- 最后一帧突然停止或新增动作

Hard Fail 必须先修复，再评分。

---

## 4. Diagnosis Tags
评分或 Hard Fail 检查后，为问题添加标签：

- `LOCK_WEAK`
- `CAMERA_OVERLOAD`
- `MOTION_OVERLOAD`
- `PHYSICS_WEAK`
- `WIND_CONFLICT`
- `TEXTURE_RISK`
- `IDENTITY_RISK`
- `HIDDEN_GEOMETRY_RISK`
- `ENVIRONMENT_COMPETES`
- `LIGHTING_INSTABILITY`
- `NEGATIVE_TOO_GENERIC`
- `PLATFORM_DRIFT`
- `TIMELINE_OVERLOAD`
- `TEMPORAL_DISCONTINUITY`

标签只用于内部修复，不要求默认展示。

---

## 5. Repair Priority
按以下顺序修复，越靠前优先级越高：

1. Structural Lock
2. Identity / Count
3. Text / Ornament Lock
4. Camera Risk
5. Primary Motion Count
6. Hidden Geometry
7. Physics / Causality
8. Wind Field
9. Environment Competition
10. Lighting Stability
11. Negative Constraints
12. Style Compression

不得为了提高“电影感”降低前 6 项的安全性。

---

## 6. Repair Actions

### LOCK_WEAK
- 将原图构图、建筑、地形、人物身份、数量、文字显式写入首段
- 增加 `strictly preserve / remain structurally fixed / do not redesign`

### CAMERA_OVERLOAD
- 删除辅助镜头
- orbit → slow push-in / static
- crane + pan → 保留其中一个
- camera amplitude × 0.5

### MOTION_OVERLOAD
- 删除第二主动作
- 将复杂动作改为单一动作阶段
- 3秒只保留一个视觉事件

### PHYSICS_WEAK
- 把次级运动改写为 `Cause -> Response`
- 删除无法解释来源的粒子 / 云 / 布料运动

### WIND_CONFLICT
- 统一 direction / strength / stability
- 删除与主风向冲突的软体运动

### TEXTURE_RISK
- 将书法 / 壁画 / 纹样设为 hard lock
- 相关区域只保留微小视差或极轻反光

### IDENTITY_RISK
- 强化脸、服装、体型、位置、人数不变
- 人物很小时进一步缩小动作

### HIDDEN_GEOMETRY_RISK
- 减小视角变化
- 取消大幅侧移 / 环绕
- 改为单轴推镜或静机

### ENVIRONMENT_COMPETES
- 环境运动数量减半
- 高频 → low-frequency
- 显著 → subtle

### LIGHTING_INSTABILITY
- 锁定主光方向 / 色温 / 曝光
- 删除闪烁、日夜变化、强烈光变

### NEGATIVE_TOO_GENERIC
- 根据 scene type 重新生成 8–16 个高相关失败项
- 删除与当前画面无关的负面词

### PLATFORM_DRIFT
- 回滚到 Director IR
- 重新路由平台 Compiler
- 禁止平台版改写主动作、镜头与锁定对象

### TIMELINE_OVERLOAD
- 重新按 0–0.5 / 0.5–2.3 / 2.3–3.0 划分
- 删除后段新增动作

### TEMPORAL_DISCONTINUITY
- 加强 continuous / temporally consistent / no popping / no flicker
- 结尾保持动作自然延续

---

## 7. Repair Loop

```yaml
max_repair_rounds: 3
release_threshold: 31
target_threshold: 36
hard_fail_allowed: false

for round in 1..3:
  detect_hard_fail()
  score_40()
  if score >= target_threshold and hard_fail == false:
    release(PRODUCTION_READY)
  if score >= release_threshold and hard_fail == false and round >= 2:
    release(GOOD)
  diagnose()
  repair_by_priority()
  recompile_from_IR()

if still_failed:
  apply_maximum_safe_degrade()
  release(SAFE_FALLBACK)
```

---

## 8. Maximum Safe Degrade
第三轮仍失败时：

- Camera = Static 或 very slow push-in
- Primary Motion = 1
- Secondary Motion <=1
- Ambient Motion <=1
- Lighting = locked
- No orbit
- No hidden geometry expansion
- No new objects
- 强化结构 / 身份 / 文字 / 数量锁定
- 负面约束只保留最高风险项

目标不是“最炫”，而是“最稳”。

---

## 9. Score Report Object
内部可使用：

```yaml
quality_report:
  score: 34
  grade: B
  hard_fail: false
  repair_round: 1
  diagnosis:
    - CAMERA_OVERLOAD
    - ENVIRONMENT_COMPETES
  repairs:
    - removed_secondary_camera_move
    - reduced_ambient_motion_50_percent
  release_status: GOOD
```

默认用户可见输出只展示：
- Quality Score
- Grade
- 是否触发修复
- 最终状态

除非用户要求，不展示完整内部诊断对象。

---

## 10. Release Status
- `PRODUCTION_READY`：36–40，无 Hard Fail
- `GOOD`：31–35，无 Hard Fail
- `SAFE_FALLBACK`：已最大降级后发布
- `REJECT`：仅当请求本身与原图严重冲突且无法在不改变意图的情况下修复

---

## 11. V6 Final Rule
最终 Prompt 必须满足：

**导演逻辑一致 + 平台表达正确 + 结构稳定 + 物理可信 + 时间连续 + 通过质量门槛。**

Skill 不应把第一次生成的 Prompt 直接视为成品；第一次输出只是 Draft。