---
name: comfyui-mcp-bridge
description: "MCP 桥接：接线方式、真实工具名、启动排障与连接证明。"
whenToUse: "ComfyUI 出图 / 工作流 / 批量 / 排障 / 参数 / 视频音频 3D 训练 时"
license: MIT
---

# ComfyUI MCP 桥接（comfyui-mcp-bridge）

> **DSH 适配**：本技能来自 WorkBuddy 专家团版。「成员/派单/回执」= 你的分步执行与交付记录，「本团」= 你。单 agent 场景下纪律不变。

教用户把 **ComfyUI MCP 桥**接进 IDE 并连通自检。这是 comfyui-studio 的「首选路径」——让对话能直接驱动本机 ComfyUI。

## 1. 前置：本机 ComfyUI 已跑

- `http://127.0.0.1:8188` 是 ComfyUI 本体的默认监听地址（桥连哪由 `COMFY_URL` 决定，见下面两条）。先确认服务在线（见 Step 3 自检）。
- 服务未起 → 提示用户启动 ComfyUI（`python main.py` 或桌面端），确认端口未被占用再配桥。

## 2. 两条桥路径

### 路径 A：comfyui-mcp（推荐首选，工具最全）
- 启动：`uvx comfyui-easy-mcp`（IO-AtelierTech）。
- 上游：PyPI https://pypi.org/project/comfyui-easy-mcp/ ｜仓库 https://github.com/IO-AtelierTech/comfyui-mcp （环境变量表与工具清单以上游 README 为准）。
- 指向：
  - **上游默认**：`http://localhost:8188`（可用环境变量 `COMFY_URL` 覆盖）
  - **本包建议**：显式写 `http://127.0.0.1:8188`（理由见 comfyui-sop §11）
- 工具：`get_system_stats` / `list_nodes` / `run_workflow` / `execute_workflow` / `get_result_image` 等 20+。
- 优点：节点目录、工作流执行、结果取图一体化，最贴近本团标准流程。

### 路径 B：comfyui-mcp-server（轻量备选，多 fork）
- 启动：社区多 fork 实现，HTTP workflow-backed。
  - **上游默认**：`COMFY_URL` = `http://localhost:8188`
  - **本包建议**：显式写 `http://127.0.0.1:8188`（理由见 comfyui-sop §11）
- ⚠️ **无唯一权威仓库可引用（查不到）**：该项目多个 fork 并存，本团不为任何一个背书。买家要用这条路，让他自行确认装的是哪个 fork，并以那个 fork 自己的文档为准。
- 工具：偏 workflow-backed（提交/查询/取结果），节点级操作较少。
- 适用：只想最快把"跑一个已存工作流"接进对话。

### 可照抄的配置样例（路径 A）

下面这段是**合法 JSON**，可直接粘进 MCP 客户端的配置文件。它只做一件事：让客户端用 `uvx` 拉起 `comfyui-easy-mcp`，并告诉桥 ComfyUI 在哪。

```json
{
  "mcpServers": {
    "comfyui": {
      "command": "uvx",
      "args": ["comfyui-easy-mcp"],
      "env": {
        "COMFY_URL": "http://127.0.0.1:8188"
      }
    }
  }
}
```

**改哪个文件**（按客户端对号入座，别自己猜）：

| 客户端 | 文件 | 说明 |
|---|---|---|
| Claude Code（项目级） | 项目根目录 `.mcp.json` | 可提交进版本控制，团队共享 |
| Claude Code（用户级/本地级） | `~/.claude.json` | 跨项目可用；本地级按项目路径隔离 |
| Claude Desktop / Cursor 等 | 各自的 `mcpServers` 配置 JSON | 外层键同样是 `mcpServers`，条目形状与上面一致 |

> 客户端配置文件的位置以各客户端官方文档为准（Claude Code 的说明见 https://code.claude.com/docs/en/mcp ）。
> 用命令行加也行：`claude mcp add-json comfyui '<上面那条条目，去掉最外层 mcpServers>'`——注意传给 `add-json` 的是**里面那条**，不是带外层的整块。

**改哪几个字段**：

| 字段 | 要不要改 | 说明 |
|---|---|---|
| `env.COMFY_URL` | **通常要改** | ComfyUI 不在本机 8188 时改这里；端口没被占用就别动 |
| `command` / `args` | 一般不动 | 已按上游 README 的启动方式写好 |
| 其余 `env` | 可选 | 上游还支持 `POLL_TIMEOUT`（默认 60 秒，范围 1–300）、`COMFY_WORKFLOWS_DIR` 等，用不到就不写 |

配完不是结束——**必须过第 3 节的连通自检**，拿到 `get_system_stats` 的真实返回才算通。

## 3. 连通自检（闸门，必须过）

- 让 agent 调 `get_system_stats`（或直连 `GET /system_stats`）。
- 返回 JSON 含 `system`/`devices`（GPU 型号、显存已用/总量、ComfyUI 版本）即连通。
- 拿不到该证据前，禁止任何「生成 / 读取结果」动作。

## 4. 排连清单（按顺序查，别跳步）

- **第一步永远是「服务在不在」**：查端口三条命令按平台选——macOS `lsof -nP -iTCP:8188 -sTCP:LISTEN`｜Windows `netstat -ano | findstr 8188`｜Linux `ss -ltnp | grep 8188`（部分环境禁用 `ps`，所以别只依赖 `ps`）+ `curl -s $COMFY_URL/system_stats`。有监听、有 JSON = 服务在线，问题不在 ComfyUI。三平台等价写法的权威出处是 comfyui-sop §11。
- **`curl` 报 `upstream connect failed` / `Connection refused` 时不要先怪代理**：注意——本机 `HTTP_PROXY` 存在，但回环地址不受影响，真因**通常**是 ComfyUI 尚未开始监听。先查进程，再查网络层。
- `--noproxy '*'` 可作无害防守写法，但**它不是判据**：不带它也能通，就别把它写进「必须绕过代理」这类断言。
- 8188 无监听 → 让用户启动 ComfyUI（`python main.py` 或桌面端），确认端口未被占用、`--listen` 参数正确。
- 桥启动报错 → 确认 `uvx` 可用、`COMFY_URL` 指向无误；换路径 B 兜底。
- 偶发断连 → 重启 ComfyUI / 重起桥，本团所有路径都需"断连自检 + 重启指引"。
- **跑很久不出图**：桥这一层的等待上限是环境变量 `POLL_TIMEOUT`（上游默认 60 秒，范围 1–300）。卡住时怎么停、怎么清队列，见 comfyui-sop §12（超时与中断的权威出处）。

## 5. 判定标准（怎么算「桥配通了」）

- ✅ 过：`get_system_stats`（或 `GET /system_stats`）返回含 `system.comfyui_version` + `devices[].vram_total` 的 JSON，**原文贴出**。
- ✅ 过：`list_nodes`（或 `/object_info`）返回非空节点字典。
- ✅ 过：MCP 配置在用户确认后写入，且**告知改了哪个文件、改了什么**。
- ❌ 不过：只证明「uvx 命令能启动」就宣布连通——启动 ≠ 连上 ComfyUI。
- ❌ 不过：拿 `curl` 能通但 `get_system_stats` 调不到，却报「桥已就绪」。

## 6. 做不到什么（边界）

- **不保证**桥在用户环境一定能装上：`uvx` 缺失、Python 版本、企业代理/防火墙都可能挡住，装不上就退回原生 REST 路径。
- **不能替代**用户的安装决定：改 IDE / MCP 全局配置必须用户明确点头，agent 不擅自改。
- **不保证**桥与 ComfyUI 版本兼容：桥是社区项目，ComfyUI 大版本升级后工具名可能变，需重新核验工具表。
- **不负责**网络层故障（DNS、企业代理策略）——只给诊断命令，不承诺修好。
- **不判**生成质量：桥只负责「接得通」，生成与交付归下游成员。

## 7. 真实工具（连通后由其他成员使用）

`run_workflow` / `execute_workflow` / `get_result_image` / `list_nodes` / `get_system_stats`

> 本技能只管「接得通 + 证明通」，不管设计节点。设计交给 comfyui-workflow-architect。

## 8. 2026-11-03 实测排障记录（诚实档：当天桥是坏的）

在本机 Mac（uvx）按 README 拉 comfyui-easy-mcp，**四次尝试全失败**（错误原文摘要）：

1. `uvx comfyui-easy-mcp` → 包里没有同名可执行：「An executable named `comfyui-easy-mcp` is not provided…The following executables are available: - comfyui-mcp-server」→ 用 `uvx --from comfyui-easy-mcp comfyui-mcp-server`。
2. 改对名字后 import 炸：「No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed…」→ 建议钉 `mcp<2`。
3. 钉 `mcp<2` 后走到 register_all_tools 炸：「pydantic.errors.PydanticSchemaGenerationError: … <class 'mcp.server.fastmcp.utilities.types.Image'>」。
4. 再钉 `pydantic<2.11` 同样 schema 错。

**结论（如实告知，别假装开箱即用）**：2026-11-03 当日该桥在本机起不来，属上游 mcp 库版本漂移；工具名清单改走上游 README（`[外核]`，30 个，见 `comfyui-sop` §13 台账）。用户侧动作：等上游更新后复跑本节四步；或自行钉旧版组合继续试。桥通不通，判定标准仍按 §5——通了才叫通。
