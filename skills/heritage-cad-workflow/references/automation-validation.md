# 自动维护验证与触发

经验维护为项目指令流程，不是后台学习服务。项目所有者授权后，在相关任务成果验证后、最终回复前执行一次检查。普通重复操作不写文件；维护及其回滚不递归触发维护。

本公开版没有注册生命周期 Hook，也不修改全局配置。官方 Hook 与 AGENTS 加载机制可参考 [Hooks](https://learn.chatgpt.com/docs/hooks) 和 [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。客户端版本与信任状态应在实际部署时检查，不能因为文档支持某事件就声称当前会话已启用。

自动维护门禁有合成事务测试支撑，语义去重、证据真实性和规则冲突仍需执行任务的 Codex 判断。修改后运行 [验证流程](validation.md)，失败回滚并记录原因。来源项目的自动维护授权不转移给新安装者。
