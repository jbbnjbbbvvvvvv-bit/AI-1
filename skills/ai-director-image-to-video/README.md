# AI Director Image-to-Video Skill

这是一个面向 Kling / 可灵、Runway、Veo、Hailuo、即梦等图转视频平台的 AI 导演 Skill。

它的核心不是堆叠“电影感、8K、IMAX”等风格词，而是先把静态图理解为真实摄影机拍摄到的物理世界，再决定什么必须锁定、谁应该运动、摄影机如何移动、环境如何响应，并在连续镜头中保持角色、建筑、光线、风场和摄影语言一致。

## 当前版本

**V9 — Shot Memory & Style Consistency Engine**

当前流程：

`原图拉片 → 场景分类 → Structural Lock → 风险评分 → 主运动选择 → V8 Preset Router → Parameter Clamp → Director IR → V7 SAFE/BALANCED/EXPRESSIVE 候选 → Stability Score → V9 Continuity Check → Platform Router → Platform Compiler → V6 40分评分 → Hard Fail → Diagnose → Repair → Recompile → Rescore → Memory Update → Release`

## 目录

- `SKILL.md`：核心 Skill。
- `references/director-rules.md`：专项导演规则库。
- `references/prompt-compiler.md`：V3 通用 Prompt Compiler。
- `references/auto-director-decision-tree.md`：V4 自动导演决策树。
- `references/platform-compilers.md`：V5 平台专用编译器与 Platform Router。
- `references/self-repairer.md`：V6 自动评分、诊断、自我修复与安全降级。
- `references/adaptive-shot-planner.md`：V7 SAFE / BALANCED / EXPRESSIVE 自适应镜头规划器。
- `references/preset-engine.md`：V8 时长 / 画幅 / 风险 / 场景 / 情绪参数预设与 Clamp。
- `references/shot-memory.md`：V9 多镜头 Shot Memory、Continuity Anchor、Drift Detector 与 Handoff。
- `examples/golden-examples.md`：标准测试案例。
- `examples/compiler-examples.md`：导演分析 → IR → 平台 Prompt 编译案例。
- `tests/evaluation-checklist.md`：40分质量评估与 Hard Fail 检查。
- `tests/adaptive-shot-planner-tests.md`：V7 镜头规划验收测试。
- `tests/preset-engine-tests.md`：V8 参数预设验收测试。
- `tests/shot-memory-tests.md`：V9 连续性与风格一致性测试。

## 推荐输入

```text
原图：上传图片 / 多张连续图片
时长：3秒
画幅：16:9
主运动对象：可选
镜头感受：压迫 / 宏大 / 唯美 / 宁静
生成平台：Kling / Veo / Runway / Hailuo / 即梦
附加要求：静音 / 锁文字 / 不允许环绕 / 不新增元素 / 保持连续镜头风格统一
```

如果只提供“原图 + 时长 + 平台”，Skill 自动进入 **Auto Director Mode**。如果是连续分镜、系列短片或多张同场景图片，则自动进入 **V9 Shot Memory Mode**。

## V9 Shot Memory

V9 把连续性分成三层：

- `PROJECT MEMORY`：整个项目共享的视觉语言、camera family、镜头运动频率、光线、色温、风场、角色和建筑规则。
- `SEQUENCE MEMORY`：一个连续段落共享的情绪、天气、时间、运动强度、方向偏好和 continuity anchors。
- `SHOT MEMORY`：单个镜头当前的主动作、camera、risk、preset 和 release status。

### 默认连续性锚点

连续项目至少选 3 个 continuity anchors，例如：

- 人物脸 / 发型 / 服装
- 宫殿 / 屋顶 / 桥梁几何
- 主光方向
- 风向
- 色温与综合色
- camera family
- 巨物尺度

### Drift Detector

自动检查：

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

### Memory 写入规则

- `DRAFT`：不写入
- `REJECT`：不写入
- `SAFE_FALLBACK`：只写入结构和稳定风格，不写失败动作
- `GOOD`：可写入
- `PRODUCTION_READY`：完整写入

这样可以避免上一镜头的失败结果污染后续镜头。

## V8 Preset Router

根据时长、画幅、风险、场景、情绪和平台生成参数起点。

关键约束：

- HIGH risk：`camera_strength <= 0.30`
- MEDIUM risk：`camera_strength <= 0.55`
- LOW risk：`camera_strength <= 0.75`
- 复杂文字：`lighting_variation <= 0.10`
- 建筑主体：`motion budget = 0`
- 巨型灵体：`limb_action_complexity <= 0.20`
- 巨型凤凰 3 秒：`wingbeat_count <= 1`

## V7 Adaptive Shot Planner

同一 Director IR 生成最多三档候选：

- `SAFE`：最高稳定性
- `BALANCED`：稳定性与电影感平衡
- `EXPRESSIVE`：仅 LOW RISK 且结构简单时启用

默认候选 Stability Score 必须 >=80 且无 Hard Reject。

## V6 Quality Gate

第一次平台 Prompt 只视为 `DRAFT`。

必须执行：

`SCORE → HARD_FAIL_CHECK → DIAGNOSE → REPAIR → RECOMPILE → RESCORE`

最多自动修复 3 轮。

- 36–40：`PRODUCTION_READY`
- 31–35：`GOOD`
- 25–30：继续修复
- 0–24：强制重构

## 核心原则

- 先锁结构，再动镜头。
- 先做风险控制，再做电影化。
- 连续镜头先守住共同语法，再设计单镜头变化。
- 建筑不动，环境回应。
- 人物越小，动作越少。
- 巨物越大，动作越慢。
- 形可以不动，质可以流动。
- 平台表达可以变化，导演决策不能变化。
- Preset 是起点，不是导演替代品。
- 第一次 Prompt 只是 Draft，不是成品。
- 生成稳定性优先于文字华丽程度。
- 不是让所有东西动，而是让观众相信整个世界正在运行。

## 适用场景

尤其适合：东方玄幻 / 仙侠、古建筑与历史场景、巨型生物 / 凤凰 / 仙鹤、云海 / 瀑布 / 水汽、人物凝视 / 极小动作、巨型灵体 / 能量体、复杂前中后景电影构图、连续分镜、系列短片和同一角色跨镜头一致性控制。