---
name: comfyui-studio
description: "ComfyUI 在 DSH 里的总入口：环境体检、API 提交工作流、批量出图、取图与排障路由。当用户要跑 ComfyUI、出图、批量生成、查崩图原因、接本地 ComfyUI 时使用。"
whenToUse: "ComfyUI / 出图 / 工作流 / 批量生成 / 崩图 / 黑图 / OOM / 127.0.0.1:8188 时"
license: MIT
---

# ComfyUI × DSH

> 本技能是执行层：怎么在 DSH 里把 ComfyUI 跑起来、提交工作流、取回图片。
> 领域知识在另外六个技能里（见第 5 节路由）。

## 0. 先决条件

- 本机已装 ComfyUI，默认监听 `127.0.0.1:8188`；
- 需要局域网访问时，ComfyUI 启动加 `--listen 0.0.0.0`，客户端用 `--host <IP>:8188`；
- DSH 侧只需 Python 3（零依赖脚本），不需要额外装包。

## 1. 30 秒体检

```bash
python3 scripts/comfy_client.py doctor
```

输出会检查：服务是否可达、ComfyUI 版本、GPU/VRAM、队列长度、节点数、可用 checkpoint / LoRA。
任何一项不通，先看 `comfyui-env` 技能，不要急着改工作流。

## 2. 提交工作流

工作流必须是 **API 格式**（ComfyUI 里 `Save (API Format)` 导出的 JSON，顶层是节点 id → `class_type`），不是 UI 格式。

```bash
# 提交并等结果，图片落到指定目录
python3 scripts/comfy_client.py submit \
  --workflow wf.json --wait --outdir outputs/comfyui/2026-10-19

# 只提交不等
python3 scripts/comfy_client.py submit --workflow wf.json

# 查看 / 下载
python3 scripts/comfy_client.py status <prompt_id>
python3 scripts/comfy_client.py download <prompt_id> --outdir outputs/comfyui/2026-10-19
```

批量：写一个循环，每次换 prompt / seed，串行提交（ComfyUI 自己排队）。不要并发轰炸，OOM 多半是这么来的。

## 3. 输出约定（DSH 里很重要）

- 图片统一落到 `outputs/comfyui/<YYYY-MM-DD>/`，文件名带 prompt 摘要 + seed；
- 生成后**用 `present` 把结果给用户看**，不要让用户自己去翻文件夹；
- 一次批量超过 10 张时，先给缩略图/前 3 张，再给完整目录。

## 4. 常用命令补充

```bash
python3 scripts/comfy_client.py queue        # 看队列
python3 scripts/comfy_client.py interrupt    # 中断当前任务（OOM 卡死时用）
python3 scripts/comfy_client.py models       # 列 checkpoint / LoRA
python3 scripts/comfy_client.py objects --filter KSampler   # 查节点输入
```

## 5. 领域路由

| 用户问题 | 调用技能 |
|---|---|
| 服务连不上 / 模型不显示 / 显存不够 | `comfyui-env` |
| 出图不稳、想知道问题在哪一层 | `comfyui-production-sop` |
| 提示词怎么写、为什么不出想要的效果 | `comfyui-prompt-engineering` |
| 改工作流：高清修复、局部重绘、加节点 | `comfyui-workflow-architecture` |
| 参数设多少（CFG/步数/采样器/分辨率） | `comfyui-parameter-tuning` |
| 黑图、花图、主体重复、彩边、报错 | `comfyui-troubleshooting` |
| 角色一致性、批量生产 | `comfyui-consistency-batch` |

## 6. 诚实边界

- 出图质量的上限由本地模型和硬件决定，本技能不承诺“这套参数在你那也能出好图”；
- 不代装 ComfyUI、不代下模型（版权与体积问题）；
- 参数表基于 SD1.5 实测；用户跑 SDXL / Flux 时必须重新给区间，不能套用；
- 所有请求只发往用户指定的本地地址，不经过任何云端。
