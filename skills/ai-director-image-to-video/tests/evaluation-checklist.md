# AI Director Skill Evaluation Checklist V6

## Scoring
每项 0 / 1 / 2 分：

- 0 = 未满足或明显错误
- 1 = 部分满足
- 2 = 完全满足

总分 40 分。

## A. 原图理解
1. 是否正确识别前景、中景、远景？
2. 是否正确识别视觉锚点？
3. 是否找到合理尺度参照？
4. 是否识别文字、建筑、人物、复杂纹理等高风险区域？

## B. 结构稳定
5. 是否明确锁定建筑与地形？
6. 是否保护人物身份、比例、服装和数量？
7. 是否保护书法、文字、壁画和纹样？
8. 是否避免无必要隐藏面推断？

## C. 镜头
9. 是否只有一个主镜头运动？
10. 镜头运动是否与情绪匹配？
11. 是否避免快速推拉、剧烈旋转和无必要环绕？
12. 摄影机运动是否有利于空间层次而非炫技？

## D. 主体运动
13. 是否存在清晰的一级主体？
14. 是否最多只有两个明显运动主体？
15. 动作是否包含方向、速度、幅度、节奏和惯性？
16. 动作幅度是否与主体在画面中的尺寸匹配？

## E. 物理因果
17. 二级运动是否由一级运动触发？
18. 风场是否统一？
19. 水、云、羽毛、布料是否符合基本物理？
20. 环境是否保持辅助地位？

## 判定
- 36–40：A / Production Ready
- 31–35：B / Good
- 25–30：C / Risky
- 0–24：D / Reject

发布阈值：`score >= 31` 且无 Hard Fail。
目标阈值：`score >= 36` 且无 Hard Fail。

## Hard Fail 一票否决
出现任一项时，即使总分较高也不得发布：

- 明确要求建筑主体移动或变形
- 3秒内安排多个复杂主动作
- 书法/文字区域大幅形变
- 人物身份或数量未锁定
- 巨型鸟类高频扑翼
- 大幅环绕复杂单张图
- 多个互相冲突的风向
- 没有针对当前图像的负面约束
- 以大量风格词替代真实运动设计
- 平台编译器改变 Director IR 的主动作或镜头风险判断
- 透明巨型灵体执行高风险大幅人体动作且未降级
- 最后一帧突然停止或新增动作

## V6 自动修复循环
候选 Prompt 不直接发布，执行：

`Score → Hard Fail → Diagnose → Repair → Recompile → Rescore`

最多 3 轮。

### 修复优先级
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

### 低于31分时
1. 删除一个明显运动主体。
2. 将镜头改为 Static 或 Slow Push-In。
3. 环境运动降低50%。
4. 建筑与文字强制锁定。
5. 只保留一个主要物理因果链。
6. 重新生成负面约束。
7. 重新编译并评分。

### 第3轮仍失败
执行 Maximum Safe Degrade：

- Camera = Static 或 very slow push-in
- Primary Motion = 1
- Secondary Motion <= 1
- Ambient Motion <= 1
- Lighting locked
- No orbit
- No hidden geometry expansion
- No new objects

最终状态：`PRODUCTION_READY / GOOD / SAFE_FALLBACK / REJECT`。

详细规则见：`references/self-repairer.md`。