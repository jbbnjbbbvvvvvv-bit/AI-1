# heritage-cad-workflow

**历史建筑线稿净化与 CAD 构件重建**

A reusable Codex Skill for evidence-preserving architectural linework, ornamental boundary tracing, editable DXF transfer, and geometric auditing.

适用于历史建筑立面、门窗花格和雕花。按任务选择流程：分区净化、框料双边界保护、纹样保形、已有 CAD 几何复用、等比例块移植、非目标区域保护及 Model/布局检查。

## 能做什么

- 对可分离的暖色平面纹样提取内外轮廓，输出黑白线稿与原生可编辑 DXF。
- 保存材料宽度、小闭环和有意义短线，保留裁切造成的开放边界。
- 复用 LINE、LWPOLYLINE、圆弧 bulge、SPLINE、CIRCLE 和已有块，避免重新描绘完成的 CAD。
- 检查 DXF 结构、复制/逆变换一致性、原实体与样式保护，以及实际视口记录。
- 经项目所有者授权后，以 VERIFIED / CANDIDATE / REJECTED 隔离经验，进行去重、验证和失败回滚。

## 已知范围

暖色纹样提取脚本已用合成几何测试与近正视拼图验证。它不等于任意照片的完整正射重建器。真实斜拍、镜头畸变、强阴影、遮挡后构造与实物比例需要另行验证。没有实测基准时使用图样坐标，不宣称毫米尺寸、历史形制或绝对配准精度。

公开包不包含原始照片、项目 CAD、精确场地坐标、私人路径、输入文件哈希清单或完整聊天记录。匿名案例只保留方法与失败类型。

## 安装

将当前目录完整复制到项目 `.agents/skills/heritage-cad-workflow/`，或安装到你自己选择的 Codex Skill 目录。保留 references、scripts、tests、assets 和 agents 结构。

本目录的公开地址：

https://github.com/jbbnjbbbvvvvvv-bit/AI-1/tree/main/skills/heritage-cad-workflow

## 使用示例

```text
使用 $heritage-cad-workflow，将这张雕花图转换为正视二维线稿和可编辑 DXF。
保留纹样、材料双边界和已有宽度；不补造遮挡或裁切部分。
输出回读预览、原图叠加与质量报告。没有可靠尺寸时使用图样坐标。
```

```text
使用 $heritage-cad-workflow，将 source.dxf 中的原生构件等比移植到 target.dxf 的指定开口。
先识别单位、源主体包络、目标中轴与基准；保护其他块、尺寸和布局。
另存新文件，并执行逆变换及非目标区域保护核验。
```

## Python 依赖与测试

建议使用隔离 Python 环境。脚本不需要 OpenAI API Key。

```bash
python -m pip install -r requirements.txt
python -X utf8 -B -m unittest discover -s tests -v
python -X utf8 -B scripts/maintain_lessons.py --check
```

发布版包含 35 项合成/事务测试。测试使用临时文件，不修改你的生产 CAD。原项目的真实 CAD 案例未公开，不应把合成测试等同于所有真实图纸验收。详见 [验证范围](references/validation.md)。

暖色纹样的运行示例：

```bash
python -X utf8 -B scripts/trace_coloured_ornament_panels.py --input ornament.png --config assets/panel-config-example.json --output new_results
```

示例配置中的图幅范围仅是参数格式示例，需要按你的输入实际像素尺寸与分区修改。已有正式输出不会被覆盖。

DXF 只读检查：

```bash
python -X utf8 -B scripts/cad_checks.py inspect drawing.dxf --body-layer A-ARCH
```

## 自动经验维护

自动维护需要当前项目所有者明确授权。可参考 [项目收尾协议模板](references/project-agents-template.md) 后追加到自己的 AGENTS.md。来源项目的授权不会随安装传播。经验维护只作用于当前 Skill，不自动修改 CAD，也不自动推送 GitHub。

## 发布与许可

本版本是公开分享包；未替作者新增独立开源许可证。所依赖第三方库遵循各自许可。公开可访问不构成对项目素材或未公开成果的再分发授权。
