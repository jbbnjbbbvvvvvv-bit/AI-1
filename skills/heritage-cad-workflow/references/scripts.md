# 脚本与验证边界

## 彩色平面纹样

[../scripts/trace_coloured_ornament_panels.py](../scripts/trace_coloured_ornament_panels.py) 支持可分离的暖色材料、浅中性色背景、近正视平面纹样。按用户核对后的区域提取材料内外轮廓，保留裁切开放边界和小闭环，用直段/原生圆弧 bulge 拟合并回读 DXF。未知物理比例为 INSUNITS=0。不会自动将任意照片正射化。

```bash
python -X utf8 -B scripts/trace_coloured_ornament_panels.py --input ornament.png --config assets/panel-config-example.json --output new_results
```

配置 rows、columns、curve_panels、阈值和容差属于当前图像参数，不能直接沿用示例像素范围。正式输出已存在时拒绝覆盖。依赖见 [../requirements.txt](../requirements.txt)。`--vendor` 可重复追加已有库目录，优先保留解释器兼容的已安装依赖。测试见 [../tests/test_trace_coloured_ornament_panels.py](../tests/test_trace_coloured_ornament_panels.py)；如使用已有 vendor，在测试进程临时设置 `HERITAGE_CAD_VENDOR_PATHS`（按操作系统路径分隔符分隔），不写全局配置。

## DXF 只读检查

[../scripts/cad_checks.py](../scripts/cad_checks.py) 支持 inspect 和 verify。inspect 按类型/图层统计原生实体、相同定义、可选主体图层包络及视口；不保存 CAD。

```bash
python -X utf8 -B scripts/cad_checks.py inspect input.dxf --body-layer A-ARCH
python -X utf8 -B scripts/cad_checks.py verify assets/transfer-check-example.json --project-root your_case_directory
```

verify 比较复制到块中的原生定义、INSERT 等比和逆变换，支持 LINE、LWPOLYLINE、SPLINE、CIRCLE、ARC；未支持实体停止对应检查。嵌套块按既有名字和定义保留处理，重命名映射需另验。比较样式表、原模型/块/图层/布局，检查实际视口投影与冻结上下文。

相同定义检测包括样式，不等于几何逆序或局部共线判定。部分重叠、短线语义、自交、曲线连续性和纹样识别不能据此自动通过。视口检验限单个活动俯视视口且完整包含对象；多视口、透视与局部裁切需专门核验。

[../scripts/validate_cases.py](../scripts/validate_cases.py) 读取使用者提供的 source/before/after 配置，对适用案例构造内存中的比例、缺复制、原证据线、已有块和共用样式反例，不保存 CAD。该案例测试入口要求相应原生块/图层及原 LWPOLYLINE 等前提；不适用的真实案例需要调整，不能把示例配置的占位文件当成已验证输入。输出 JSON 默认终端，报告显式另存，已有报告拒绝覆盖。

## 自动经验维护

[../scripts/maintain_lessons.py](../scripts/maintain_lessons.py) 为标准库事务入口：默认预演，仅 `--commit` 写当前授权 Skill。细则见 [learning-protocol.md](learning-protocol.md)，测试见 [../tests/test_maintain_lessons.py](../tests/test_maintain_lessons.py)。机械门禁不能证明自然语言证据真实，也不能替代代码内容审查。公开包不含原项目绘图生成器；新建筑按实际输入选择工具，不声称完全自动重建。
