#!/usr/bin/env python3
"""由 data/services.json 生成 README.md 的目录区块（不改动 README 其他部分）。

用法: python scripts/build_readme.py           # 写回 README.md
      python scripts/build_readme.py --check   # 只 diff，CI 里防止忘记生成
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "services.json"
README = ROOT / "README.md"

START = "<!-- CATALOG:START -->"
END = "<!-- CATALOG:END -->"

CATEGORY_ORDER = [
    "出行和生活",
    "办公和协作",
    "笔记阅读网盘",
    "搜索内容企业数据",
    "设计创作",
    "支付金融",
    "云和开发",
    "其他",
]

AUTH_LABEL = {
    "none": "免登录",
    "api_key": "Key",
    "oauth": "OAuth",
    "account": "账号授权",
    "enterprise": "企业认证",
    "unknown": "待确认",
}

BADGE = {True: "✅", False: "—"}


def load() -> list[dict]:
    services = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(services, list):
        raise SystemExit("services.json 必须是数组")
    ids = [s["id"] for s in services]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit(f"id 重复: {sorted(dup)}")
    return services


def kind_cell(s: dict) -> str:
    mcp = s.get("mcp", {})
    skill = s.get("skill", {})
    parts = []
    if mcp.get("available"):
        t = mcp.get("type", "unknown")
        parts.append(f"MCP<sub>{t}</sub>" if t != "unknown" else "MCP")
    if skill.get("available"):
        parts.append("Skill")
    return " · ".join(parts) or "—"


def link_cell(s: dict) -> str:
    """优先指向 MCP 文档，其次 Skill，最后官方首页。"""
    mcp = s.get("mcp", {})
    skill = s.get("skill", {})
    for url in (mcp.get("url"), skill.get("url"), s.get("docs")):
        if url:
            return f"[文档]({url})"
    return "—"


def render(services: list[dict]) -> str:
    today = dt.date.today().isoformat()
    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    for cat in CATEGORY_ORDER:
        grouped[cat] = []
    for s in services:
        grouped.setdefault(s["category"], []).append(s)

    total = len(services)
    n_mcp = sum(1 for s in services if s.get("mcp", {}).get("available"))
    n_skill = sum(1 for s in services if s.get("skill", {}).get("available"))
    n_remote = sum(
        1 for s in services if s.get("mcp", {}).get("type") in ("remote", "both")
    )

    out: list[str] = []
    out.append(START)
    out.append("")
    out.append(
        f"> 数据快照：共 **{total}** 个国内服务 · **{n_mcp}** 个提供官方 MCP "
        f"（其中 {n_remote} 个远程端点）· **{n_skill}** 个提供官方 Skill。"
        f"  最后重建：{today}"
    )
    out.append(">")
    out.append("> 图例：✅ 已开放 · — 未开放 · Key/OAuth/账号授权 = 调用前需要的前置凭据。")
    out.append("")

    for cat, items in grouped.items():
        if not items:
            continue
        out.append(f"### {cat}")
        out.append("")
        out.append("| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |")
        out.append("| --- | --- | --- | --- | --- |")
        for s in sorted(items, key=lambda x: x["name"]):
            notes = s.get("notes") or ""
            if s.get("client_required"):
                notes = f"需{s['client_required']}；" + notes
            out.append(
                "| {name} | {kind} | {auth} | {link} | {notes} |".format(
                    name=s["name"],
                    kind=kind_cell(s),
                    auth=AUTH_LABEL.get(s.get("auth", "unknown"), "待确认"),
                    link=link_cell(s),
                    notes=notes.replace("|", "/"),
                )
            )
        out.append("")

    out.append(END)
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比对，不写入")
    args = ap.parse_args()

    block = render(load())
    text = README.read_text(encoding="utf-8")

    if START not in text or END not in text:
        raise SystemExit(f"README.md 缺少 {START} / {END} 标记")

    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    if args.check:
        if text != head + block + tail:
            print("README.md 目录区块与 services.json 不同步，请运行 python scripts/build_readme.py")
            return 1
        print("README.md 与 services.json 同步")
        return 0

    README.write_text(head + block + tail, encoding="utf-8")
    print(f"README.md 已重建：{len(load())} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
