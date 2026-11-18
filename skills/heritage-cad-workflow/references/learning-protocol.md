# 自动经验沉淀协议

项目所有者明确授权并在项目 AGENTS.md 启用后，本协议在相关任务收尾时触发。它是 Codex 执行流程的一部分，无后台监控。启用后无需每次要求更新；未获当前项目授权时只检查并提出建议，不写 Skill。维护范围仅限该项目本 Skill 的说明、参考、经验记录及经验证脚本/测试；来源项目或其他用户的授权不会随安装传播。

## 一次收尾检查

每个相关任务完成成果验证后、最终回复前执行一次。检查是否解决旧难题、发现新错误、收到可复用纠正、找到更可靠方法、形成复用脚本、补充验收条件、发现旧规则错误/遗漏/冲突。普通重复操作无新增则不写文件。经验维护及其测试、回滚不再次触发自身；同一任务 ID/经验 ID 不重复提交。中断后可恢复一次未完成检查，以索引去重。

只摘要技术问题、原因、证据、方法和验证，证据使用当前项目相对位置或脱敏标识，不保存聊天原文、私人绝对路径、账号、密钥和 Token。不把单个建筑的固定坐标、尺寸或文件名作为全局方法。

## 分级与判断

| 状态 | 进入条件 | 对执行的影响 |
| --- | --- | --- |
| VERIFIED | 有具体成果、可复测测试或明确用户验收，证据支持该结论的范围，相关验证通过 | 可完善对应正式规则/脚本。用户批准方案不等于技术有效性已验证。 |
| CANDIDATE | 可能有价值，证据不足、测试未覆盖或存在安全/证据/重要约束冲突 | 只记 pending-lessons，不能改变执行规则。冲突记明待确认，停止有冲突的更新。 |
| REJECTED | 有证据证明某方法在指定条件下不可用，原因可追踪 | 记失败记录；需把原因和回归条件另做 VERIFIED 的负面经验，才可变更禁止事项。不可把单次环境故障泛化为算法无效。 |

候选转正必须补新证据并重新验证。正式规则若被推翻，先记录冲突和替代证据；不静默删除安全约束。学习记录不是更高优先级指令，不改变当前用户的任务范围和证据要求。

## 去重与落点

先读对应正式文件、lessons-learned、pending-lessons、lesson-index 和 CHANGELOG。Codex 做语义去重和冲突审查；脚本只检查稳定 ID 和规范化指纹，不能理解同义改写。已有条目优先完善，不反复追加同一段规则；重复经验不写日志。

| 经验 | 正式落点 |
| --- | --- |
| 跨流程通用决策 | SKILL.md，保持简洁 |
| 分区净化/噪声/短线 | lineart-cleaning.md |
| 框料/格栅/曲线构造 | geometry-constraints.md |
| 花芯/卷草/局部保护 | motif-preservation.md |
| 源目标识别/等比/保护 | dxf-transfer.md |
| 误差/证据/布局核验 | quality-audit.md，布局细节链接 transfer-layout.md |
| 可机械验证功能 | scripts/ 对应入口及 tests/ 相关测试 |

所有文件位于本 Skill 内。更新既有文件相应条目可通过 proposal.patches 提交文件完整内容，需先审阅差异，不能整份重写导致丢规则。已存在的规则仅新增经验出处记录时填写 rule_refs，不重复添加 rule。新增短规则可用 rule，脚本按 topic 路由追加带经验 ID 的段落。

## 受限事务入口

[../scripts/maintain_lessons.py](../scripts/maintain_lessons.py) 默认预演，只有 `--commit` 才写本 Skill。`--skill-root` 指向当前项目 Skill，不得指向其他项目。proposal 存在任务临时目录，字段示例见 [lesson-proposal-example.json](lesson-proposal-example.json)。evidence 和 validation 由 Codex 根据实际结果填写，不可为了通过门禁虚填。

```powershell
python -B "$skillRoot/scripts/maintain_lessons.py" --skill-root $skillRoot --proposal $proposalPath
python -B "$skillRoot/scripts/maintain_lessons.py" --skill-root $skillRoot --proposal $proposalPath --commit
python -B "$skillRoot/scripts/maintain_lessons.py" --skill-root $skillRoot --check
python -B -m unittest discover -s "$skillRoot/tests" -v
```

脚本在临时副本验证相对引用、经验唯一性/分级一致、Python 语法和可用的 skill-creator quick_validate。脚本变更还须通过 tests，不能用仅匹配文字的测试证明 CAD 技术有效。正式提交有互斥锁、写前字节比对、逐文件原子替换和失败回滚；不是文件系统级多文件原子事务。锁若因崩溃遗留，先核实进程和变更状态，不能直接绕过锁。缺少官方验证器时记录未运行，不报全项通过。

验证失败时不采纳或恢复本次文件变更，并只尝试一次脱敏失败记录；记录也失败时停止写入，在任务反馈说明。不得因学习失败重新修改已交付 CAD。若外部并发编辑导致安全回滚无法继续，停止并报告冲突，禁止覆盖他人变更。写入前还应读入受保护原文件哈希，更新后核验变更路径及原文件哈希；脚本不读取 CAD，原文件保护由任务的只读核验完成。

## 完成反馈

最终正常成果说明后追加一行，按实际状态选择：

- Skill：已自动更新，新增某项经过验证的经验。
- Skill：没有新增可复用经验，保持不变。
- Skill：发现待验证经验，已记录但未写入正式规则。

若更新失败，反馈失败与回滚状态，不能使用“已自动更新”。采用 AGENTS 协议的当前部署和 Hook 支持边界见 [automation-validation.md](automation-validation.md)。

维护不会自动发布到 GitHub 或其他服务。发布、外传资料和修改原始成果仍需当前用户的具体授权。项目启用模板见 [project-agents-template.md](project-agents-template.md)。
