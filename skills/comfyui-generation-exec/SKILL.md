---
name: comfyui-generation-exec
description: "生成执行：把校验过的 workflow 提交到本地队列、跟踪进度、取回真实结果。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# ComfyUI 生成执行（comfyui-generation-exec）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

把校验通过的 workflow **真正提交到本机 ComfyUI 队列、跟踪进度、取回真实结果**。

## 1. 提交生成（异步）

- **经 MCP 桥**：`run_workflow` / `execute_workflow`（传 API 格式 workflow），拿回 **prompt_id / 队列 ID**。
- **直连原生 API**：
  ```
  POST /prompt
  body: {"prompt": { "node_id": {"class_type": "...", "inputs": {...}} }}
  ```
  返回 `{"prompt_id": "..."}`。注意 body 必须包 `{"prompt": {...}}`，漏包会 400。
- 异步模型：提交即返回，不等完成——轮询或走 WS。

## 2. 进度跟踪

- **WS `/ws`**：订阅 `progress`（百分比/当前节点）与 `executing` 事件，向用户实时通报。
- **无 WS 时**：`GET /history/{prompt_id}` 轮询，直到出现该 prompt_id 的结果条目。

## 3. 取回结果（真实字节）

- 从 `history[prompt_id].outputs` 取输出节点（Save Image/Video）的 `images`/`gifs` 数组，每项含 `filename` / `subfolder` / `type`。
- `GET /view?filename=...&subfolder=...&type=...` 或 MCP `get_result_image` 取**真实图像/视频字节**——这是"已生成"的证据。
- 多输出（批/视频帧）：逐条取，记录真实路径/字节指纹。

## 4. 排错

- **400**：body 未包 `{"prompt":...}` 或 workflow 非 API 格式。
- **OOM / 队列卡死**：本地 GPU 受限——查 ComfyUI 终端日志，降分辨率/步数或换小模型，不无脑重试。
- **节点错**：核对 `class_type`/输入名（用 `/object_info`），打回补设计。

## 5. 红线

- 未取得真实结果字节前，不得声称"已生成图像/视频"。
- 不编造文件名/参数/耗时——以 `history` / `/view` 真实数据为准。
- 越过 env-setup 闸门强行提交 → 环境不通只能输出"待生成"并显式告知阻塞。

## 6. 判定标准（四件套齐全才算成功）

| # | 判据 | 不通过的表现 |
|---|---|---|
| 1 | `prompt_id` 来自 `/prompt` 真实返回 | 只有一个「已提交」的说法 |
| 2 | `/history/{prompt_id}` 里 `status_str = success` | 只有 `prompt_id` 就宣称已生成 |
| 3 | `/view` 落盘文件 > 0 字节 + SHA-256 真实值（命令按平台选，见 comfyui-sop §11） | 文件 0 字节 / 只贴 URL 不落盘 |
| 4 | 端到端耗时 = `execution_success` − `execution_start` | 用「大概 20 秒」估算 |

附加必报：`execution_cached.nodes`（空数组 = 全量真执行）。收尾必查：`/queue` 无 running/pending，未重复提交。

## 7. 回报格式（硬要求）

收到派单首轮就必须给：`① prompt_id ② history 片段 ③ 路径+字节+SHA256 ④ 耗时 ⑤ 一行结论`。
**禁止**回「没有新情况 / 无待处理动作 / 与上轮一致」——那是把派单误判成后台回调，等于没交付。

## 8. 做不到什么（边界）

- **不保证**出图：OOM / 显存不足会失败，如实报日志片段，不刷队列硬试。
- **不替代**上游校验：没 validate 过的 workflow 不提交。
- **不做**环境修复与配置改动（归 env-setup）。
- **不判**画质与商用合规（归用户，口径见 comfyui-sop §9）。
- **不承诺**逐字节复现：未重跑比 sha256 前不下「完全相同」的结论（权威依据见 comfyui-sop §9）。
- **超时与中断**：单张等待上限建议 max(3×T, 60 秒)，T 用 `/history` 实测；卡住时 `POST /interrupt`（或 MCP `cancel_current`）停当前这张、`POST /queue` body `{"clear": true}`（或 `clear_queue`）清队列。完整依据与步骤见 comfyui-sop §12。
