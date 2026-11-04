---
name: comfyui-vision-utils
description: "实用视觉：去背景、遮罩手术、局部重绘、放大链、分割跟踪、电商一条龙。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# 实用视觉（去背景 / 修复 / 放大 / 分割 / 打标）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

证据级：`[实测]` 本机可复现 ｜ `[外核]` URL+日期 ｜ `[待核验]` 没验过别当能跑。
本文 `ClassType` 均在本机 ComfyUI 0.41.0 `/object_info`（2026-11-03，987 类）命中 `[实测]`。

## 1. 去背景

`LoadBackgroundRemovalModel` → `RemoveBackground` → `SplitImageWithAlpha`（拆 RGBA）→ `SaveImage`。权重 `[待核验·权重]`（本机未装，节点存在性 `[实测]`，权重路径/来源未核验，装什么才能跑见 `comfyui-hardware-audit` 动态清单）。
- 云端替代（API 节点，第三方付费 + 账号自理，只指路不进主链）：`BriaRemoveImageBackground`、`RecraftRemoveBackgroundNode`。

## 2. 遮罩手术（去背景后的精修，全本地）

`ImageToMask`、`LoadImageMask`、`GrowMask`（扩边）、`FeatherMask`（羽化）、`MaskComposite`（多遮罩合成）、`InvertMask`、`CropMask`、`ImageCropToMask`、`ImageColorToMask`、`ImageCompositeMasked`（贴回）、`MaskPreview`（看结果）。

## 3. 修复 / 局部重绘

`LoadImage` + `LoadImageMask` → `VAEEncodeForInpaint` + `InpaintModelConditioning` → `KSampler`（denoise 取值照 `comfyui-param-tuning` 的实测区间）→ `VAEDecode` → `SaveImage`。
- denoise 是成败手：局部重绘只动遮罩区时取低值，具体数值引 `comfyui-workflow-upgrade` 的实测取值，不新造数字。

## 4. 放大链

`UpscaleModelLoader` → `ImageUpscaleWithModel` →（需再走扩散精修时）`LatentUpscaleBy` / `SD_4XUpscale_Conditioning` + `SamplerLCMUpscale` → `SaveImage`（`SaveImageAdvanced` 可带元数据）。
放大模型文件 `[待核验·本机未装]`；节点存在性 `[实测]`。

## 5. 分割 / 跟踪（SAM3 族）

`SAM3_Detect`（检测）→ `SAM3_VideoTrack`（视频跟踪）→ `SAM3_TrackToMask`（出遮罩）→ `SAM3_TrackPreview`（预览）。
- 3D 人体支线：`SAM3DBody_Loader` / `SAM3DBody_Predict` / `SAM3DBody_Render` / `SAM3DBody_Smooth` / `SAM3DBody_FaceExpression`。
- 权重 `[待核验·本机未装]`；「SAM 3/3.1」版本号 `[待核验]`（无直链外核，原引用为内部提案，已降级）+ 节点名印证 SAM3 族 `[实测]`。

## 6. 打标（诚实缺口）

WD14 / BLIP / 打标类节点**不在本机 `/object_info`**（987 类内无 caption/tagger 节点）→ 打标能力 `[待核验]`。常见做法是装 custom node，装上后以 `refresh_nodes` + `/object_info` 复验再启用；在此之前训练管线（`comfyui-training-lora`）走人工标注。

## 7. 电商一条龙（合成管线）

`LoadImage` → `RemoveBackground` →（§2 精修）→（§4 放大）→ `SaveImage` / `SaveImageAdvanced`。每一步的模型前提走 `comfyui-hardware-audit` 动态清单；缺模型就只跑有模型的段，缺哪段写哪段。

## 8. 停手与红线

1. 模型未装的段不硬跑，标 `[待核验]` 并交「装什么才能跑」清单。
2. 不判审美与商用合规（归用户与法务，见 `comfyui-sop`）；产出物归用户（资质墙）。
