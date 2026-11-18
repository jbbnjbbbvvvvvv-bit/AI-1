---
name: heritage-cad-workflow
description: 历史建筑线稿分区净化、彩色平面纹样提取、门窗花格与雕花保形重建、DXF 构件移植及模型布局核验。适用于窑洞等建筑立面，支持既有 CAD 优先复用、保护破损现状和原始证据。任务范围由当次请求决定。
---

# 历史建筑线稿净化与 CAD 构件重建

先确定当前任务的输入身份、证据状态、保护对象和交付范围，再选择所需模块。仅请求审计时只读检查；已要求生成或修改成果时直接执行范围内工作，另存新文件。默认读取用户指定项目及相关资料。

## 选择流程

| 任务 | 应读参考与操作 |
| --- | --- |
| 彩色平面纹样转线稿/DXF | [references/lineart-cleaning.md](references/lineart-cleaning.md) 中已验证的暖色纹样范围；使用 [references/scripts.md](references/scripts.md) 中的提取入口。真实斜拍和强阴影需另验。 |
| 线稿净化、CAD 碎线清理 | [references/lineart-cleaning.md](references/lineart-cleaning.md)。先分区保护，再判断重线、共线和疑似短线。 |
| 建筑几何规范化与装饰保形 | [references/geometry-constraints.md](references/geometry-constraints.md)、[references/motif-preservation.md](references/motif-preservation.md)。按原图和本次授权处理。 |
| DXF 构件移植、多组立面集成、局部花饰替换 | [references/dxf-transfer.md](references/dxf-transfer.md)。核对源实体、目标开口与保护范围，等比安装。 |
| 模型、布局及几何核验 | [references/quality-audit.md](references/quality-audit.md)、[references/transfer-layout.md](references/transfer-layout.md)。检查实际实体、变换和视口。 |
| 参考匿名案例及失败类型 | [references/n03-cases.md](references/n03-cases.md)。案例数值只描述对应文件。 |
| 运行只读脚本、选择原项目工具 | [references/scripts.md](references/scripts.md)。读取依赖和验证范围后再调用。 |

## 开始时记录

记录对象编号、源文件和目标文件的完整路径及哈希、原图像素尺寸、DXF 单位、保护图层或句柄、实际几何范围、证据状态、授权阶段和输出格式。文件名相近或带下载后缀时先核验身份。未知单位使用图样坐标；原图映射采用统一比例及明确的 Y 轴方向。以当次资料量取参数。

## 必须守住的构件关系

- 保留框料的两条实体边界、横档和竖梃的真实连接。根据原图分别判断规则构件、装饰曲线、现状破损和辅助纹理。
- 花芯、卷草、心形空隙、连续菱形等先设保护区。短线按构件与连接归属判断，单凭长度不足以删除。
- 有证据的重复单元才采用 BLOCK。镜像和对称约束须符合原图或用户明确的方案；保留各侧可辨差异。
- 复用已有有效曲线和块定义；移植时保持实体类型和构件内部相对位置。源主体包络与墙地纹理包络分别计算。
- 模型与布局共用模型几何；通过视口设置表达可见性差异。所有非目标构件、原核对线、尺寸和不确定性注记均纳入保护检查。
- 图像转绘、类型参考、推断补配、实测资料分别标注证据状态。几何一致性误差只说明 CAD 处理，不用于宣称实物尺寸或绝对配准精度。

## 输出和验收

根据当前请求交付可编辑 DXF、净化线稿、CAD 回读预览、同尺度叠加、关键细节图与审计。使用 [assets/audit-template.md](assets/audit-template.md) 中相关项目，填入实际读数和未核事项。只读阶段可将脚本结果输出到终端；报告落盘需要处于用户授权范围。

[scripts/cad_checks.py](scripts/cad_checks.py) 支持只读结构检查、参数化移植逆变换检查、原图保护检查和实际视口检查。它覆盖的实体类型及不覆盖的拓扑检查见脚本参考，其他检查不能据此自动判为通过。

## 与现有技能配合

如已安装，`cad-operations` 处理通用 CAD 环境、格式转换和交付验证；平面墙基线、墙厚及门窗开口重建任务可调用 `floorplan-to-vector`。以当前技能目录发现结果定位这两项技能，按需读取，避免将平面图墙体算法直接用于立面雕花。优先复用项目中已经验证的能力；本技能包含独立只读核验入口，绘制脚本按案例参考使用。

## 自动经验沉淀

项目所有者明确授权自动维护后，相关任务成果验证后、最终回复前，按 [references/learning-protocol.md](references/learning-protocol.md) 执行一次经验检查，无需用户另发更新指令。新项目不能继承其他用户或来源项目的维护授权；未授权时只检查和提出建议。无新增不写文件；候选/失败经验隔离记录，仅经证据验证且无规则冲突的经验进入正式指导。先读旧规则去重，更新后验证并在失败时回滚。维护只限当前用户授权的项目中本 Skill，不能改动已完成 CAD。收尾反馈一行实际状态；学习维护本身不递归触发学习。
