#!/usr/bin/env python3
"""lhg-oss-launch 确定性发布前审计：49 条规则，零第三方依赖。

扫描目标目录（README*.md、LICENSE*、package.json、launch 素材），
输出 JSON 与人类可读报告；有 blocker 时以 exit code 2 退出。

用法：
    python3 oss_launch_audit.py --target <目录> [--format json|text] [--fail-on blocker|warning|nit]

规则文案均为本项目原创（详见仓库 ATTRIBUTION.md）。
诚实原则：本脚本重点检查"虚构数据/坏链/缺失章节"三类发布前必查项。
"""

import argparse
import json
import os
import re
import sys

VERSION = "1.0.0"
TOOL = "lhg-oss-launch/oss-audit"

SKIP_DIRS = {".git", "__pycache__", "node_modules", "dist", "build"}

# ---------------------------------------------------------------- 数据模型
class Finding:
    __slots__ = ("rule_id", "severity", "category", "title", "file", "line", "snippet", "detail")

    def __init__(self, rule_id, severity, category, title, file, line, snippet, detail):
        self.rule_id = rule_id
        self.severity = severity
        self.category = category
        self.title = title
        self.file = file
        self.line = line
        self.snippet = snippet
        self.detail = detail

    def to_dict(self):
        return {
            "rule_id": self.rule_id, "severity": self.severity,
            "category": self.category, "title": self.title,
            "file": self.file, "line": self.line,
            "snippet": self.snippet, "detail": self.detail,
        }


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        return None
    except OSError:
        return ""


def collect(target):
    readmes, licenses, packages, assets = [], [], [], []
    has_gitignore = False
    has_github = False
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if ".github" in dirs:
            has_github = True
        for f in files:
            p = os.path.join(root, f)
            fl = f.lower()
            if fl == "readme.md" or (fl.startswith("readme") and fl.endswith(".md")):
                readmes.append(p)
            elif fl.startswith("license"):
                licenses.append(p)
            elif fl == "package.json":
                packages.append(p)
            elif fl == ".gitignore" or f == ".gitignore":
                has_gitignore = True
            if "launch" in root.lower() or "assets" in root.lower():
                if fl.endswith(".md") and p not in readmes:
                    assets.append(p)
    return {"readmes": sorted(readmes), "licenses": sorted(licenses),
            "packages": sorted(packages), "assets": sorted(assets),
            "has_gitignore": has_gitignore, "has_github": has_github}


# ---------------------------------------------------------------- 规则注册表
RULES = []
_RULE_BY_ID = {}


def rule(rule_id, severity, category, title, detail):
    def deco(fn):
        r = {"id": rule_id, "severity": severity, "category": category,
             "title": title, "detail": detail}
        _RULE_BY_ID[rule_id] = r
        r["check"] = fn
        RULES.append(r)
        return fn
    return deco


def _mk(rule_id, path, line, snippet):
    r = _RULE_BY_ID[rule_id]
    return Finding(r["id"], r["severity"], r["category"], r["title"],
                   path, line, snippet[:160], r["detail"])


def _lines(text):
    return text.split("\n")


def _headings(text):
    return [(i, ln) for i, ln in enumerate(_lines(text), 1)
            if re.match(r"^#{1,3}\s+", ln)]


def _section_text(text, start_line):
    """取从 start_line 开始到下一个同级/高级标题前的内容。"""
    out = []
    for i, ln in enumerate(_lines(text), 1):
        if i <= start_line:
            continue
        if re.match(r"^#{1,3}\s+", ln):
            break
        out.append(ln)
    return "\n".join(out)


# ---------------------------------------------------------------- 自建表
INSTALL_H_RE = re.compile(r"^#{1,3}\s*(安装|install|快速开始|quick\s*start|getting\s+started)", re.I | re.M)
USAGE_H_RE = re.compile(r"^#{1,3}\s*(用法|使用|usage|examples?|示例)", re.I | re.M)
LICENSE_H_RE = re.compile(r"^#{1,3}\s*(许可|license|许可证)", re.I | re.M)
FEATURE_H_RE = re.compile(r"^#{1,3}\s*(功能|features?|特性)", re.I | re.M)
CONTRIB_H_RE = re.compile(r"^#{1,3}\s*(贡献|contributing)", re.I | re.M)
DEMO_H_RE = re.compile(r"^#{1,3}\s*(演示|demo|screenshot)", re.I | re.M)

LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]*)\)")
VIDEO_RE = re.compile(r"youtu\.?be|vimeo|\.mp4", re.I)
DURATION_RE = re.compile(r"[（(]\s*(?:时长\s*)?(\d+)\s*[:：]\s*(\d{1,2})\s*[)）]|时长\s*(\d+)\s*分")
LICENSE_KW_RE = re.compile(r"MIT|Apache-2\.0|Apache 2\.0|GPL-?3\.0|BSD|版权所有|Permission is hereby granted", re.I)

TRUTH_STARS_RE = re.compile(r"\d[\d,]*\s*\+?\s*(stars|star 数|颗星|个 star)", re.I)
TRUTH_COUNT_RE = re.compile(r"(下载量|用户数|downloads|users)\s*(突破|达到|超过|已有)?\s*\d", re.I)
TRUTH_ABS_RE = re.compile(r"最快|第一|唯一|最好|首个|最强")
TRUTH_RANK_RE = re.compile(r"Product Hunt|PH\s*#\s*1|热榜|HN\s*首页|hacker news", re.I)
TRUTH_PRAISE_RE = re.compile(r"好评如潮|广受好评|用户一致好评")
TRUTH_USEDBY_RE = re.compile(r"被.+公司采用|used by|trusted by", re.I)
TRUTH_BENCH_RE = re.compile(r"提升\s*\d+\s*%|快\s*\d+\s*倍|\d+\s*%\s*提升")
TRUTH_MONEY_RE = re.compile(r"融资|估值|收入\s*\d|ARR|营收")

PLACEHOLDER_RE = re.compile(r"example\.(com|org|net)|your-username|YOUR_REPO|yourname", re.I)
LOCALHOST_RE = re.compile(r"localhost|127\.0\.0\.1")
TODO_RE = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b")


# ---- OL-README 必备章节类 ----
@rule("OL-README-001", "blocker", "README", "缺安装章节",
      "README 缺少 安装/Install/快速开始 章节，用户不知道怎么装。")
def _r001(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not INSTALL_H_RE.search(text):
            out.append(_mk("OL-README-001", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-002", "blocker", "README", "缺用法章节",
      "README 缺少 用法/Usage/示例 章节，用户不知道怎么用。")
def _r002(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not USAGE_H_RE.search(text):
            out.append(_mk("OL-README-002", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-003", "blocker", "README", "缺许可章节",
      "README 缺少 许可/License 章节。")
def _r003(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not LICENSE_H_RE.search(text):
            out.append(_mk("OL-README-003", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-004", "warning", "README", "缺演示材料",
      "README 无截图/GIF/演示视频，转化率会打折。")
def _r004(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not (re.search(r"!\[", text) or VIDEO_RE.search(text)
                or re.search(r"\.gif", text, re.I)):
            out.append(_mk("OL-README-004", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-005", "warning", "README", "缺功能列表",
      "README 缺少 功能/Features 章节，访客 30 秒看不到价值。")
def _r005(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not FEATURE_H_RE.search(text):
            out.append(_mk("OL-README-005", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-006", "warning", "README", "首屏无一句话介绍",
      "H1 之后 8 行内无 ≥10 字的 plain 介绍句，首屏转化弱。")
def _r006(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        lines = _lines(text)
        h1 = next((i for i, ln in enumerate(lines) if re.match(r"^#\s+", ln)), None)
        if h1 is None:
            out.append(_mk("OL-README-006", p, 1, "无 H1 标题"))
            continue
        ok = False
        seen = 0
        for ln in lines[h1 + 1:]:
            s = ln.strip()
            if not s:
                continue
            seen += 1
            if seen > 8:
                break
            s2 = re.sub(r"!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|`[^`]*`", "", s).strip()
            s2 = re.sub(r"^>\s*", "", s2).strip()
            if len(s2) >= 10 and not s2.startswith(("#", "-", "*", "|")):
                ok = True
                break
        if not ok:
            out.append(_mk("OL-README-006", p, h1 + 1, lines[h1] if h1 < len(lines) else ""))


@rule("OL-README-007", "nit", "README", "缺贡献指南",
      "README 缺少 贡献/Contributing 章节或链接。")
def _r007(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not CONTRIB_H_RE.search(text):
            out.append(_mk("OL-README-007", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-008", "warning", "README", "徽章链接坏",
      "徽章图片用了非 https 链接。")
def _r008(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in enumerate(_lines(text), 1):
            for m in re.finditer(r"!\[.*?\]\((.*?)\)", ln):
                url = m.group(1).strip()
                if url.startswith("http://"):
                    out.append(_mk("OL-README-008", p, i, ln))


@rule("OL-README-009", "nit", "README", "无版本号声明",
      "README 未声明当前版本号（如 v1.0.0）。")
def _r009(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not re.search(r"v\d+\.\d+|版本\s*[：:]\s*\d|version\s*[：:]\s*\d", text, re.I):
            out.append(_mk("OL-README-009", p, 1, _lines(text)[0] if text else ""))


@rule("OL-README-010", "nit", "README", "长文档无目录",
      "README 超过 300 行但无目录/TOC。")
def _r010(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if len(_lines(text)) > 300 and not re.search(r"^#{1,3}\s*(目录|TOC|Contents)", text, re.M | re.I):
            out.append(_mk("OL-README-010", p, 1, "共 %d 行" % len(_lines(text))))


# ---- OL-LIC 许可类 ----
@rule("OL-LIC-001", "blocker", "许可", "LICENSE 文件缺失",
      "仓库根目录无 LICENSE 文件。")
def _l001(ctx, out):
    if not ctx["licenses"]:
        out.append(_mk("OL-LIC-001", ctx.get("target", ""), 0, "未找到 LICENSE*"))


@rule("OL-LIC-002", "blocker", "许可", "LICENSE 文件为空",
      "LICENSE 文件存在但内容为空。")
def _l002(ctx, out):
    for p in ctx["licenses"]:
        text = read_text(p)
        if text is not None and not text.strip():
            out.append(_mk("OL-LIC-002", p, 1, "文件为空"))


@rule("OL-LIC-003", "warning", "许可", "LICENSE 内容无法识别",
      "LICENSE 内容不含常见许可关键词（MIT/Apache/GPL/版权所有），请确认。")
def _l003(ctx, out):
    for p in ctx["licenses"]:
        text = read_text(p)
        if text and text.strip() and not LICENSE_KW_RE.search(text):
            out.append(_mk("OL-LIC-003", p, 1, text.strip()[:80]))


@rule("OL-LIC-004", "warning", "许可", "README 许可声明与 LICENSE 不一致",
      "README 许可章节声明的类型与 LICENSE 文件不一致。")
def _l004(ctx, out):
    if not (ctx["readmes"] and ctx["licenses"]):
        return
    lic_text = read_text(ctx["licenses"][0]) or ""
    m_lic = re.search(r"MIT|Apache-?2\.0|GPL-?3\.0|BSD", lic_text, re.I)
    for p in ctx["readmes"]:
        text = read_text(p) or ""
        for i, ln in _headings(text):
            if LICENSE_H_RE.match(ln):
                sec = _section_text(text, i)
                m_readme = re.search(r"MIT|Apache-?2\.0|GPL-?3\.0|BSD", sec, re.I)
                if m_lic and m_readme and m_lic.group(0).upper() != m_readme.group(0).upper():
                    out.append(_mk("OL-LIC-004", p, i, ln))


@rule("OL-LIC-005", "warning", "许可", "package.json 缺 license 字段",
      "package.json 存在但无 license 字段。")
def _l005(ctx, out):
    for p in ctx["packages"]:
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        if not d.get("license"):
            out.append(_mk("OL-LIC-005", p, 1, "无 license 字段"))


# ---- OL-LINK 链接类 ----
def _each_link(text):
    for i, ln in enumerate(_lines(text), 1):
        for m in LINK_RE.finditer(ln):
            yield i, ln, m.group(1) == "!", m.group(2), m.group(3).strip()


@rule("OL-LINK-001", "blocker", "链接", "空链接",
      "出现 [文本]() 空链接。")
def _k001(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if not url:
                out.append(_mk("OL-LINK-001", p, i, ln))


@rule("OL-LINK-002", "warning", "链接", "http 非 https 外链",
      "外链用了 http 而非 https。")
def _k002(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if url.startswith("http://"):
                out.append(_mk("OL-LINK-002", p, i, ln))


@rule("OL-LINK-003", "blocker", "链接", "相对链接目标不存在",
      "相对路径链接指向的文件不存在。")
def _k003(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        base = os.path.dirname(p)
        for i, ln, is_img, label, url in _each_link(text):
            if not url or url.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(base, url.split("#")[0]))
            if not os.path.exists(target):
                out.append(_mk("OL-LINK-003", p, i, ln))


@rule("OL-LINK-004", "warning", "链接", "锚点无对应标题",
      "站内锚点链接 #xxx 无对应标题。")
def _k004(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        anchors = set()
        for _, ln in _headings(text):
            t = re.sub(r"^#{1,3}\s*", "", ln).strip().lower()
            anchors.add(re.sub(r"[^\w\u4e00-\u9fff\- ]", "", t).replace(" ", "-"))
        for i, ln, is_img, label, url in _each_link(text):
            if url.startswith("#") and len(url) > 1:
                a = url[1:].lower()
                if a not in anchors and a.replace("-", "") not in {x.replace("-", "") for x in anchors}:
                    out.append(_mk("OL-LINK-004", p, i, ln))


@rule("OL-LINK-005", "nit", "链接", "图片缺 alt 文本",
      "图片语法 ![]() 缺 alt 文本，影响可访问性。")
def _k005(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if is_img and not label.strip():
                out.append(_mk("OL-LINK-005", p, i, ln))


@rule("OL-LINK-006", "warning", "链接", "同一 URL 重复 ≥5 次",
      "同一 URL 在文档中出现 5 次以上，疑似链接堆砌。")
def _k006(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        counts = {}
        for i, ln, is_img, label, url in _each_link(text):
            if url:
                counts[url] = counts.get(url, 0) + 1
        for url, c in counts.items():
            if c >= 5:
                out.append(_mk("OL-LINK-006", p, 1, "%s 出现 %d 次" % (url[:60], c)))


@rule("OL-LINK-007", "warning", "链接", "链接含空格未编码",
      "URL 中含空格，应编码为 %20 或改用短横线。")
def _k007(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if " " in url:
                out.append(_mk("OL-LINK-007", p, i, ln))


@rule("OL-LINK-008", "nit", "链接", "无意义链接文本",
      "链接文本为'点击这里/click here/这里'，无信息量。")
def _k008(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if label.strip().lower() in ("点击这里", "click here", "here", "这里"):
                out.append(_mk("OL-LINK-008", p, i, ln))


# ---- OL-BADLINK 坏链模式类 ----
@rule("OL-BADLINK-001", "blocker", "坏链", "example 占位链接",
      "出现 example.com/org/net 占位链接，发布前必须替换。")
def _b001(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in enumerate(_lines(text), 1):
            if PLACEHOLDER_RE.search(ln) and "example.com" in ln.lower():
                out.append(_mk("OL-BADLINK-001", p, i, ln))


@rule("OL-BADLINK-002", "warning", "坏链", "localhost 链接",
      "出现 localhost/127.0.0.1 链接，外人打不开。")
def _b002(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in enumerate(_lines(text), 1):
            if LOCALHOST_RE.search(ln):
                out.append(_mk("OL-BADLINK-002", p, i, ln))


@rule("OL-BADLINK-003", "warning", "坏链", "TODO/FIXME 残留",
      "文档残留 TODO/FIXME/XXX。")
def _b003(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in enumerate(_lines(text), 1):
            if TODO_RE.search(ln):
                out.append(_mk("OL-BADLINK-003", p, i, ln))


@rule("OL-BADLINK-004", "blocker", "坏链", "本地图片/附件不存在",
      "引用的本地图片或附件文件不存在。")
def _b004(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        base = os.path.dirname(p)
        for i, ln, is_img, label, url in _each_link(text):
            if not url or url.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if is_img or re.search(r"\.(png|jpg|jpeg|gif|svg|mp4|pdf|zip)$", url, re.I):
                target = os.path.normpath(os.path.join(base, url.split("#")[0]))
                if not os.path.exists(target):
                    out.append(_mk("OL-BADLINK-004", p, i, ln))


@rule("OL-BADLINK-005", "blocker", "坏链", "your-username 占位",
      "出现 your-username/YOUR_REPO 占位符，发布前必须替换为真实地址。")
def _b005(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in enumerate(_lines(text), 1):
            if re.search(r"your-username|YOUR_REPO", ln, re.I):
                out.append(_mk("OL-BADLINK-005", p, i, ln))


@rule("OL-BADLINK-006", "warning", "坏链", "coming soon 占位",
      "出现 coming soon/即将上线 占位文案，发布前确认是否保留。")
def _b006(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in enumerate(_lines(text), 1):
            if re.search(r"coming soon|即将上线|敬请期待", ln, re.I):
                out.append(_mk("OL-BADLINK-006", p, i, ln))


# ---- OL-DEMO 演示类 ----
@rule("OL-DEMO-001", "warning", "演示", "视频无时长标注",
      "演示视频链接无时长标注（如（时长 1:32）），访客不知道要投入多久。")
def _d001(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if VIDEO_RE.search(url or "") and not DURATION_RE.search(ln):
                out.append(_mk("OL-DEMO-001", p, i, ln))


@rule("OL-DEMO-002", "nit", "演示", "GIF 无大小说明",
      "GIF 演示无文件大小/时长说明。")
def _d002(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        lines = _lines(text)
        for i, ln, is_img, label, url in _each_link(text):
            if (url or "").lower().endswith(".gif"):
                near = "\n".join(lines[max(0, i - 3):min(len(lines), i + 2)])
                if not re.search(r"\d+\s*(MB|KB)|时长|循环", near):
                    out.append(_mk("OL-DEMO-002", p, i, ln))


@rule("OL-DEMO-003", "warning", "演示", "演示视频超 3 分钟",
      "演示视频时长超过 3 分钟，建议剪到 90 秒内或分段。")
def _d003(ctx, out):
    for p in ctx["readmes"] + ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln, is_img, label, url in _each_link(text):
            if VIDEO_RE.search(url or ""):
                m = DURATION_RE.search(ln)
                if m:
                    mins = int(m.group(1) or m.group(3) or 0)
                    if mins >= 3:
                        out.append(_mk("OL-DEMO-003", p, i, ln))


@rule("OL-DEMO-004", "warning", "演示", "演示章节只有视频无说明",
      "演示章节只有视频链接，无一句话文字说明。")
def _d004(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        for i, ln in _headings(text):
            if DEMO_H_RE.match(ln):
                sec = _section_text(text, i)
                text_lines = []
                for l in sec.split("\n"):
                    s = l.strip()
                    if not s:
                        continue
                    s2 = re.sub(r"!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|`[^`]*`", "", s).strip()
                    if len(s2) >= 10:
                        text_lines.append(s2)
                if VIDEO_RE.search(sec) and len(text_lines) < 1:
                    out.append(_mk("OL-DEMO-004", p, i, ln))


# ---- OL-TRUTH 虚构数据类 ----
def _truth_rule(rule_id, severity, rx, title, detail):
    @rule(rule_id, severity, "诚实", title, detail)
    def _t(ctx, out, _rx=rx, _rid=rule_id):
        for p in ctx["readmes"] + ctx["assets"]:
            text = read_text(p)
            if text is None:
                continue
            for i, ln in enumerate(_lines(text), 1):
                if _rx.search(ln):
                    out.append(_mk(_rid, p, i, ln))
    _t.__name__ = rule_id.lower()
    return _t


_truth_rule("OL-TRUTH-001", "blocker", TRUTH_STARS_RE, "stars 数字无依据",
            "出现 stars 数量声明，发布前必须删掉或给出真实来源。")
_truth_rule("OL-TRUTH-002", "blocker", TRUTH_COUNT_RE, "下载量/用户数无依据",
            "出现下载量/用户数声明，发布前必须删掉或给出真实来源。")
_truth_rule("OL-TRUTH-003", "warning", TRUTH_ABS_RE, "绝对化宣称",
            "出现'最快/第一/唯一/最好'绝对化宣称，请给出限定条件或证据。")
_truth_rule("OL-TRUTH-004", "warning", TRUTH_RANK_RE, "排名声明无时间",
            "出现 Product Hunt/热榜/HN 排名声明，请标注时间届次或删除。")
_truth_rule("OL-TRUTH-005", "warning", TRUTH_PRAISE_RE, "好评宣称无来源",
            "出现'好评如潮'类宣称但无来源。")
_truth_rule("OL-TRUTH-006", "warning", TRUTH_USEDBY_RE, "被采用宣称无来源",
            "出现'被XX公司采用/used by'但无来源。")
_truth_rule("OL-TRUTH-007", "warning", TRUTH_BENCH_RE, "性能数字无复现方式",
            "出现性能提升数字但无 benchmark 复现方式。")
_truth_rule("OL-TRUTH-008", "warning", TRUTH_MONEY_RE, "融资/收入数字",
            "出现融资/估值/收入数字，请确认可公开。")


# ---- OL-STRUCT 结构类 ----
@rule("OL-STRUCT-001", "warning", "结构", "无 GEO 答案块",
      "README 前 40 行无'一句话介绍 + 安装代码块'答案块，AI 搜索与访客转化弱。")
def _s001(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        head = "\n".join(_lines(text)[:40])
        has_pitch = bool(re.search(r"^>\s*.{10,}", head, re.M))
        has_install = bool(re.search(r"```(bash|sh|shell)", head))
        if not (has_pitch and has_install):
            out.append(_mk("OL-STRUCT-001", p, 1, _lines(text)[0] if text else ""))


@rule("OL-STRUCT-002", "nit", "结构", "无 .github 目录",
      "仓库无 .github 目录（issue/PR 模板），建议补上。")
def _s002(ctx, out):
    if not ctx["has_github"]:
        out.append(_mk("OL-STRUCT-002", ctx.get("target", ""), 0, "无 .github 目录"))


@rule("OL-STRUCT-003", "nit", "结构", "无 topics 建议",
      "README 未给出 GitHub topics 建议关键词。")
def _s003(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not re.search(r"topics", text, re.I):
            out.append(_mk("OL-STRUCT-003", p, 1, _lines(text)[0] if text else ""))


@rule("OL-STRUCT-004", "warning", "结构", "无 .gitignore",
      "仓库根目录无 .gitignore。")
def _s004(ctx, out):
    if not ctx["has_gitignore"]:
        out.append(_mk("OL-STRUCT-004", ctx.get("target", ""), 0, "无 .gitignore"))


@rule("OL-STRUCT-005", "warning", "结构", "README 版本与 package.json 不一致",
      "README 声明的版本与 package.json 不一致。")
def _s005(ctx, out):
    vers = {}
    for p in ctx["packages"]:
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
            if d.get("version"):
                vers[p] = d["version"]
        except Exception:
            continue
    if not vers:
        return
    for p in ctx["readmes"]:
        text = read_text(p) or ""
        m = re.search(r"v(\d+\.\d+\.\d+)", text)
        if m:
            for pp, v in vers.items():
                if m.group(1) != v:
                    out.append(_mk("OL-STRUCT-005", p, 1,
                                   "README v%s vs package.json %s" % (m.group(1), v)))


@rule("OL-STRUCT-006", "nit", "结构", "无路线图",
      "README 无路线图/Roadmap，访客不知道项目往哪走。")
def _s006(ctx, out):
    for p in ctx["readmes"]:
        text = read_text(p)
        if text is None:
            continue
        if not re.search(r"路线图|Roadmap", text, re.I):
            out.append(_mk("OL-STRUCT-006", p, 1, _lines(text)[0] if text else ""))


# ---- OL-PUB 发布节奏类 ----
@rule("OL-PUB-001", "nit", "发布", "launch 素材无发布时间建议",
      "launch 素材目录存在，但无发布时间/排期建议。")
def _pub1(ctx, out):
    for p in ctx["assets"]:
        text = read_text(p)
        if text is None:
            continue
        if not re.search(r"发布时间|排期|schedule|周二|周三|上午|北京时间", text, re.I):
            out.append(_mk("OL-PUB-001", p, 1, _lines(text)[0] if text else ""))


@rule("OL-PUB-002", "warning", "发布", "多平台文案无差异化",
      "多个平台的 launch 文案首段完全相同，建议按平台调性改写。")
def _pub2(ctx, out):
    heads = []
    for p in ctx["assets"]:
        text = read_text(p)
        if text:
            heads.append((p, text[:200].strip()))
    for i in range(len(heads)):
        for j in range(i + 1, len(heads)):
            if heads[i][1] and heads[i][1] == heads[j][1]:
                out.append(_mk("OL-PUB-002", heads[j][0], 1, "与 %s 首段相同"
                               % os.path.basename(heads[i][0])))


# ---------------------------------------------------------------- 主流程
def run_audit(target):
    ctx = collect(target)
    ctx["target"] = os.path.abspath(target)
    findings = []
    for r in RULES:
        try:
            r["check"](ctx, findings)
        except Exception as e:  # 单条规则失败不影响整体：fail-open
            findings.append(Finding(r["id"], "nit", r["category"],
                                    "规则执行异常（已跳过）", "", 0, "", str(e)))
    findings.sort(key=lambda f: ({"blocker": 0, "warning": 1, "nit": 2}[f.severity], f.rule_id))
    sev_count = {"blocker": 0, "warning": 0, "nit": 0}
    for f in findings:
        sev_count[f.severity] += 1
    summary = {
        "tool": TOOL, "version": VERSION, "target": os.path.abspath(target),
        "rules_run": len(RULES),
        "blocker": sev_count["blocker"], "warning": sev_count["warning"],
        "nit": sev_count["nit"], "total": len(findings),
    }
    return {"summary": summary, "findings": [f.to_dict() for f in findings]}


def format_text(report):
    s = report["summary"]
    lines = [
        "lhg-oss-launch 审计报告 v%s" % s["version"],
        "目标：%s  规则：%d 条" % (s["target"], s["rules_run"]),
        "blocker=%d warning=%d nit=%d" % (s["blocker"], s["warning"], s["nit"]),
        "-" * 60,
    ]
    for f in report["findings"]:
        lines.append("[%s][%s] %s:%s %s" % (
            f["severity"], f["rule_id"], os.path.basename(f["file"]) or "(仓库)",
            f["line"], f["title"]))
        if f["snippet"]:
            lines.append("    %s" % f["snippet"][:120])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--format", default="text", choices=["json", "text"])
    ap.add_argument("--fail-on", default="blocker", choices=["blocker", "warning", "nit"])
    args = ap.parse_args()
    report = run_audit(args.target)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text(report))
    order = {"blocker": 0, "warning": 1, "nit": 2}
    thresh = order[args.fail_on]
    bad = any(order[f["severity"]] <= thresh for f in report["findings"])
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
