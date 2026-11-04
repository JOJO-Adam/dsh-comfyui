---
name: comfyui-video-pipeline
description: "视频管线：T2V/I2V/动作迁移/多镜头续写/放大补帧，LTXV、Wan、HunyuanVideo 三条路线。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# 视频管线（T2V / I2V / 动作迁移 / 多镜头 / 放大补帧）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

证据级约定：`[实测]` = 本机可复现命令的结果；`[外核]` = URL + 访问日期；`[待核验]` = 没验过，**别当能跑**。
本文全部 `ClassType` 节点名已在本机 ComfyUI 0.41.0 `/object_info`（2026-11-03 实测，987 类）命中 → 节点存在性 `[实测]`；**接线**以 `get_node_info` / `validate_workflow` 校验为准；**权重文件**本机未装的一律 `[待核验]`。

## 0. 进场先过硬件闸门

任何视频任务开跑前走 `comfyui-hardware-audit` 四步：入场审计 → 小规格探针（视频从 480p×2s 起步）→ 动态能力清单（硬件前提卡）→ 量化降级。禁止按显存写死档位断言；本机是 Mac/MPS 统一内存，数字不得外推 NVIDIA。

## 1. T2V 文生视频（LTXV 路线，本地节点最全）

骨架（API 格式导出后可跑）：
`UNETLoader` → `LTXVConditioning` ← `CLIPLoader` + `CLIPTextEncode`；`EmptyLTXVLatentVideo` → `LTXVScheduler` + `SamplerCustomAdvanced`(`KSamplerSelect` + `SplitSigmas`) → `VAEDecode` → `SaveWEBM` / `SaveVideo`。
辅助节点：`LTXVDurationPredictor`（先估时长）、`LTXVContextWindows`（长视频分窗）、`LTXVSpatioTemporalGuidance`、`LTXVDualCFGGuider`。

- 权重：LTXV 系模型文件（`models/diffusion_models/` + `models/text_encoders/` + `models/vae/`）`[待核验·本机未装]`；模型族与节点族对应关系 `[实测·节点名]`。
- 版本号「LTX 2.5」`[外核·https://docs.comfy.org/tutorials/video/ltx/ltx-2-5 （2026-11-03 访问）]`（官方教程含 LTX-2.5/2.3 说明）；节点名只印证到 LTXV 族 `[实测]`，本机小版本 `[待核验]`。

## 2. I2V 图生视频

- LTXV 路线：`LoadImage` → `LTXVImgToVideo`（或 `LTXVImgToVideoInplace`）→ 上面同一条采样链。
- Wan 2.2 路线：`Wan22ImageToVideoLatent`（`[实测·节点名]` 印证 Wan2.2 族）+ `ModelMergeWAN2_1`（合并参考）。
- HunyuanVideo 1.5 路线：`HunyuanVideo15ImageToVideo` + `EmptyHunyuanVideo15Latent` + `TextEncodeHunyuanVideo_ImageToVideo`。
- 三条路线的权重均 `[待核验·本机未装]`；选路线前先看审计里的已装模型清单，**装了什么跑什么**。

## 3. 动作迁移 / 参考驱动

- 本地节点族：`WanAnimateToVideo`、`WanAnimate2ToVideo`、`WanAnimate2Cache`（缓存复用）、`WanMoveTrackToVideo`、`WanTrackToVideo`、`GenerateTracks`（轨迹生成）`[实测·节点名]`。
- 音频驱动口型/节奏：`WanDancerEncodeAudio`、`WanDancerPadKeyframes`。
- 外部 API 形态的 `Wan2ReferenceVideoApi` / `KlingMotionControl` / `HiggsfieldMotionTransferNode` 属 **API 节点（第三方云）**：只做如实指路，标第三方付费 + 账号自理，不进本地管线主链。

## 4. 多镜头 / 续写

- 关键帧法（本地）：`LTXVAddGeneratedKeyframes` + `LTXVGeneratedKeyframesToGuides` + `LTXVAddGuide` / `LTXVAddLatentGuide` + `LTXVFreezeLatent`（锁住已成片段）。
- 分窗法：`LTXVContextWindows` 切上下文窗口，窗口间用 `LTXVSeparateGeneratedKeyframes` 对齐。
- 首尾帧法：`LoadImage`×2 → `KlingStartEndFrameNode`/`ByteDance2FirstLastFrameNode` 属 API 节点（第三方付费，账号自理）；本地替代是把首尾帧当 guide 走 LTXV 路线。

## 5. 放大 / 补帧

- 潜空间放大：`LTXVLatentUpsampler`、`HunyuanVideo15LatentUpscaleWithModel`。
- 超分出片：`HunyuanVideo15SuperResolution`。
- 补帧：`FrameInterpolationModelLoader` + `FrameInterpolate`（插帧模型 `[待核验·本机未装]`）。
- 逐段放大 → 补帧 → `SaveVideo`（`SaveWEBM`/`SaveAnimatedWEBP` 亦 `[实测·节点名]`）。

## 6. 输入输出与复现

- 读入：`LoadVideo`、`LoadVideoDataSetFromFolder`（批量）；音频轨 `LoadAudio`、`LTXVReferenceAudio`。
- 出货：`SaveVideo` / `SaveWEBM`；AV 合流 `LTXVConcatAVLatent`、拆流 `LTXVSeparateAVLatent`。
- 工作流 JSON 嵌入 PNG 可复现（工程底座 `[实测·comfyui-sop]`）；改参数先复制工作流再改，版本化照 `comfyui-workflow-upgrade`。

## 7. 停手与降级（硬）

1. 探针（480p×2s）都跑不完 → 不硬试，先降量化（GGUF/量化权重；外核：ComfyUI 仓库 QUANTIZATION 文档，2026-11-03 参考）。
2. 还不行 → 降分辨率 / 降时长 / 降帧数，把降了什么写进交付单。
3. 本机做不到就如实说做不到；**不承诺成片质量**——产出物归用户，本团只交管线与参数（资质墙：判据=产出物归属）。
