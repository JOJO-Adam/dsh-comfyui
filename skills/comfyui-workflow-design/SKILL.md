---
name: comfyui-workflow-design
description: "工作流设计：节点选型、接线纪律、API/UI 两种格式的取舍与校验。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# ComfyUI 工作流设计（comfyui-workflow-design）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

把创意翻译成**可被本机 ComfyUI 执行的节点图**，并定义版本化边界。

## 1. API 格式 vs UI 格式（宪法级边界）

- **API 格式**：`{ "node_id": { "class_type": "...", "inputs": { "key": ["src_node","slot"] | value } } }`。
  - 节点间引用：`inputs` 里的值写成 `["source_node_id", "source_slot"]`，指向某上游节点的第 N 个输出槽。
  - `POST /prompt` 只吃这个格式。
- **UI 格式**：ComfyUI 前端保存的 **workflow.json** / **graph.json**，含 `last_node_id` / `nodes` 数组 / 界面坐标——**不可直接被 `/prompt` 执行**。

<!-- 维护提示：上面两个文件名保持加粗，不要改回反引号——本包用反引号标注包内文件引用，这两个不是包内文件。 -->

- **转换**：在 ComfyUI 前端打开工作流 → 菜单「Save (API Format)」导出 API 格式 JSON，再交生成。不要手改 UI 格式冒充 API 格式。

## 2. 主干节点链路（模板）

```
Load Checkpoint (MODEL/CLIP/VAE)
   ├─ CLIP Text Encode (Prompt)  → positive
   ├─ CLIP Text Encode (Negative)→ negative
   └─ Empty Latent Image         → latent
KSampler (model/positive/negative/latent) → LATENT
VAE Decode (samples)             → IMAGE
Save Image (images)              → 输出文件
```

进阶挂载点：
- ControlNet：在 KSampler 前用 `ControlNet Apply` 注入（需对应预处理器节点）。
- LoRA：`Lora Loader` 置于 Checkpoint 与 KSampler 之间（model/clip 串联）。
- Upscale：`Save` 前接 `Upscale Image (using Model)` 或 `Image Scale`。
- 视频：`Video Combine` / 视频模型（Wan/SVD）链路替代末端 Save Image。

## 3. 节点字段核验

- 每个节点的 `class_type` 与 `inputs` 键名用 `GET /object_info` 或 MCP `list_nodes` 查真实定义，不凭记忆拼。
- **规范节点库兜底（有条件）**：核心规范节点未出现在 `/object_info` 时，**先排查** ① 版本变化（改名 / 移除）② 未安装 / 未注册，两者都排除后才可凭规范节点库放行。
   ② 按节点类别用不同命令：自定义 / 社区节点 → `ls custom_nodes/` + `/object_info` 与 `list_nodes` 双向核对；**ComfyUI 内置核心节点（不在 `custom_nodes/` 里，ls 它永远「没有」）→ 查 ComfyUI 本体：启动日志有无 import failed / 未注册，`/object_info` 里该分类在不在**。两类命令的完整写法以 comfyui-model-management 为准。**不能一见缺失就归因为「服务端自报不全」。** 自定义 / 社区节点仍须 `/object_info` 或 `list_nodes` 实证。
- 必填输入缺失 → 校验失败，打回补设计。

## 4. 工作流版本化

- `dev`：草稿，跑通即标。
- `staging`：稳定可复现（固定模型名、采样器、分辨率）。
- `prod`：交付版（锁定 checkpoint 名/版本、seed 区间、输出命名）。
- 每次改动记变更点（换节点/模型/参数），避免漂移。

## 5. 输出物

- 节点图说明（文本/ASCII/mermaid）、API 格式 workflow JSON（标注 `class_type` 与关键 `inputs`）、版本标签与变更记录。

## 6. 判定标准（怎么算设计过关）

- ✅ 每个 `class_type` 与必填 `inputs` 键名逐字来自 `/object_info`（或属核心规范节点），附核验命令。
- ✅ 明确写出这份是 **API 格式（可执行）** 还是 **UI 格式（不可直接执行）**；后者必须标转换路径。
- ✅ 有版本标签（dev / staging / prod）+ 本次变更点。
- ✅ 不确定处标「待实测」，不写死分辨率/显存/耗时数字。
- ❌ 不过：UI 格式说成「能跑」；节点名靠记忆；无版本标签；**凭规范节点库放行，却留不下 ①② 的排除证据**。

## 7. 做不到什么（边界）

- **不能保证**设计可执行就等于本机能出图：OOM / 缺模型 / 显存不足只有真跑才知道。
- **不能**把 UI 格式手改成 API 格式冒充可执行。
- **不能替代**模型选型（归 model-management）与用户创作意图。
- **不保证**跨版本 / 跨机可直接复用：节点改名或弃用后需重新核验。
