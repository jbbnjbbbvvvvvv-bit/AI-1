# Prompt Compiler Examples

## Example 01 — 凤凰 / 云上宫殿 / 3秒 / Kling

### Director IR
- Risk: HIGH
- Locked: 古建筑屋顶、人物位置与比例、凤凰数量、原构图、云层空间关系
- Primary: 凤凰
- Action: 一次有重量的翼下压后进入滑翔
- Camera: 极慢推进
- Response: 尾羽延迟跟随；翼下薄云轻微卷动
- Ambient: 远云低频漂移

### Compiled Prompt
基于原始图片进行3秒图转视频。严格保持古建筑屋顶、人物、凤凰数量、原始构图、比例、透视和空间关系完全稳定，不重构建筑，不改变人物身份，不新增任何主体。

凤凰是唯一明显主运动对象。它以缓慢、有重量的节奏完成一次完整翼下压，随后自然进入短暂滑翔；翼根稳定，外侧飞羽略有延迟弯曲，长尾羽在主体动作之后以柔和惯性跟随，不高频扇翅。

摄影机只做极慢、极小幅度向前推进，保持原有低角度宏大构图，不环绕，不快速改变视角。凤凰翼下压产生轻微空气扰动，仅使邻近薄云局部缓慢卷动；远处云层维持低频连续漂移。所有飘带、羽毛和薄云遵循一致风向。

锁定原始阳光方向、色温和曝光，只允许羽毛表面产生连续细微高光变化。真实摄影质感，真实空气透视，巨大生物重量感，电影级自然运动模糊，时间连续。

负面：extra wings, missing wings, wing deformation, feather melting, phoenix duplication, architectural deformation, roof distortion, character deformation, camera shake, rapid zoom, orbit, flickering, frame jumping, geometry drift, new objects。

### Minimal
锁定建筑、人物、凤凰数量与原构图。凤凰仅完成一次缓慢有重量的翼下压并短暂滑翔，尾羽延迟跟随；镜头极慢推进，邻近薄云只产生轻微翼压响应。禁止多翼、羽毛融化、建筑变形、环绕、抖动、闪烁和新增主体。

---

## Example 02 — 人物 / 巨型书法幕 / 古建筑 / 3秒 / Kling

### Director IR
- Risk: HIGH
- Locked: 书法内容、幕布形态、建筑、人物身份
- Primary: 人物
- Action: 呼吸 + 极轻微抬头
- Camera: slow push-in
- Response: 发丝和衣带同风向微动
- Ambient: 云层极慢移动

### Compiled Prompt
基于原始图片进行3秒图转视频。严格保持古建筑、巨大书法幕、原始书法笔画、人物身份、服饰、比例、位置、透视和构图不变。不得重新生成、改写或扭曲任何书法文字和建筑纹样。

人物是唯一一级运动主体，保持站立姿态，只出现自然呼吸，并在中段极轻微抬头凝视前方；不迈步、不转身、不做复杂手势。发丝、衣带受到同一高空微风影响产生极小幅度连续摆动。

摄影机做非常缓慢的小幅推进，通过原有前中后景产生轻微视差；不环绕，不横移到需要生成大量隐藏面的角度。巨大书法幕宏观形态保持固定，不做大幅布料摆动；远处云层只做低频缓慢漂移。

保持原始光线方向、曝光与色温。真实摄影、自然空气透视、宏大尺度、安静压迫感、连续时间一致性。

负面：calligraphy rewrite, text mutation, texture crawling, architectural deformation, roof warping, face deformation, identity change, extra limbs, walking, sudden turn, camera shake, orbit, rapid zoom, flicker, object drift, new characters。

---

## Example 03 — 巨型水灵体 / 宫殿 / 人物 / 3秒 / Kling

### Director IR
- Risk: HIGH
- Primary: 水灵体内部介质
- Macro Shape: LOCKED
- Camera: nearly static / tiny push
- Motion: 内部水流连续向上与向后流动
- Response: 微粒与水雾沿流场脱离

### Compiled Prompt
基于原始图片进行3秒图转视频。严格保持宫殿、人物、巨型水灵体的整体轮廓、尺度、位置和原始空间关系不变。水灵体不得行走、转身、抬手或改变人体轮廓。

巨型水灵体遵循“形不动、质在动”：宏观人形轮廓稳定，内部透明水流与细小水粒沿既有身体结构持续缓慢流动，局部水丝向后拉伸，少量水雾和微粒从轮廓边缘自然脱离并消散。人物只保持静止尺度参照，不做明显动作。

摄影机近乎固定，仅有极弱向前推进以增强巨物压迫感。宫殿完全固定。保持原始光向和曝光，水体高光随内部流动产生连续微变化。真实流体重量、透明介质层次、自然空气透视、宁静而宏大的电影摄影。

负面：body morphing, giant walking, giant turning, limb deformation, liquid body collapse, palace deformation, character mutation, camera orbit, camera shake, rapid zoom, flicker, geometry drift, new objects。