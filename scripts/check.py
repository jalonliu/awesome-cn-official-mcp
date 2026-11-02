#!/usr/bin/env python3
"""巡检 data/services.json：结构校验 + 官方链接可达性检查。

用法:
    python scripts/check.py                # 全量巡检，写回 last_checked / status
    python scripts/check.py --no-network   # 只做结构校验（本地/CI 用）
    python scripts/check.py --report out.md

退出码 0 表示没有 hard failure（链接失效只告警，不阻断）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "services.json"
SCHEMA = ROOT / "data" / "schema.json"

UA = "Mozilla/5.0 (compatible; awesome-cn-official-mcp-checker/1.0)"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CATEGORIES = {
    "出行和生活",
    "办公和协作",
    "笔记阅读网盘",
    "搜索内容企业数据",
    "设计创作",
    "支付金融",
    "云和开发",
    "其他",
}
AUTH_VALUES = {"none", "api_key", "oauth", "account", "enterprise", "unknown"}
MCP_TYPES = {"stdio", "remote", "both", "unknown"}


def structural_checks(services: list[dict]) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for s in services:
        sid = s.get("id", "<missing>")
        if not ID_RE.match(str(sid)):
            errs.append(f"[schema] id 非法: {sid}")
        if sid in seen:
            errs.append(f"[schema] id 重复: {sid}")
        seen.add(sid)
        for field in ("name", "category", "docs", "verified_at"):
            if field not in s:
                errs.append(f"[schema] {sid} 缺字段 {field}")
        if s.get("category") not in CATEGORIES:
            errs.append(f"[schema] {sid} category 非法: {s.get('category')}")
        if s.get("auth") and s["auth"] not in AUTH_VALUES:
            errs.append(f"[schema] {sid} auth 非法: {s['auth']}")
        if s.get("official") is not True:
            errs.append(f"[policy] {sid} 非官方条目（official != true），本仓库只收官方")
        mcp = s.get("mcp", {})
        skill = s.get("skill", {})
        if not mcp.get("available") and not skill.get("available"):
            errs.append(f"[policy] {sid} 既无 MCP 也无 Skill")
        if mcp.get("available") and mcp.get("type") not in MCP_TYPES:
            errs.append(f"[schema] {sid} mcp.type 非法: {mcp.get('type')}")
        if mcp.get("available") and not (mcp.get("url") or mcp.get("endpoint") or mcp.get("install")):
            errs.append(f"[schema] {sid} 声称有 MCP 但没有 url/endpoint/install")
        if skill.get("available") and not skill.get("url"):
            errs.append(f"[schema] {sid} 声称有 Skill 但没有 url")
        d = s.get("verified_at", "")
        if not DATE_RE.match(str(d)):
            errs.append(f"[schema] {sid} verified_at 不是 YYYY-MM-DD: {d}")
    return errs


def probe(url: str) -> tuple[str, int | None, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:  # noqa: S310 - 只访问清单内官方地址
            return url, r.status, ""
    except urllib.error.HTTPError as e:
        # 401/403/429 通常是反爬或需要登录，不算失效
        return url, e.code, ""
    except Exception as e:  # noqa: BLE001
        return url, None, type(e).__name__ + (f": {e}" if str(e) else "")


def collect_urls(services: list[dict]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for s in services:
        sid = s["id"]
        for key, url in (
            ("docs", s.get("docs")),
            ("mcp.url", (s.get("mcp") or {}).get("url")),
            ("skill.url", (s.get("skill") or {}).get("url")),
        ):
            if url and url.startswith("http"):
                pairs.append((f"{sid}:{key}", url))
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--report", default="")
    ap.add_argument("--write", action="store_true", help="把 last_checked/status 写回 services.json")
    args = ap.parse_args()

    services = json.loads(DATA.read_text(encoding="utf-8"))
    errs = structural_checks(services)
    today = dt.date.today().isoformat()

    dead: list[str] = []
    soft: list[str] = []
    if not args.no_network:
        pairs = collect_urls(services)
        print(f"巡检 {len(pairs)} 个链接 …")
        with ThreadPoolExecutor(max_workers=12) as ex:
            results = list(ex.map(lambda p: probe(p[1]), pairs))
        status_by_url = {}
        for (label, url), (_, code, err) in zip(pairs, results):
            status_by_url[url] = code
            if code is None:
                dead.append(f"- ❌ {label} → {url} （{err}）")
            elif code >= 400 and code not in (401, 403, 405, 429):
                dead.append(f"- ❌ {label} → {url} （HTTP {code}）")
            elif code in (401, 403, 429):
                soft.append(f"- ⚠️ {label} → {url} （HTTP {code}，可能是反爬/需登录）")

        if args.write:
            for s in services:
                s["last_checked"] = today
                code = status_by_url.get(s.get("docs", ""))
                if code is None or (isinstance(code, int) and code >= 400 and code not in (401, 403, 405, 429)):
                    s["status"] = "unreachable"
                else:
                    s["status"] = "active"
            DATA.write_text(
                json.dumps(services, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"已写回 last_checked={today}")

    report = ["# 巡检报告", "", f"- 日期：{today}", f"- 条目数：{len(services)}"]
    report.append(f"- 结构/策略错误：{len(errs)}")
    report.append(f"- 失效链接：{len(dead)}")
    report.append(f"- 可疑链接：{len(soft)}")
    report.append("")
    if errs:
        report += ["## 结构/策略错误", ""] + [f"- {e}" for e in errs] + [""]
    if dead:
        report += ["## 失效链接", ""] + dead + [""]
    if soft:
        report += ["## 可疑链接（需人工确认）", ""] + soft + [""]
    if not errs and not dead and not soft:
        report.append("全部通过 ✅")

    text = "\n".join(report)
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
        print(f"报告写入 {args.report}")
    print(text)

    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
