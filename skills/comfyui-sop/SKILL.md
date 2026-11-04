---
name: comfyui-sop
description: "本团标准实务：控制层真存在性、工具名表、工作流纪律、模型管理与反编造红线——一切工程判断的单一真相源。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# ComfyUI 标准实务（comfyui-sop）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

本团所有工程判断的**单一真相源**。任何成员遇到"怎么接/怎么取数据/能不能编"的疑问，先查本文件。

## 1. 控制层真存在性（已核实，无连接幻觉风险）

- **本地 ComfyUI Server**：aiohttp，`http://127.0.0.1:8188` 是它本体的默认监听地址。真实存在，**但控制层在用户侧**，无法随包自带。需本地 GPU/VRAM、模型在 `models/checkpoints/`、workflow 须「Save (API Format)」导出。
- 原生 API：`POST /prompt`（异步，body 须 `{"prompt":{...}}`）·`GET /history/{id}`（结果）·`GET /view`（原始图像字节）·`WS /ws`（实时进度）·`GET /system_stats`（版本/GPU/显存）·`/object_info`（节点目录）·`POST /upload/image`。
- **MCP 桥（社区，真存在）**：`comfyui-mcp`（`uvx comfyui-easy-mcp`，IO-AtelierTech，工具最全：get_system_stats / list_nodes / run_workflow / execute_workflow / get_result_image 等 20+）。
  - 上游：PyPI https://pypi.org/project/comfyui-easy-mcp/ ｜仓库 https://github.com/IO-AtelierTech/comfyui-mcp （配置样例与环境变量表以上游 README 为准）。
  - `comfyui-mcp-server`（轻量 workflow-backed，多 fork）：**无唯一权威仓库，查不到可引用的链接**——用之前让用户自行确认装的是哪一个 fork，本团不为它背书。
- 无官方云端 MCP（ComfyUI 本质是本地引擎）；云端替代是 ComfyDeploy（https://www.comfydeploy.com ）等托管服务，不在本团默认路径。
- ComfyUI 本体：https://github.com/comfyanonymous/ComfyUI （许可证 GPL-3.0，不随本作品分发）。

## 2. 工具名表（真实，禁止臆造）

| 来源 | 工具 |
|---|---|
| 原生 REST | `GET /system_stats` · `GET /object_info` · `POST /prompt` · `GET /history/{id}` · `GET /view` · `WS /ws` · `POST /upload/image` |
| comfyui-mcp | `get_system_stats` / `list_nodes` / `run_workflow` / `execute_workflow` / `get_result_image` |
| comfyui-mcp-server | workflow-backed 提交/查询/取结果（依 fork） |

## 3. 工作流纪律（杜绝幻觉自建）

- **API 格式可执行，UI 格式不可**：UI 格式含 `last_node_id`/`nodes` 数组/坐标，必须转 API 格式（`{node_id:{class_type,inputs}}`）才能被 `/prompt` 执行。转换交给 `comfyui-workflow-design`。
- **节点字段以核验为准**：`class_type` 与输入名用 `/object_info` 或 `list_nodes` 查，不凭记忆拼。
- **版本化**：dev（草稿）→ staging（稳定可复现）→ prod（锁定模型/seed 区间的交付版）。

## 4. 真实结果驱动（宪法级）

- 所有"图像/视频已生成"的结论必须以 ComfyUI 真实返回（队列 ID / `history` 结果 / `get_result_image` 字节）为依据。
- **禁止凭空编造**生成物（内容、参数、文件名、耗时）。未取得真实结果前只能出设计/文档并告知阻塞。

## 5. 模型红线

- checkpoint/LoRA/ControlNet 用户自备、体积大、有版权——**不替用户下载大模型**；引用前先 `/system_stats` 或 `/object_info` 核验存在。
- 模型效果结论须基于真实生成结果，不可用前就夸。

## 6. 环境闸门（强制）

MCP 未配通（无 `get_system_stats` 返回 GPU/版本/显存 或 `/system_stats` 证据）前，任何成员不得声称"已生成图像/视频"。

## 7. 数字纪律（实测，否则写「待实测」）

> 典型错误：凭印象断言「某档显存只能上某档」。这类数字没有普适性——同一模型在不同分辨率、采样步数、批大小下差异很大，**写进工作流之前必须实测**。

- **任何性能 / 规格数字必须实测或注明出处**：显存占用、生成耗时、分辨率上限、模型体积、并发数等，一律以 `/system_stats`、`/object_info`、`/history` 真实返回或官方文档为准。
- **实测不了就写「待实测」并给实测步骤**：绝不凭记忆/经验编造。例：`"该模型在此显存下的档位——待实测：先 /system_stats 取显存，再跑 512/1024 对照"`。
- 范围数字（"支持到 X 分辨率"）同理：给出实测条件或标注待实测，禁止无依据断言。
- 🔴 **单次采样 ≠ 固定值**：显存空闲、耗时这类随系统负载波动的量，必须报**实测区间 + 采样时刻**（例：`3.23–3.73 GiB，21:58–22:16 间多次 /system_stats`）。写「约 3.8 GiB（交接时实测）」这类单点数值，下游会当常数用，出错时无法归因。

## 8. 红线（一票否决级，全团适用）

- 无真实结果不得编造/声称已生成。
- 工作流只有 API 格式可执行，UI 格式须先转换。
- 不替用户下载大模型；引用模型先核验存在。
- `COMFY_URL` 等凭证走钥匙串、不落明文。
- 本地 GPU 受限、大图/视频耗时占显存——失败先查日志再决定，不无脑重试。
- 🔴 **数字未实测也未标注「待实测」而凭记忆编造** → 一票否决。

> 红线解释权归对应领域成员，最终仲裁归主理人（凯尔）。

## 9. 做不到什么（全团边界，对外必须说清）

- **不能替代用户的本地环境**：引擎、GPU/VRAM、模型权重在用户侧，控制层不随包。环境不通时只能出设计/文档。
- **不保证出图 / 不保证效果**：不承诺「一定出得来 / 一定好看 / 一定能商用」。只保证「真实跑出来的 + 可溯源」。
- **不替用户下载大模型**：checkpoint / LoRA / ControlNet 一律自备。
- **不判审美与商用合规**：画质好坏、版权与商用范围归用户与法务。
- **不改用户全局 IDE / MCP 配置**：须用户明确点头。
- **不保证跨机可迁移**：换机器、换 ComfyUI 版本、换 torch 后端需重新核验节点与模型。
- **不承诺逐字节复现**：同 seed 跨后端可能有像素级差异，未重跑比 sha256 前不下「完全相同」结论。

> 用户要求越界时：**当场点名哪一段做不到 + 卡在哪 + 替代路径是什么**，不许含糊应下再拖。

## 10. 排错归因纪律

> 常见误判：把「curl 报 `upstream connect failed`」直接归因为本机代理拦截——**真因往往是 ComfyUI 尚未开始监听**。绕代理（`--noproxy '*'`）能跑通可能只是巧合。

- **先验证服务是否在监听，再怀疑网络层**：查端口用哪条命令见 §11 的三平台表（macOS `lsof -nP -iTCP:8188 -sTCP:LISTEN`；部分环境禁用 `ps`）。
- **归因必须能被一条命令证伪**：说不出「哪条命令能证明是我也不是它」，就写「待查」，不要写结论。
- **一条错误前提会污染全线**：前提卡/交接文档里的每条环境断言，**自己先实测**再写给别人。

## 11. 平台相关命令的三平台等价写法（权威出处）

本包不在任何一处假定买家是 macOS。下表是**唯一权威写法**，其他文件里出现同类命令时引用本节，不再重复抄三份。

| 用途 | macOS | Windows | Linux |
|---|---|---|---|
| 查端口是否在监听 | `lsof -nP -iTCP:8188 -sTCP:LISTEN` | `netstat -ano \| findstr 8188` | `ss -ltnp \| grep 8188` |
| 算文件 SHA-256 | `shasum -a 256 <文件>` | `certutil -hashfile <文件> SHA256` | `sha256sum <文件>` |
| 看进程 | `ps aux` | `tasklist` | `ps aux` |

> **为什么统一写 `127.0.0.1` 而不写主机名形式**：部分系统会把主机名先解析到 IPv6（`::1`），于是出现「端口明明开着却连不上」。点分 IP 没有这个歧义。
> 上游文档里的默认值用的是主机名写法，两者指向同一台本机服务。
> 连不上时优先显式写点分 IP（`127.0.0.1:8188`）再排查。
> Windows 的 `findstr`、`certutil`、`tasklist` 与 Linux 的 `ss` 为各平台内置工具，无需额外安装。
> 这三行的等价关系**未在本机实测**（本机是 macOS，见交付报告的证据边界）；买家在任何平台上跑一次即可自证。

## 12. 长任务的超时与中断（权威出处）

**超时建议值**：先实测一次同类任务的耗时 T（用 `/history` 条目的起止时间算），再把等待上限设为 **max(3×T, 60 秒)**。

- **依据**：上游 `comfyui-easy-mcp` 的 `POLL_TIMEOUT` 默认 60 秒、可调范围 1–300 秒，`POLL_INTERVAL` 默认 1.0 秒（见其 README 环境变量表，链接见 §1）。本包不写死秒数——买家硬件差异是数量级级别的，写死就是编数字；3× 的余量覆盖队列等待与首次模型加载。
- 单图实测超过 60 秒 → 按上游范围上调 `POLL_TIMEOUT`，不要靠无限等。

**中断与清理**（生成卡住时按序做）：

1. 看队列里到底有什么：`GET /queue`（或 MCP `get_queue_status`）。
2. 只停当前这张：`POST /interrupt`（或 MCP `cancel_current`；上游支持带 `prompt_id` 精确中断）。
3. 把排队的全清掉：`POST /queue`，body `{"clear": true}`（或 MCP `clear_queue`）。
4. 清完重跑前先 `get_system_stats` 确认服务还活着——中断后显存释放需要时间。

> 上述 REST 端点存在于 ComfyUI 上游源码（/interrupt 与 /queue 的 clear 分支，可在上游仓库检索到），MCP 工具名来自上游 README；链接见 §1。

## 13. 能力核验台账（v1.2.0，2026-11-03 核）

全包能力声明的唯一台账：每个能力「按来源分档」，没验过的不许当能跑。证据级：`[实测]` 可复现命令 ｜ `[外核]` URL+访问日期 ｜ `[待核验]`。

| 能力 / 名称 | 证据级 | 依据 | 结论 |
|---|---|---|---|
| 原生 REST（`/system_stats`、`/object_info`、`/prompt`、`/history/{id}`、`/view`、`/ws`、`/queue`、`/interrupt`） | [实测] | 2026-11-03 起本机 ComfyUI 0.41.0 实跑：`/prompt` 提交 + `/history` 轮询出图（探针卡见 `comfyui-hardware-audit`） | 可用 |
| 987 个节点类目（视频/音频/3D/训练/实用视觉各族） | [实测] | `/object_info` 全量拉取 2026-11-03，987 类清单留档 | 节点存在；**接线**仍以 `get_node_info` / `validate_workflow` 校验为准 |
| MCP 工具名 30 个（`get_system_stats`、`list_models`、`run_workflow`、`execute_workflow`、`get_result_image`、`build_wan_video_workflow` 等） | [外核] | 上游仓库 IO-AtelierTech/comfyui-mcp README，2026-11-03 访问 | 名单成立；本机当日未 `tools/list` 实测 |
| MCP 桥启动（uvx 拉 comfyui-easy-mcp） | [实测·失败] | 2026-11-03 四次尝试全炸（默认 mcp 2.x 报 FastMCP 改名；钉 mcp<2 后 register_all_tools 报 pydantic schema 错） | 现状跑不起来，排障记入 `comfyui-mcp-bridge` |
| 模型族 Wan / HunyuanVideo / Hunyuan3D / ACE-Step / MiniMax Music / SAM | [实测·节点名印证族]（小版本号另标） | 节点名（`Wan22*`、`HunyuanVideo15*`、`Hunyuan3Dv2*`、`EmptyAceStep1.5LatentAudio`、`EmptyMiniMaxMusic3LatentAudio`、`SAM3_*`） | 族成立；小版本号：Hunyuan3D 2.0/2.1、ACE-Step 1.5 `[外核·https://docs.comfy.org/tutorials/3d/hunyuan3D-2 · https://docs.comfy.org/zh/tutorials/audio/ace-step/ace-step-v1 （2026-11-03 访问）]`；Wan 2.2 / HunyuanVideo 1.5 / MiniMax Music 3 / SAM 3 / LTX 2.5 的**小版本号** `[待核验]`（节点名只到族） |
| 本机已装权重：SD1.5 v1-5-pruned-emaonly.safetensors | [实测] | 目录盘点 + 探针出图成功 | 当前唯一「当场能跑」的生成权重 |
| 打标 / caption（WD14、BLIP 类） | [待核验] | `/object_info` 987 类中无 caption/tagger 节点 | 缺口如实告知；装 custom node 后以 `refresh_nodes` + `/object_info` 复验再启用 |
| 量化加载节点（GGUF 系） | [待核验] | 以现场 `/object_info` 为准 | 不预写节点名，现场查了再写 |
| 硬件档位表（X GB 能/不能跑什么） | **禁用** | 机制红线（见 `comfyui-hardware-audit`） | 全包 0 引用；一律改走审计→探针→动态清单 |
<!-- 维护提示：不要把上游文件名用反引号包起来——本包用反引号标注包内文件引用，上游文件名不是包内文件。 -->
