---
name: comfyui-3d-pipeline
description: "3D 管线：图生 3D、贴图与法线、网格清理、GLB/点云出货；精修转 blender-* 技能。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# 3D 管线（图生 3D 资产 / 贴图 / 网格清理 / 出货路由）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

证据级：`[实测]` 本机可复现 ｜ `[外核]` URL+日期 ｜ `[待核验]` 没验过别当能跑。
本文 `ClassType` 均在本机 ComfyUI 0.41.0 `/object_info`（2026-11-03，987 类）命中 `[实测]`；3D 权重本机未装 `[待核验]`。

## 0. 硬件闸门与定位

- 走 `comfyui-hardware-audit`：3D 生成吃显存，探针先用低面数/低分辨率图。
- 🔴 **分工边界**：本团交「能用的 3D 资产」；拓扑精修、出货级清理、渲染出片走 **blender-studio 跨团路由**，不抢活（停手条件见 §4）。

## 1. 图生 3D（Hunyuan3D v2 路线）

骨架：`LoadImage`（参考图）→ `Hunyuan3Dv2Conditioning`（多视角用 `Hunyuan3Dv2ConditioningMultiView`）→ `EmptyLatentHunyuan3Dv2` → 采样链 → `VAEDecodeHunyuan3D` → `MeshToFile3D` / `SaveGLB` / `Save3DAdvanced` → `Preview3D`（`Preview3DAdvanced`）。
- 权重：Hunyuan3D 系 `[待核验·本机未装]`；版本「2.0/2.1」`[外核·https://docs.comfy.org/tutorials/3d/hunyuan3D-2 （2026-11-03 访问）]`（官方教程列 2.0/2.1/turbo），节点名印证 v2 族 `[实测]`。
- 其他生成路线（节点存在性 `[实测]`，服务多为第三方 API）：`Rodin3D_Gen2` / `Rodin3D_Gen25_Image`、`TripoMeshCompleteNode`、`MeshyImageToModelNode`、`Tencent3DPartNode`——属 **API 节点（第三方付费，账号自理）**，只做如实指路。

## 2. 贴图与法线

`ApplyTextureToMesh`（贴图）、`MeshTextureToImage`（UV 出图）、`UnwrapMesh`（UV 展开）、`PaintMesh`（手绘）、`BakeNormalMapFromMesh`（法线烘焙）、`BakeTextureFromVoxel`。

## 3. 网格清理（出货前，本团做「能用」级）

`RemeshMesh`（重拓扑·低配）、`DecimateMesh`（减面）、`MeshSmoothNormals`（法线平滑）、`MergeMeshes` + `GetMeshInfo`（体检）、`RotateMesh` / 变换、`Get3DComponents`（拆件）。
- 格式出口：`SaveGLB` / `MeshToFile3D` / `Save3DAdvanced`；点云/高斯泼溅支线 `File3DToSplat`、`SplatToMesh`、`SaveGaussianSplat`、`PreviewGaussianSplat`。
- 读入体检：`Load3D` / `Load3DAdvanced`。

## 4. 出货路由（blender-studio，不抢活）

- 交给 blender-studio 的：成品 GLB/网格 + 本团的体检单（面数、贴图尺寸、法线状态，来自 `GetMeshInfo`）。
- 本团停手条件：出现「要按出货标准调拓扑/布线/材质节点/渲染」的诉求 → 停手，写路由单，不硬做。
- 路由单三件：资产文件、体检数字、「哪里没做到出货级」的诚实缺口清单。

## 5. 降级与红线

1. 显存不足 → 降生成分辨率 / 用减面级管线（§3），如实告知。
2. 模型文件未装 → 只交 §2-§3 的清理与贴图层，生成层标 `[待核验]`。
3. 不承诺资产可直接进生产管线（那是 blender-studio 的验收标准）；产出物归用户（资质墙）。
