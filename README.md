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

**执行层（本插件自带脚本）**

| 技能 | 用途 |
|---|---|
| `comfyui-studio` | 总入口：体检、提交工作流、取图、六域路由（含 `scripts/comfy_client.py` 与示例 workflow） |
| `comfyui-env` | 服务连不上、模型不显示、显存不够、MPS 问题 |

**标准与流程**

| 技能 | 用途 |
|---|---|
| `comfyui-sop` | 标准实务：控制层真存在性、工具名表、反编造红线（单一真相源） |
| `comfyui-workflow-design` | 从零设计工作流：节点选型、接线纪律、格式校验 |
| `comfyui-workflow-upgrade` | 改造：高清修复、局部重绘、denoise 取值、常见接错线 |
| `comfyui-param-tuning` | 参数实测矩阵：CFG / 步数 / 分辨率 / 采样器耗时 |
| `comfyui-prompt-structure` | 提示词结构：句子优于关键词、四种失效模式 |
| `comfyui-batch-consistency` | 构图一致 vs 身份一致、批量队列、seed 不是身份锁 |
| `comfyui-failure-tree` | 崩图排查树：黑图/花图/主体重复/彩边/OOM → 层 → 动作 |
| `comfyui-production-sop` | 生产 SOP：六层故障模型、SD1.5 安全区间 |
| `comfyui-generation-exec` | 提交队列、跟进度、取回真实结果 |
| `comfyui-mcp-bridge` | MCP 桥接、工具名对齐、启动排障 |
| `comfyui-model-management` | 模型/LoRA 清单、版本核对 |
| `comfyui-handoff` | 资产交接：交付文档 + 缺口清单 |
| `comfyui-hardware-audit` | 硬件审计：探针 → 动态能力卡 → 量化降级 |

**五条产线**

| 技能 | 用途 |
|---|---|
| `comfyui-video-pipeline` | T2V / I2V / 动作迁移 / 多镜头 / 补帧 |
| `comfyui-audio-pipeline` | 配乐 / 音效 / 剪辑节点 / 音视频合流 |
| `comfyui-3d-pipeline` | 图生 3D / 贴图 / 网格清理 / GLB 出货 |
| `comfyui-training-lora` | LoRA 训练、数据集、角色一致性 |
| `comfyui-vision-utils` | 去背景 / 修复 / 放大 / 分割 / 打标 |

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
