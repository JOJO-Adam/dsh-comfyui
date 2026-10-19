# dsh-comfyui · JOJO&Adam

ComfyUI 在 DeepSeek Harness 里的生产包：环境体检、零依赖 API 客户端、工作流改造、实测参数矩阵、崩图排查、一致性与批量。

不是“教你怎么点 ComfyUI”，是让 agent 真的能把图跑出来、把坏图查明白。

## 安装

```bash
# 本地开发
dsh plugin --profile desktop add link:/absolute/path/to/dsh-comfyui

# 从 npm
dsh plugin --profile web add @jojonadam/dsh-comfyui        # Web 版
dsh plugin --profile desktop add @jojonadam/dsh-comfyui    # 桌面版
```

## 30 秒上手

前置：本机 ComfyUI 已启动（默认 `127.0.0.1:8188`）。

```bash
# 1. 体检
python3 skills/comfyui-studio/scripts/comfy_client.py doctor

# 2. 跑一张（示例工作流是标准 SD1.5 txt2img）
python3 skills/comfyui-studio/scripts/comfy_client.py submit \
  --workflow skills/comfyui-studio/examples/sd15_txt2img_api.json \
  --wait --outdir outputs/comfyui/demo
```

第一次跑之前把示例里的 `ckpt_name` 换成你本地 `models/checkpoints/` 里的文件名（`comfy_client.py models` 可以列）。

## 包含

| 技能 | 用途 |
|---|---|
| `comfyui-studio` | 总入口：体检、提交、取图、路由（含客户端脚本与示例工作流） |
| `comfyui-env` | 连不上、模型缺失、节点缺失、OOM、MPS 问题 |
| `comfyui-production-sop` | 六层故障模型与生产流程 |
| `comfyui-prompt-engineering` | 提示词结构、失效模式、权重坑 |
| `comfyui-workflow-architecture` | 高清修复、局部重绘、管线改造 |
| `comfyui-parameter-tuning` | CFG/步数/分辨率/采样器实测矩阵 |
| `comfyui-troubleshooting` | 黑图、花图、主体重复、彩边、OOM 排查树 |
| `comfyui-consistency-batch` | 角色一致、固定前缀、队列批量 |

## 设计边界

- 只连本地 ComfyUI，不经过云端；
- 不代装 ComfyUI、不代下模型；
- 参数矩阵基于 SD1.5 + Apple M5 实测，SDXL / Flux 需重新给区间；
- 客户端零依赖（Python 标准库），兼容 Python 3.8+。

## 验证

```bash
node test/provider.test.mjs
python3 skills/comfyui-studio/scripts/comfy_client.py --help
```

实机验证：ComfyUI 0.41.0 · Apple M5 16GB · MPS，SD1.5 512×512 / 20 步 / cfg 7 / euler，三次中位数 **11.7s**（10.4–15.1s，2026-10-19）。

## 品牌

JOJO & Adam · <https://jojo-adam.com>

## License

MIT
