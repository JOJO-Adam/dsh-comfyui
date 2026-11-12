# Changelog

## 0.2.1 — 2026-11-12

- 补英文 README（README.en.md）与版本历史；无功能变更。

## 0.2.0 — 2026-11-04

同步专家团 ComfyUI v1.1.0 / v1.2.0 / v1.2.1 / v1.2.2。

- **全模态**：新增视频（T2V/I2V/动作迁移/补帧）、音频（配乐/音效/合流）、3D（图生 3D/贴图/GLB）、LoRA 训练、实用视觉五条产线。
- **硬件审计**：新增 `comfyui-hardware-audit`（入场审计→探针→动态能力卡→降级），全包禁止静态显存档位表。
- **标准与流程**：新增 `comfyui-sop`（单一真相源）、`comfyui-workflow-design`、`comfyui-generation-exec`、`comfyui-mcp-bridge`、`comfyui-model-management`、`comfyui-handoff`。
- **重命名对齐**：`comfyui-parameter-tuning`→`comfyui-param-tuning`、`comfyui-troubleshooting`→`comfyui-failure-tree`、`comfyui-workflow-architecture`→`comfyui-workflow-upgrade` + `comfyui-workflow-design`、`comfyui-prompt-engineering`→`comfyui-prompt-structure`、`comfyui-consistency-batch`→`comfyui-batch-consistency`。
- **证据级**：能力标注统一为 `[实测]/[外核]/[待核验]`；耗时数字带机器、内存口径、采样时刻。
- 技能数 8 → 20；`node test/provider.test.mjs` 全绿。

## 0.1.2 — 2026-10-21

- 补市场图标与中英 locale 元数据。

## 0.1.1 — 2026-10-21

- 修复技能发现与打包清单。

## 0.1.0 — 2026-10-21

- 首版：ComfyUI 环境体检、API 客户端、参数矩阵、工作流改造与崩图排查。
