# AI Director Image-to-Video Skill

这是一个面向 Kling / 可灵、Runway、Veo、Hailuo、即梦等图转视频平台的 AI 导演 Skill。

它的核心不是堆叠“电影感、8K、IMAX”等风格词，而是先把静态图理解为真实摄影机拍摄到的物理世界，再决定：

- 什么绝对不能动
- 谁应该成为主运动主体
- 摄影机应该如何移动
- 哪些次级运动来自真实物理因果
- 哪些环境动态应该被压低
- 如何降低建筑、人物、动物和纹理的 AI 变形风险
- 如何把同一导演 IR 编译为不同平台最适合的提示词
- 如何在发布前自动评分、Hard Fail 检查并自我修复
- 如何在 SAFE / BALANCED / EXPRESSIVE 三档候选中自动选择最稳的一版
- 如何根据时长、画幅、风险、场景和情绪自动生成稳定参数起点

## 当前版本

**V8 — Adaptive Parameter Preset Engine**

当前流程：

`原图拉片 → 场景分类 → Structural Lock → 风险评分 → 主运动选择 → V8 Preset Router → Parameter Clamp → Director IR → V7 SAFE/BALANCED/EXPRESSIVE 候选 → Stability Score → Auto Selection → Platform Router → Platform Compiler → V6 40分评分 → Hard Fail → Diagnose → Repair → Recompile → Rescore → Release`

## 目录

- `SKILL.md`：核心 Skill。
- `references/director-rules.md`：专项导演规则库。
- `references/prompt-compiler.md`：V3 通用 Prompt Compiler。
- `references/auto-director-decision-tree.md`：V4 自动导演决策树。
- `references/platform-compilers.md`：V5 平台专用编译器与 Platform Router。
- `references/self-repairer.md`：V6 自动评分、诊断、自我修复与安全降级。
- `references/adaptive-shot-planner.md`：V7 SAFE / BALANCED / EXPRESSIVE 自适应镜头规划器。
- `references/preset-engine.md`：V8 时长 / 画幅 / 风险 / 场景 / 情绪参数预设与 Clamp。
- `examples/golden-examples.md`：标准测试案例。
- `examples/compiler-examples.md`：导演分析 → IR → 平台 Prompt 编译案例。
- `tests/evaluation-checklist.md`：40分质量评估与 Hard Fail 检查。
- `tests/adaptive-shot-planner-tests.md`：V7 镜头规划验收测试。
- `tests/preset-engine-tests.md`：V8 参数预设验收测试。

## 推荐输入格式

```text
原图：上传图片
时长：3秒
画幅：16:9
主运动对象：可选
镜头感受：压迫 / 宏大 / 唯美 / 宁静
生成平台：Kling / Veo / Runway / Hailuo / 即梦
附加要求：静音 / 锁文字 / 不允许环绕 / 不新增元素
```

如果只提供“原图 + 时长 + 平台”，Skill 自动进入 **Auto Director Mode**，无需用户先定义动作和镜头。

## 默认输出结构

1. 导演判断
2. 空间分层
3. 风险评级
4. 推荐 Preset 与参数摘要
5. 推荐镜头档位（SAFE / BALANCED / EXPRESSIVE）
6. Stability Score 与选择理由
7. 运动预算
8. 镜头设计
9. 主体运动设计
10. 环境因果
11. 时间轴
12. 正式平台提示词
13. 极简版提示词
14. 负面提示词
15. Quality Score / Grade
16. 是否触发修复
17. Release Status

Director IR 与完整 preset_output 默认隐藏，用户要求时再显示。

## V8 Preset Router

Preset Router 根据：

- 时长：3s / 5s / 8–10s
- 画幅：9:16 / 16:9 / 2.39:1
- 风险：LOW / MEDIUM / HIGH
- 场景：HUMAN / CREATURE / ARCHITECTURE / WATER / ATMOSPHERE / ENTITY / TEXTURE_LOCK / MIXED
- 情绪：压迫 / 宏大 / 唯美 / 宁静 / 神秘 / 紧张
- 平台：Kling / Veo / Runway / Hailuo / 即梦

生成稳定参数起点。

Preset 合并优先级：

`Structural Lock > Risk > Scene > Duration > Aspect > Mood > Platform`

关键约束：
- HIGH risk：camera_strength <= 0.30
- MEDIUM risk：camera_strength <= 0.55
- LOW risk：camera_strength <= 0.75
- 复杂文字 / 书法：lighting_variation <= 0.10
- 建筑主体：motion budget = 0
- 巨型灵体：limb_action_complexity <= 0.20
- 巨型凤凰 3 秒：wingbeat_count <= 1

## V7 Adaptive Shot Planner

同一 Director IR 生成最多三档候选：

- `SAFE`：最高稳定性，适合 HIGH RISK
- `BALANCED`：稳定性与电影感平衡
- `EXPRESSIVE`：仅 LOW RISK 且结构简单时启用

默认推荐候选 Stability Score 必须 >=80 且无 Hard Reject。

## V6 Quality Gate

每个平台 Prompt 第一次生成后只视为 `DRAFT`。

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
- 先套稳定参数，再选候选镜头。
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

尤其适合：东方玄幻 / 仙侠、古建筑与历史场景、巨型生物 / 凤凰 / 仙鹤、云海 / 瀑布 / 水汽、人物凝视 / 极小动作、巨型灵体 / 能量体、复杂前中后景电影构图、同一镜头多平台提示词转换。