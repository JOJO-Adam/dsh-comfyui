---
name: comfyui-training-lora
description: "LoRA 训练：数据集组装、训练链、应用与角色一致性；不承诺收敛效果。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# 训练管线（LoRA 微调 / 数据集 / 角色一致性）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

证据级：`[实测]` 本机可复现 ｜ `[外核]` URL+日期 ｜ `[待核验]` 没验过别当能跑。
本文 `ClassType` 均在本机 ComfyUI 0.41.0 `/object_info`（2026-11-03，987 类）命中 `[实测]`。

## 0. 硬件闸门（训练前必走）

训练是全包最吃资源的域：先走 `comfyui-hardware-audit` 入场审计 → 小样本探针（先训 10–20 步看显存/内存曲线）→ 动态能力清单 → 降级。🔴 不写「多少 GB 能训多大 LoRA」这类断言；每个数字都要本机实测并带机器 + 内存口径 + 采样时刻。

## 1. 数据集（本地，全部 `[实测]` 节点）

- 建集：`MakeTrainingDataset`（从图建集）；读入 `LoadImageDataSetFromFolder`、`LoadImageTextDataSetFromFolder`（图文对）。
- 存/洗：`SaveTrainingDataset`、`SaveImageTextDataSetToFolder`、`ShuffleDataset`、`ShuffleImageTextDataset`。
- 视频数据集支线：`LoadVideoDataSetFromFolder`、`LoadVideoTextDataSetFromFolder`、`ShuffleVideoDataset`、`ShuffleVideoTextDataset`。
- 打标缺口：WD14/BLIP 类打标节点**不在本机 `/object_info`**（987 类里无 caption/tagger 节点）→ 打标能力 `[待核验]`（多为 custom node，装上后再实测）；当前先用人工标注文本对。

## 2. 训练（核心链）

`LoadTrainingDataset` → `TrainLoraNode` → `SaveLoRA`（`LoraSave` 亦在列）。
- 超参不写死模板数字：步数/学习率/秩以探针曲线定，结果带采样时刻写进交付单。
- 权重底模（SD1.5/SDXL/FLUX 等）随审计清单走；`GetICLoRAParameters`（IC-LoRA 参数）可用时再用。

## 3. 应用（出图/出视频侧）

- 图像：`LoraLoader`（`LoraLoaderModelOnly` / `LoraLoaderBypass` 变体）或 `LoadLoraModel` + `LoadLoraTextEncoder` / `LoraModelLoader`。
- 视频：训练产物按 `comfyui-video-pipeline` 的 I2V/T2V 骨架挂载；动作一致性优先配合固定前缀法（`comfyui-batch-consistency`）与提示结构（`comfyui-prompt-structure`）。
- 验收口径：先小批量抽图对比身份一致性（对照 `comfyui-batch-consistency` 的一致性判据），不过就不回炉，不硬吹「已一致」。

## 4. 停手与降级

1. 探针阶段显存/内存顶不住 → 降 batch、降分辨率、降 rank，逐项记入交付单；再不行如实说「本机训不了」。
2. 训练不承诺收敛与效果——数据质量与超参决定结果，本团只交「跑得起来的训练链 + 实测记录」。
3. 产出物（LoRA 权重）归用户（资质墙：判据=产出物归属）。
