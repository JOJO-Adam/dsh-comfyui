---
name: comfyui-workflow-architecture
description: "工作流改造手册：从官方默认图出发的四种生产管线、决定高清修复与局部重绘成败的 denoise 取值，以及每种改造最常见的接错线方式。"
whenToUse: "ComfyUI 工作流 / 改造 / hires fix / 高清修复 / 局部重绘 / 接错线 时"
license: MIT
---


# 工作流改造手册

> DSH 执行层（跑 API、提交工作流、取图）：见 `comfyui-studio` 技能。


## 一 · 为什么不给现成 json

别人做的 json 导入后三种典型失败：
1. 缺自定义节点（红框报错）
2. 模型名对不上（本地没有同名 checkpoint）
3. 版本差异导致节点参数改了

**所以给改造步骤**——从官方默认图出发，官方图本身验证过，不会导入失败。

## 二 · 四种生产管线

### ① 高清修复（hires fix）—— 最重要的一个

```
默认图：EmptyLatentImage(512) → KSampler → VAEDecode → SaveImage

改造后：
EmptyLatentImage(512) → KSampler_A(denoise 1.0)
  → LatentUpscale(×1.5~2.0)
  → KSampler_B(denoise 0.45~0.6)     ← 关键
  → VAEDecode → SaveImage
```

🔴 **KSampler_B 的 denoise 必须显著低于 1.0**。
- 0.45-0.6：在原图基础上补细节（正确）
- **忘了改还是 1.0：等于重画，细节全丢，还可能出主体重复**
- 低于 0.35：几乎不变化，白跑一遍

**为什么必须这样**：我们的实测显示，直接生成 768 会出主体重复（SD1.5 训练分辨率是 512）。hires fix 是绕过这个限制的标准做法。

### ② 局部重绘（inpaint）

```
LoadImage → VAEEncode → SetLatentNoiseMask（接遮罩）
→ KSampler(denoise 0.7~0.9) → VAEDecode
```

- denoise < 0.5：改不动
- denoise 0.7-0.9：正常
- denoise > 0.95：遮罩外也会变

**常见接错**：遮罩没接进 `SetLatentNoiseMask`，直接给 KSampler → 局部重绘退化成整图重绘。

### ③ 参考控制（ControlNet）

```
LoadImage(参考图) → Preprocessor(线稿/姿势/深度) → ControlNetApply
→ 输出接到「正向 conditioning」→ 再进 KSampler
```

- strength 0.6-0.8 通常够
- strength 1.0：过度约束，出图生硬
- **接错到负向 conditioning → 完全不生效**（最常见的错）

### ④ 批量输出

两条路：

| 方式 | 优点 | 风险 |
|---|---|---|
| `EmptyLatentImage.batch_size = N` | 一次提交 | N 大→ OOM |
| 队列多次提交（同 seed 递增） | 稳、可控 | 慢一点 |

**推荐队列方式**：`SaveImage.filename_prefix` 带递增序号，中途失败不影响已完成部分。

## 三 · 让工作流可调试的三条

1. **一次只改一段** —— 加三个节点出问题，不知道是哪个
2. **保留默认图作回退** —— 改造失败能退回去
3. **用 Note 节点标注每段干什么** —— 一周后自己都看不懂

## 四 · 常见改错对照表

| 改错 | 后果 |
|---|---|
| 高清修复第二段 denoise 还是 1.0 | 等于重画，越修越糊 |
| ControlNet 接到负向 | 完全不生效 |
| batch_size 过大 | OOM |
| 遮罩未接 SetLatentNoiseMask | 局部重绘变整图重绘 |
| LatentUpscale 倍率 > 2.0 | 二次采样压力大，易出重复主体 |

## 五 · 交付格式

```
起点（从官方图的哪个节点开始）
步骤（第 1 步加什么、连到哪、参数多少）
每步目的
验收（跑一次应看到什么）
回退（改坏了怎么退）
```

## 六 · 红线

- 不给"直接导入的 json"
- 必须写明每段 KSampler 的 denoise
- 一次只改一段
- 需要额外节点时明确标注「需先装 X」，不假设用户有
