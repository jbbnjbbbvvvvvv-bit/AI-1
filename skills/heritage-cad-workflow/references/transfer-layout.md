# 模型与布局一致性

构件选择和安装见 [dxf-transfer.md](dxf-transfer.md)。

## Model 与实际视口

确认纸空间用 VIEWPORT 显示同一 Model 几何。检查 view direction、target、twist、view height、paper dimensions、视口比例、视口冻结及图层覆盖。图层全局开关和视口冻结分别核验。多视口按各自裁切域比较，不能假设全部模型都应出现在每个视口。

两种显示状态可用同一模型配不同视口冻结层，不复制第二套建筑。完整检查应比较 Model 绘图记录经视口变换后的控制坐标与布局真实回读记录，并查看正式渲染。检查颜色、线宽、打印样式及精度设置，不能以空样式表声称黑白打印已验证。

本项目 ezdxf 视口回调曾对嵌套 INSERT 使用全局 RenderContext，导致冻结纹理仍被绘制。`cad_checks.py` 中的 `ViewportFrontend` 将当前视口上下文传给嵌套块，并检查实际冻结结果。遇不同库版本先复测。Core Console 配置加载失败只记录为环境限制，不能记作 AutoCAD AUDIT 通过。
