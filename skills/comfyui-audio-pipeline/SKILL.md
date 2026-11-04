---
name: comfyui-audio-pipeline
description: "音频管线：配乐、音效与剪辑节点、音视频合流。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# 音频管线（配乐 / 音效 / 剪辑 / 与视频合流）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

证据级：`[实测]` 本机可复现 ｜ `[外核]` URL+日期 ｜ `[待核验]` 没验过别当能跑。
本文 `ClassType` 均在本机 ComfyUI 0.41.0 `/object_info`（2026-11-03，987 类）命中 `[实测]`；权重文件本机未装 `[待核验]`。

## 0. 硬件闸门

音频探针规格自定（如 10s 低采样），走 `comfyui-hardware-audit` 四步；禁档位断言。

## 1. 配乐生成（ACE-Step 路线）

骨架：`EmptyAceStep1.5LatentAudio`（或 `EmptyAceStepLatentAudio`）→ `TextEncodeAceStepAudio1.5`（`TextEncodeAceStepAudio` 旧版）→ 采样链（`SamplerCustomAdvanced` + `KSamplerSelect`）→ `VAEDecodeAudio` → `SaveAudio` / `SaveAudioMP3` / `SaveAudioOpus`。
- 权重：ACE-Step 系文件 `[待核验·本机未装]`；「ACE-Step 1.5」版本 `[实测·节点名 EmptyAceStep1.5LatentAudio 印证]`。

## 2. Stable Audio 路线

骨架：`ConditioningStableAudio`（文本条件）→ `EmptyLatentAudio` → 采样链 → `VAEDecodeAudio` → `SaveAudio`。
- 「Stable Audio 3」版本号 `[待核验]`（无直链外核，原引用为内部提案，已降级）；节点名只印证到 StableAudio 族 `[实测]`，版本细节 `[待核验]`。

## 3. 音效与剪辑（全部本地、无需大模型）

- 读入/录制：`LoadAudio`、`RecordAudio`。
- 拼接与混音：`AudioConcat`、`AudioMerge`、`SplitAudioChannels`。
- 调整：`AudioAdjustVolume`、`AudioEqualizer3Band`。
- 预览：`PreviewAudio`。
这类节点是「当场能跑」的第一梯队：只要 ComfyUI 起着，就有 `/object_info` 实测背书。

## 4. 与视频合流（AV）

- LTXV AV 链：`LTXVEmptyLatentAudio`、`LTXVReferenceAudio`（参考音色）、`LTXVConcatAVLatent`（音视频潜空间合流）、`LTXVSeparateAVLatent`（拆流）、`LTXVAudioVAELoader` + `LTXVAudioVAEEncode` / `LTXVAudioVAEDecode`。
- 参考音色：`ReferenceTimbreAudio`。
- 云端音色/音乐 API（`ElevenLabsVoiceSelector`、`FishAudioVoiceSelector`、`ComfyCloudMiniMaxMusic3TextToAudioNode`、`ByteDanceSeedAudio`）= **API 节点（第三方付费，账号自理）**，只做如实指路，不进本地主链。

## 5. 停手与降级

1. 音频权重未装 → 先只交「剪辑/合流」层（第 3、4 节），生成层标 `[待核验]`。
2. 显存吃紧 → 降时长 / 降采样率，把降了什么写进交付单。
3. 不承诺成曲质量与商用版权；产出物归用户（资质墙：判据=产出物归属）。
