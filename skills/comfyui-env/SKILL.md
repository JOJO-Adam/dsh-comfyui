---
name: comfyui-env
description: "ComfyUI 环境体检与修复：服务连不上、模型不显示、节点缺失、显存不足、Apple Silicon 的 MPS 问题。当 doctor 报错或用户说 ComfyUI 打不开/很慢/一跑就崩时使用。"
whenToUse: "ComfyUI 连不上 / 8188 / 模型缺失 / 节点缺失 / 显存 / OOM / MPS / 启动失败 时"
license: MIT
---

# ComfyUI 环境体检

> 先体检，再改工作流。90% 的“出图坏了”最终是环境问题：服务没起、模型没加载、显存不够。
>
> 下文 `comfy_client.py` 指 `comfyui-studio` 技能下的 `scripts/comfy_client.py`（零依赖）。

## 1. 体检顺序（从上往下，不要跳）

| 步 | 检查 | 命令 / 动作 | 失败含义 |
|---|---|---|---|
| 1 | 服务是否在跑 | `curl -s 127.0.0.1:8188/system_stats` | 没起，或端口不同 |
| 2 | 版本与后端 | 同上，看 `system.comfyui_version` / `devices` | 旧版 API 字段可能不同 |
| 3 | 模型是否可见 | `comfy_client.py models` | 模型放错目录 / 未刷新 |
| 4 | 节点是否齐 | `comfy_client.py objects --filter <节点名>` | 自定义节点没装 |
| 5 | 队列是否堵 | `comfy_client.py queue` | 前面的任务卡住 / OOM |

## 2. 常见故障与处置

### 连不上（Connection refused）

- ComfyUI 没启动：先在终端起 `python main.py`；
- 端口不是 8188：`--port` 换过就用 `--host 127.0.0.1:<端口>`；
- 在另一台机器：启动加 `--listen 0.0.0.0`，并确认防火墙放行；
- Docker 里跑：端口映射 `-p 8188:8188`。

### 模型列表是空的

- checkpoint 放 `ComfyUI/models/checkpoints/`，LoRA 放 `models/loras/`；
- 放完要**刷新**（网页端 Refresh，或重启服务）；
- 文件名就是工作流里的 `ckpt_name`，中文/空格文件名容易出问题，建议英文。

### 节点缺失（`Cannot execute because node X does not exist`）

- 工作流用了未安装的自定义节点；
- 先查 `objects --filter <类名>` 确认；
- 装节点用 ComfyUI Manager，或在 `custom_nodes/` 下 clone 后重启；
- 不要为了让工作流跑起来去硬删节点——那会改变管线行为。

### 显存不足（OOM / 卡在 99%）

- 降分辨率优先，其次降 batch size；
- 关掉其他占显存的程序；
- Apple Silicon：确认用的是 MPS 而不是 CPU（`system_stats` 里看 device）；
- 实在不够：分段生成 + 拼接，或换更小的模型。

### Apple Silicon 特别提示

- MPS 下部分采样器/精度组合会报错或出黑图，换 `euler` / `dpmpp_2m` 先排除；
- 统一内存被系统占用时表现像“显存不足”，先看活动监视器；
- 首次加载模型很慢是正常的，不是卡死。

### SaveImage 报 `Operation not permitted` / `PermissionError`

- **现象**：前面节点全部执行成功，最后 `SaveImage` 写文件失败，队列里显示 error。
- **原因**：ComfyUI 进程对目标输出目录没有写权限（被沙箱、容器或受限用户启动时常见）。
- **处置**：用可写目录重启，不要为了绕过保存去删 `SaveImage` 节点：

  ```bash
  python main.py --output-directory <可写目录> --temp-directory <可写目录>
  ```

  或让 ComfyUI 以有权限的普通用户身份、在沙箱外启动。

## 3. 体检输出怎么读

`doctor` 会打印：

```
✅ 服务可达 · ComfyUI 0.3.x · device mps · vram 16.0 GB
✅ 队列 0 · 节点 1203 · checkpoints 4 · loras 12
```

- 队列 > 3 且不动 → 前面的任务卡住，`interrupt` 后重试；
- checkpoints 为 0 → 模型目录问题；
- device 是 `cpu` → 跑得慢是必然，先修环境。

## 4. 边界

- 不代装 ComfyUI、不代下模型；
- 不修改用户的模型文件；
- 环境修不好时，明确告诉用户卡在哪一步，而不是继续调工作流。
