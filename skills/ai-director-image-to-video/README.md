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

## 当前版本

**V6 — Quality Scoring & Self-Repair Engine**

当前流程：

`原图拉片 → 场景分类 → Structural Lock → 风险评分 → 主运动选择 → Camera Decision Tree → Motion Budget → Wind Field → Causal Motion Graph → Auto Degrade → Director IR → Platform Router → Platform Compiler → 40分评分 → Hard Fail → Diagnose → Repair → Recompile → Rescore → Release`

## 目录

- `SKILL.md`：核心 Skill。
- `references/director-rules.md`：专项导演规则库。
- `references/prompt-compiler.md`：V3 通用 Prompt Compiler。
- `references/auto-director-decision-tree.md`：V4 自动导演决策树。
- `references/platform-compilers.md`：V5 平台专用编译器与 Platform Router。
- `references/self-repairer.md`：V6 自动评分、诊断、自我修复与安全降级。
- `examples/golden-examples.md`：标准测试案例。
- `examples/compiler-examples.md`：导演分析 → IR → 平台 Prompt 编译案例。
- `tests/evaluation-checklist.md`：V6 40分质量评估、Hard Fail 与修复循环。

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
4. 运动预算
5. 镜头设计
6. 主体运动设计
7. 环境因果
8. 时间轴
9. Director IR（默认可隐藏）
10. 正式平台提示词
11. 极简版提示词
12. 负面提示词
13. Quality Score / Grade
14. 是否触发修复
15. Release Status

## V5 平台路由

- Kling / 可灵 → `KLING Compiler`
- Veo → `VEO Compiler`
- Runway → `RUNWAY Compiler`
- Hailuo / 海螺 → `HAILUO Compiler`
- 即梦 → `JIMENG Compiler`
- 未指定平台 → `PLATFORM_NEUTRAL`

多平台模式只进行一次导演分析和一次 IR 生成，再分别编译，保证不同平台版本共享同一主运动、摄影机和结构锁定逻辑。

## V6 Quality Gate

每个平台 Prompt 第一次生成后只视为 `DRAFT`，不能直接发布。

必须执行：

`SCORE → HARD_FAIL_CHECK → DIAGNOSE → REPAIR → RECOMPILE → RESCORE`

最多自动修复 3 轮。

### 分数
- 36–40：`PRODUCTION_READY`
- 31–35：`GOOD`
- 25–30：继续修复
- 0–24：强制重构

### Hard Fail
以下问题一票否决：建筑主体变形、3秒多个复杂主动作、文字大幅形变、人物身份/数量未锁定、巨型鸟高频扑翼、复杂单图大幅环绕、风向冲突、无定制负面约束、平台版改变 Director IR、明显时间跳变等。

### 第3轮仍不合格
自动执行 `Maximum Safe Degrade`：

- Static / very slow push-in
- 1 个 Primary Motion
- <=1 Secondary Motion
- <=1 Ambient Motion
- Lighting locked
- No orbit
- No hidden geometry expansion
- No new objects

目标从“最炫”切换为“最稳”。

## 核心原则

- 先锁结构，再动镜头。
- 先做风险控制，再做电影化。
- 先定主角，再分运动。
- 建筑不动，环境回应。
- 人物越小，动作越少。
- 巨物越大，动作越慢。
- 形可以不动，质可以流动。
- 平台表达可以变化，导演决策不能变化。
- 第一次 Prompt 只是 Draft，不是成品。
- 不是让所有东西动，而是让观众相信整个世界正在运行。

## 适用场景

尤其适合：东方玄幻 / 仙侠、古建筑与历史场景、巨型生物 / 凤凰 / 仙鹤、云海 / 瀑布 / 水汽、人物凝视 / 极小动作、巨型灵体 / 能量体、复杂前中后景电影构图、同一镜头多平台提示词转换。
