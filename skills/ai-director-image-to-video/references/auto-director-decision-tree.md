# V4｜Auto Director Decision Tree

## Purpose
让 Skill 在用户只上传原图、时长、画幅和平台时，自动判断：

- 什么必须锁死
- 谁是真正的主运动主体
- 哪些对象只能做二级响应
- 哪个镜头风险最低
- 运动预算如何分配
- 是否需要自动降级
- 最终如何编译为 Kling 等平台提示词

核心原则：**先做风险控制，再做电影化。**

---

## 1. Scene Classification
先按画面主体判断场景类型，可多选但必须指定一个 dominant_scene：

- HUMAN：人物主导
- CREATURE：动物 / 凤凰 / 仙鹤主导
- ARCHITECTURE：古建筑 / 城市 / 宫殿主导
- WATER：瀑布 / 江河 / 海面主导
- ATMOSPHERE：云海 / 雾 / 烟主导
- ENTITY：灵体 / 能量体 / 半透明巨像主导
- TEXTURE_LOCK：书法 / 铭文 / 壁画 / 复杂纹样占大面积
- MIXED：多主体复杂场景

若同时出现复杂建筑 + 大面积文字 + 巨型动物 / 灵体，直接标记 HIGH RISK。

---

## 2. Structural Lock Decision
### 必锁对象
默认锁定：
- 建筑主体与屋檐
- 桥梁与地形轮廓
- 人物身份、脸、服装、比例、位置
- 动物数量、头部、翼数、尾羽结构
- 文字、书法、壁画、纹样
- 原始构图与透视

### 可动对象
仅当具有真实物理原因时允许：
- 人物呼吸 / 微抬头 / 微转头 / 手腕调整
- 羽毛、尾羽、裙摆、发丝、飘带
- 水流、水雾、波纹
- 云雾低频漂移
- 灵体内部介质
- 旗帜、门帘等附属软体

建筑主体本身默认不可动。

---

## 3. Risk Scoring
使用 0–10 风险分。

### +2 条件
- 复杂古建筑
- 大面积文字 / 书法
- 巨型动物羽毛
- 半透明灵体
- 强透视
- 近景巨大遮挡
- 多主体竞争
- 用户要求环绕 / 快速镜头

### +1 条件
- 布料很多
- 云雾很多
- 人物很小
- 画面主体接近边缘
- 大面积细纹理

### 等级
- 0–3：LOW
- 4–6：MEDIUM
- 7–10：HIGH

HIGH 自动执行：
- primary_motion = 1
- camera_motion_strength *= 0.5
- 禁止 orbit
- ambient_motion_count <= 2
- lighting_change = minimal
- 强化 negative constraints

---

## 4. Primary Motion Selection
按以下优先级选主运动：

1. 用户明确指定的生命主体，但若高风险则降级动作幅度
2. 画面视觉锚点
3. 具有最强叙事因果的对象
4. 具有稳定物理运动的对象（水流 > 云雾 > 建筑）

禁止把“建筑”设为一级运动主体，除非用户明确要求建筑机关、坍塌、开门等剧情动作。

### 人物
- 人物占画面 <10%：呼吸 / 微抬头 / 微转头
- 10–30%：可加入手腕、视线、半步以内重心变化
- >30%：可加入更明显表演，但避免复杂手指动作

### 鸟类 / 凤凰
- 大翼已展开：优先一次翼下压 + 滑翔
- 小型鸟：允许更高频扑翼
- 巨型凤凰：最多一次主要扑翼 / 3秒

### 灵体
- 默认：Macro Shape locked
- Primary Motion = Internal Medium Flow

### 水体
- 瀑布：持续下落
- 水面：低幅波纹，不凭空起大浪

---

## 5. Camera Decision Tree
### 若近景有巨大前景
优先：slow push-in / subtle dolly / tiny crane，利用视差。

### 若巨物已经充满画面
优先：static / tiny crane / micro pull-back，避免继续强推。

### 若建筑复杂
优先：static / slow push-in；禁止大幅 orbit。

### 若画面强调压迫
low angle + slow push-in。

### 若强调宏大
slow crane / drone glide + layered parallax。

### 若强调宁静
static 或极慢运动。

### 若 HIGH RISK
camera = static 或 single slow axis motion。

---

## 6. Motion Budget Auto Allocation
### LOW
- Camera 25
- Primary 40
- Secondary 20
- Ambient 10
- Lighting 5

### MEDIUM
- Camera 20
- Primary 40
- Secondary 20
- Ambient 10
- Lighting 5
- Safety reserve 5

### HIGH
- Camera 10–15
- Primary 40–45
- Secondary 20
- Ambient 5–10
- Lighting 0–3
- Safety reserve >=15

Safety reserve 表示“明确不让某些区域运动”的预算。

---

## 7. Wind Field Decision
如果画面存在 2 个以上受风软体，必须定义统一风场：

- direction
- strength
- stability
- affected_objects

所有头发、衣带、尾羽、旗帜、薄云必须遵循同一主风向。

---

## 8. Causal Motion Graph
所有二级运动必须能写成：

`Primary Cause -> Secondary Response`

例如：
- wing downstroke -> nearby mist curls
- high-altitude wind -> ribbon + hair drift
- waterfall impact -> mist expansion + surface ripples
- body turn -> costume inertia

如果无法找到物理原因，则删除该运动。

---

## 9. Auto Degrade Rules
出现以下任意 2 项，自动降低复杂度：
- 主体数量 > 2
- 镜头运动 > 1 主 + 1 辅
- 明显环境运动 > 3
- 存在大面积文字
- 需要生成大量隐藏面
- 复杂羽毛 + 快速运动
- 透明灵体 + 人体大动作

降级顺序：
1. 删除光影动态
2. 删除非必要粒子
3. 环境运动降为低频
4. 二级动作减少
5. 主动作减幅
6. 镜头降为单轴或静机

---

## 10. Emotion-to-Camera Mapping
- 压迫：low angle + scale contrast + slow push-in
- 宏大：layered depth + slow movement + atmospheric perspective
- 唯美：soft secondary motion + restrained highlights
- 宁静：low-frequency motion + stable camera
- 神秘：partial occlusion + slow reveal + fog depth
- 紧张：limited FOV + micro push + restrained subject movement

情绪词必须转化为镜头与运动，不得只作为形容词堆叠。

---

## 11. Final Decision Object
在编译 Prompt 前，应形成以下内部决策：

```yaml
dominant_scene: CREATURE
risk_level: HIGH
visual_anchor: phoenix
scale_reference: palace
locked_objects:
  - palace
  - roof geometry
  - human position
primary_motion:
  subject: phoenix
  action: one weighted downstroke then glide
secondary_motion:
  - outer feathers delayed flex
  - tail feathers inertial drag
ambient_motion:
  - low-frequency cloud drift
camera:
  primary: slow forward glide
  secondary: subtle tilt-up
wind_field:
  direction: rear-right
  strength: gentle
negative_focus:
  - extra wings
  - roof distortion
  - temporal flicker
```

该对象只用于内部决策，不要求用户必须看到。

---

## 12. V4 Execution Rule
当用户只说“这张图做3秒 Kling”时：

1. 不追问非关键参数。
2. 自动解析空间与风险。
3. 自动选主运动。
4. 自动选最低风险镜头。
5. 自动构建因果运动。
6. 自动降级高风险指令。
7. 生成完整 Prompt + 极简 Prompt。
8. 最后执行 40 分质检与 Hard Fail 检查。

最终目标：**用户不需要先懂导演语言，Skill 自己承担导演决策。**