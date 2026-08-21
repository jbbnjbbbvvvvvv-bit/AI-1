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

## 当前版本

**V5 — Platform-Specific Prompt Compilers**

当前流程：

`原图拉片 → 场景分类 → Structural Lock → 风险评分 → 主运动选择 → Camera Decision Tree → Motion Budget → Wind Field → Causal Motion Graph → Auto Degrade → Director IR → Platform Router → Kling / Veo / Runway / Hailuo / 即梦 Compiler → Quality Check`

## 目录

- `SKILL.md`：核心 Skill，包含任务目标、输入、工作流、输出格式、质量检查。
- `references/director-rules.md`：专项导演规则库。
- `references/prompt-compiler.md`：V3 通用 Prompt Compiler。
- `references/auto-director-decision-tree.md`：V4 自动导演决策树。
- `references/platform-compilers.md`：V5 平台专用编译器与 Platform Router。
- `examples/golden-examples.md`：标准测试案例，用于检查 Skill 是否跑偏。
- `examples/compiler-examples.md`：导演分析 → IR → 平台 Prompt 的编译案例。
- `tests/evaluation-checklist.md`：40 分质量评估与 Hard Fail 检查。

## 推荐输入格式

```text
原图：上传图片
时长：3秒
画幅：16:9
主运动对象：人物 / 动物 / 水 / 云 / 建筑 / 灵体
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
9. Director IR
10. 正式平台提示词
11. 极简版提示词
12. 负面提示词
13. Quality Check

## V5 平台路由

- Kling / 可灵 → `KLING Compiler`
- Veo → `VEO Compiler`
- Runway → `RUNWAY Compiler`
- Hailuo / 海螺 → `HAILUO Compiler`
- 即梦 → `JIMENG Compiler`
- 未指定平台 → `PLATFORM_NEUTRAL`

多平台模式只进行一次导演分析和一次 IR 生成，再分别编译，保证不同平台版本共享同一主运动、摄影机和结构锁定逻辑。

## 核心原则

- 先锁结构，再动镜头。
- 先定主角，再分运动。
- 建筑不动，环境回应。
- 人物越小，动作越少。
- 巨物越大，动作越慢。
- 形可以不动，质可以流动。
- 平台表达可以变化，导演决策不能变化。
- 不是让所有东西动，而是让观众相信整个世界正在运行。

## 适用场景

尤其适合：

- 东方玄幻 / 仙侠
- 古建筑与历史场景
- 巨型生物 / 凤凰 / 仙鹤
- 云海 / 瀑布 / 水汽
- 人物凝视 / 极小动作
- 巨型灵体 / 能量体
- 复杂前中后景电影构图
- 同一镜头多平台提示词转换

## 不推荐的做法

- 3秒镜头安排多个复杂动作
- 所有元素同时明显运动
- 单张图大幅环绕
- 建筑主体参与形变
- 复杂书法 / 纹理区域大幅摆动
- 巨型鸟类高频扇翅
- 巨型灵体大幅人体动作
- 为不同平台重新设计不同剧情或不同主动作

## 使用建议

当输出存在以下情况时，应自动简化：

- 多个主运动争夺注意力
- 摄影机运动过多
- 隐藏面推断过大
- 风向不一致
- 建筑参与形变
- 负面约束过于泛化
- 平台版本之间主运动不一致

如命中 3 项以上，应重新生成更克制版本。