# 已验证经验

仅列 VERIFIED。每条须有具体证据、验证范围和规则落点；候选与失败方法见 [pending-lessons.md](pending-lessons.md)。既有技术证据见 [validation.md](validation.md)。

## n03-shared-resource-protection · VERIFIED
- 日期：2026-11-18
- 任务类型：既有经验入库
- 问题：仅比较模型实体不足以证明原图显示保持不变
- 原因：共用文字、线型和尺寸样式可影响未改动的实体
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：保护快照同时比较 STYLE、LTYPE、DIMSTYLE 及被引用块和图层
- 验证：三案例回读与共用样式变动内存反例均已验证；外部字体和打印驱动仍需另核
- 更新文件：references/quality-audit.md、scripts/cad_checks.py

## n03-integrated-block-protection · VERIFIED
- 日期：2026-11-18
- 任务类型：既有经验入库
- 问题：安装一组构件时必须证明已完成组保持原状
- 原因：仅看新增组截图不能排除其他块定义被改动
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：对原实体、现有 INSERT 变换及块定义执行差分
- 验证：P1、P2 集成阶段的原组块定义改动反例被拒绝，原文件回读保护通过
- 更新文件：references/dxf-transfer.md、references/quality-audit.md

## n03-outline-collision-check · VERIFIED
- 日期：2026-11-18
- 任务类型：既有经验入库
- 问题：包络适配不能直接认定局部花饰安装无冲突
- 原因：真实连接框和过渡轮廓与外包框不是同一几何
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：等比安装后对真实轮廓、交接及相关句柄逐项检验，未排除冲突保持预演状态
- 验证：原预演报告存在连接冲突；本条只验证审核门禁，不声称最终移植已通过
- 更新文件：references/dxf-transfer.md

## n03-actual-viewport-context · VERIFIED
- 日期：2026-11-18
- 任务类型：既有经验入库
- 问题：模型可见不等于实际布局视口可见
- 原因：嵌套块及视口冻结上下文会改变出图记录
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：使用实际视口上下文核验嵌套构件、冻结层、来源前缀和投影关系
- 验证：三组现有案例及 P1 两种纹理显示状态已回读，视口投影误差记录为零
- 更新文件：references/quality-audit.md、references/transfer-layout.md

## lesson-transaction-safeguards · VERIFIED
- 日期：2026-11-18
- 任务类型：自动维护机制验证
- 问题：自动沉淀可能将未验证尝试写入规则或重复追加
- 原因：缺少状态门禁、稳定索引和写前验证会传播无证据经验
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：分级隔离、语义审查加机械去重、范围白名单、临时验证、互斥与失败回滚
- 验证：24 项隔离夹具测试通过；候选不能改规则，重复不写文件，故障后恢复原字节；证据真假和语义冲突仍须 Codex 审阅
- 更新文件：references/learning-protocol.md、scripts/maintain_lessons.py、tests/test_maintain_lessons.py

## windows-utf8-skill-validation · VERIFIED
- 日期：2026-11-18
- 任务类型：自动维护机制验证
- 问题：Windows 中文 Skill 在官方格式验证器读取时发生解码失败
- 原因：官方验证器默认 read_text 受系统本地编码影响
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：用当前解释器以 -X utf8 启动验证子进程，不改官方验证器或系统全局编码
- 验证：中文夹具读取测试和官方 quick_validate 均已通过
- 更新文件：references/quality-audit.md

## warm-planar-boundary-width-tracing · VERIFIED
- 日期：2026-11-18
- 任务类型：彩色平面纹样转线稿及 DXF
- 问题：彩色平面纹样需要保留框料宽度、裁切边界和小闭环，普通分类阈值/简化器会改变几何
- 原因：Otsu 分类阈值并非连续边缘中点；简化器可能折叠微小闭合孔
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：材料/背景代表值中点定位、内外轮廓完整提取、局部拟合、闭环回退及原生 DXF 回读；范围仅限已验证的暖色平面输入
- 验证：本例 720 条等值轮廓全部进入 DXF；零重复、零结构错误，最大拟合偏差约 0.592 像素；11 项测试含多亮度与已知 3/6/12 像素宽度通过。未验证真实照片的单应校正。
- 更新文件：SKILL.md、references/lineart-cleaning.md、references/scripts.md、scripts/trace_coloured_ornament_panels.py、tests/test_trace_coloured_ornament_panels.py

## generated-cleanup-geometry-gate · VERIFIED
- 日期：2026-11-18
- 任务类型：彩色平面纹样转线稿及 DXF
- 问题：视觉整洁的生成式净化候选可能增加孔洞、补齐边框或改动纹样
- 原因：生成结果外观规整不等于与来源有同一几何
- 证据：验证范围见 references/validation.md；原项目文件未公开，合成测试见 tests。
- 方法：先对原图叠加及检查构件来源，发生新增或改纹的候选不得作为 CAD 几何母版；沿用已有来源保护规则
- 验证：本次候选可见新增/改纹，单向线距 P95=3 像素、最大约 16.64 像素，已拒绝；正式 DXF 直接读取原图证据。该结论不否定所有图像编辑。
- 更新文件：references/motif-preservation.md、references/quality-audit.md
