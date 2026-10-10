#!/usr/bin/env python3
"""lhg-oss-launch 硬门：git commit 前检查虚构数据。

触发：PreToolUse / Bash。脚本先判断本次 Bash 命令是否为 git commit，
不是则 0 开销直接放行；是则扫描项目目录的 README 与 launch 素材，
发现"无依据的 stars/下载量/用户数"数字声明则拦截。

逃生方式（按推荐度排序）：
  1. 删掉虚构数字，或补上真实来源（推荐）。
  2. 紧急情况：LHG_OL_HOOKS_OFF=1 git commit -m "..."（单次豁免本次 hook）。
  3. /plugin disable lhg-oss-launch（整个插件停用，hooks 不再触发）。

设计原则：脚本内部出错时 fail-open 直接放行，不因插件自身故障骚扰用户；
真正的门禁在 /lhg-oss-launch:oss-audit。零第三方依赖。
"""

import json
import os
import re
import sys

COMMIT_RE = re.compile(r"(^|[;&|])\s*git\s+.*\bcommit\b")

FABRICATE_RES = [
    (re.compile(r"\d[\d,]*\s*\+?\s*(stars|star 数|颗星)", re.I), "stars 数量声明无依据"),
    (re.compile(r"(下载量|用户数|downloads|users)\s*(突破|达到|超过|已有)?\s*\d", re.I), "下载量/用户数声明无依据"),
    (re.compile(r"your-username|YOUR_REPO", re.I), "your-username 占位符未替换"),
]


def main() -> int:
    # 逃生开关
    if os.environ.get("LHG_OL_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # 输入解析失败：fail-open

    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""

    # 非 git commit：快速放行
    if not COMMIT_RE.search(command):
        return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    hits = []
    try:
        for root, dirs, files in os.walk(project_dir):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules"}]
            for f in files:
                if not f.lower().endswith(".md"):
                    continue
                p = os.path.join(root, f)
                try:
                    with open(p, encoding="utf-8") as fh:
                        text = fh.read()
                except Exception:
                    continue
                for i, ln in enumerate(text.split("\n"), 1):
                    for rx, title in FABRICATE_RES:
                        if rx.search(ln):
                            hits.append((p, i, title, ln.strip()[:80]))
    except Exception:
        return 0  # 扫描自身出错：fail-open

    if not hits:
        return 0

    lines = [
        "提交被 lhg-oss-launch 硬门拦截：发现 %d 处疑似虚构数据/占位符（发布后会被打假）。"
        % len(hits),
        "",
    ]
    for p, i, title, snippet in hits[:10]:
        lines.append("- [%s] %s:%d %s" % (title, os.path.basename(p), i, snippet))
    if len(hits) > 10:
        lines.append("…另有 %d 处，完整清单请跑 /lhg-oss-launch:oss-audit" % (len(hits) - 10))
    lines += [
        "",
        "修复方式：删掉虚构数字，或补上真实来源；占位符替换为真实地址。",
        "紧急豁免（单次）：LHG_OL_HOOKS_OFF=1 git commit",
    ]

    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "\n".join(lines),
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
