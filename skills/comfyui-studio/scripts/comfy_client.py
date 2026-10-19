#!/usr/bin/env python3
"""
comfy_client.py — 零依赖 ComfyUI HTTP 客户端（仅标准库）。

用法：
  python3 comfy_client.py doctor [--host 127.0.0.1:8188]
  python3 comfy_client.py models [--host ...]
  python3 comfy_client.py objects [--filter KSampler] [--host ...]
  python3 comfy_client.py submit --workflow wf.json [--wait] [--outdir DIR] [--timeout 600] [--host ...]
  python3 comfy_client.py status <prompt_id> [--host ...]
  python3 comfy_client.py download <prompt_id> --outdir DIR [--host ...]
  python3 comfy_client.py queue [--host ...]
  python3 comfy_client.py interrupt [--host ...]

工作流必须是 API 格式（Save (API Format) 导出的 JSON）。UI 格式会明确报错。
退出码：0 成功；2 连接失败；3 工作流格式错误；4 生成失败/超时。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

DEFAULT_HOST = os.environ.get("COMFYUI_HOST", "127.0.0.1:8188")


def fail(message: str, code: int):
    print(message, file=sys.stderr)
    raise SystemExit(code)


def base_url(host: str) -> str:
    host = host.strip()
    if not host.startswith(("http://", "https://")):
        host = "http://" + host
    return host.rstrip("/")


def request(base: str, path: str, method: str = "GET", payload=None, timeout: float = 30.0):
    url = base + path
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        fail(f"❌ HTTP {e.code} {url}\n{detail}", 2)
    except urllib.error.URLError as e:
        fail(
            f"❌ 连不上 {base}（{e.reason}）\n"
            "   先确认 ComfyUI 已启动、端口正确；需要局域网访问时启动加 --listen 0.0.0.0。",
            2,
        )
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.decode("utf-8", "replace")


def human_gb(n) -> str:
    try:
        return f"{float(n) / (1024 ** 3):.1f} GB"
    except (TypeError, ValueError):
        return "?"


def device_summary(stats: dict) -> str:
    devices = stats.get("devices") or []
    if not devices:
        return "device ?"
    d = devices[0]
    parts = []
    if d.get("type"):
        parts.append(str(d["type"]))
    if d.get("name"):
        parts.append(str(d["name"]))
    if d.get("vram_total"):
        parts.append("vram " + human_gb(d["vram_total"]))
    return " · ".join(parts)


def object_info(base: str, name: str | None = None):
    path = "/object_info" + (f"/{urllib.parse.quote(name)}" if name else "")
    return request(base, path, timeout=120)


def input_options(info: dict, node: str, field: str) -> list:
    """Read a combo option list (e.g. checkpoint names) from /object_info."""
    try:
        spec = info[node]["input"]["required"][field]
        values = spec[0]
        return list(values) if isinstance(values, list) else []
    except (KeyError, IndexError, TypeError):
        return []


def cmd_doctor(base: str, args) -> int:
    sys_stats = request(base, "/system_stats") or {}
    queue = request(base, "/queue") or {}
    info = object_info(base) or {}
    system = sys_stats.get("system") or {}
    version = system.get("comfyui_version", "?")
    queued = len(queue.get("queue_running") or []) + len(queue.get("queue_pending") or [])
    ckpts = input_options(info, "CheckpointLoaderSimple", "ckpt_name")
    loras = input_options(info, "LoraLoader", "lora_name")
    print("✅ 服务可达 · ComfyUI", version, "·", device_summary(sys_stats))
    print(f"✅ 队列 {queued} · 节点 {len(info)} · checkpoints {len(ckpts)} · loras {len(loras)}")
    if not ckpts:
        print("⚠️ 没有可用 checkpoint：模型放 models/checkpoints/ 后刷新。")
    if str((sys_stats.get("devices") or [{}])[0].get("type", "")).lower() == "cpu":
        print("⚠️ 当前是 CPU 后端，出图会非常慢；检查 MPS/CUDA 是否可用。")
    return 0


def cmd_models(base: str, args) -> int:
    info = object_info(base) or {}
    ckpts = input_options(info, "CheckpointLoaderSimple", "ckpt_name")
    loras = input_options(info, "LoraLoader", "lora_name")
    print(f"checkpoints ({len(ckpts)}):")
    for c in ckpts or ["（空）"]:
        print("  -", c)
    print(f"\nloras ({len(loras)}):")
    for l in loras[:50] or ["（空）"]:
        print("  -", l)
    if len(loras) > 50:
        print(f"  … 其余 {len(loras) - 50} 个")
    return 0


def cmd_objects(base: str, args) -> int:
    info = object_info(base) or {}
    names = sorted(info)
    if args.filter:
        names = [n for n in names if args.filter.lower() in n.lower()]
    print(f"匹配 {len(names)} 个节点：")
    for n in names[:80]:
        print("  -", n)
    if len(names) > 80:
        print(f"  … 其余 {len(names) - 80} 个，用更精确的 --filter")
    return 0


def load_workflow(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"❌ 工作流不存在: {path}", 3)
    except json.JSONDecodeError as e:
        fail(f"❌ 工作流不是合法 JSON: {e}", 3)
    if isinstance(data, dict) and "nodes" in data and "links" in data:
        fail(
            "❌ 这是 UI 格式工作流。请在 ComfyUI 里用 Save (API Format) 重新导出，"
            "顶层应为 节点id → {class_type, inputs}。",
            3,
        )
    if not isinstance(data, dict) or not data:
        fail("❌ 工作流格式不对：需要顶层对象。", 3)
    for node_id, node in data.items():
        if not isinstance(node, dict) or "class_type" not in node:
            fail(f"❌ 节点 {node_id} 缺少 class_type，不是 API 格式。", 3)
    return data


def cmd_submit(base: str, args) -> int:
    wf = load_workflow(Path(args.workflow))
    client_id = args.client_id or str(uuid.uuid4())
    result = request(base, "/prompt", method="POST", payload={"prompt": wf, "client_id": client_id})
    if not isinstance(result, dict) or "prompt_id" not in result:
        fail(f"❌ 提交失败: {result}", 4)
    pid = result["prompt_id"]
    print(f"✅ 已提交 prompt_id={pid}")
    if result.get("node_errors"):
        print("⚠️ 节点错误:", json.dumps(result["node_errors"], ensure_ascii=False)[:800])
    if not args.wait:
        return 0
    return wait_and_download(base, pid, args.outdir, args.timeout, args.poll)


def wait_and_download(base: str, pid: str, outdir: str | None, timeout: float, poll: float) -> int:
    deadline = time.time() + timeout
    while time.time() < deadline:
        hist = request(base, f"/history/{pid}") or {}
        entry = hist.get(pid) if isinstance(hist, dict) else None
        if entry:
            status = entry.get("status") or {}
            if status.get("status_str") == "error" or status.get("completed") is False:
                print("❌ 生成失败：", json.dumps(status, ensure_ascii=False)[:800])
                return 4
            files = collect_images(entry)
            if files or status.get("completed") is True:
                print(f"✅ 完成，输出 {len(files)} 张")
                if outdir and files:
                    save_images(base, files, Path(outdir))
                return 0
        time.sleep(max(0.5, poll))
    print(f"❌ 超时 {timeout}s，prompt_id={pid} 仍无结果；可用 status 继续查。")
    return 4


def collect_images(entry: dict) -> list:
    images = []
    for node_out in (entry.get("outputs") or {}).values():
        for img in node_out.get("images") or []:
            if img.get("type", "output") == "output":
                images.append(img)
    return images


def save_images(base: str, images: list, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for img in images:
        query = urllib.parse.urlencode({
            "filename": img.get("filename", ""),
            "subfolder": img.get("subfolder", ""),
            "type": img.get("type", "output"),
        })
        dest = outdir / Path(img.get("filename", "image.png")).name
        try:
            with urllib.request.urlopen(f"{base}/view?{query}", timeout=120) as resp:
                dest.write_bytes(resp.read())
            print("🖼️ ", dest)
        except urllib.error.URLError as e:
            print(f"⚠️ 下载失败 {dest}: {e}")


def cmd_status(base: str, args) -> int:
    hist = request(base, f"/history/{args.prompt_id}") or {}
    entry = hist.get(args.prompt_id)
    if not entry:
        print("⏳ 还没有结果（可能仍在队列或已失败）。")
        return 0
    status = entry.get("status") or {}
    print("状态:", status.get("status_str", "?"), "| completed:", status.get("completed"))
    for img in collect_images(entry):
        print("  输出:", img.get("subfolder") or "", img.get("filename"))
    return 0


def cmd_download(base: str, args) -> int:
    hist = request(base, f"/history/{args.prompt_id}") or {}
    entry = hist.get(args.prompt_id)
    if not entry:
        fail("❌ 没有该 prompt_id 的结果。", 4)
    images = collect_images(entry)
    if not images:
        fail("❌ 该任务没有输出图片。", 4)
    save_images(base, images, Path(args.outdir))
    return 0


def cmd_queue(base: str, args) -> int:
    q = request(base, "/queue") or {}
    running = q.get("queue_running") or []
    pending = q.get("queue_pending") or []
    print(f"运行中 {len(running)} · 排队 {len(pending)}")
    for item in running[:5]:
        print("  运行:", item[1] if len(item) > 1 else item)
    return 0


def cmd_interrupt(base: str, args) -> int:
    request(base, "/interrupt", method="POST", payload={})
    print("✅ 已发送中断")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ComfyUI 零依赖客户端")
    ap.add_argument("--host", default=DEFAULT_HOST, help=f"ComfyUI 地址（默认 {DEFAULT_HOST}）")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--host", default=argparse.SUPPRESS, help=f"ComfyUI 地址（默认 {DEFAULT_HOST}）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", parents=[common])
    sub.add_parser("models", parents=[common])
    p_obj = sub.add_parser("objects", parents=[common])
    p_obj.add_argument("--filter", default="")

    p_sub = sub.add_parser("submit", parents=[common])
    p_sub.add_argument("--workflow", required=True)
    p_sub.add_argument("--wait", action="store_true")
    p_sub.add_argument("--outdir", default="")
    p_sub.add_argument("--timeout", type=float, default=600)
    p_sub.add_argument("--poll", type=float, default=1.0)
    p_sub.add_argument("--client-id", default="")

    p_st = sub.add_parser("status", parents=[common])
    p_st.add_argument("prompt_id")
    p_dl = sub.add_parser("download", parents=[common])
    p_dl.add_argument("prompt_id")
    p_dl.add_argument("--outdir", required=True)
    sub.add_parser("queue", parents=[common])
    sub.add_parser("interrupt", parents=[common])

    args = ap.parse_args()
    base = base_url(args.host)
    handlers = {
        "doctor": cmd_doctor,
        "models": cmd_models,
        "objects": cmd_objects,
        "submit": cmd_submit,
        "status": cmd_status,
        "download": cmd_download,
        "queue": cmd_queue,
        "interrupt": cmd_interrupt,
    }
    return handlers[args.cmd](base, args)


if __name__ == "__main__":
    sys.exit(main())
