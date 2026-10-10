---
description: 开源冷启动一键生成：项目信息挖掘→README（含 GEO 答案块）→launch 素材（推文/帖子/演示文案）→一键成片指引，全程诚实无虚构数据。
argument-hint: [项目目录或一句话介绍]
---

# /lhg-oss-launch:oss-launch —— 开源冷启动一键生成

用户输入在 `$ARGUMENTS` 中：`[项目目录或一句话介绍]`。

全程加载 `lhg-ol-info`、`lhg-ol-readme`、`lhg-ol-assets` 指导；各环节可分派给 `readme-writer` / `launch-copywriter` / `release-reviewer` agent。最后必跑 `oss-audit`。

> **诚实声明**：本命令输出不编造任何数据（star 数/用户量/下载量/排名）；所有数字必须有真实来源，否则审计与 hook 会拦截。

## 流程

### 1. 项目信息挖掘（见 lhg-ol-info）
- 读项目代码与现有文档，输出 `launch-brief.json`：一句话价值主张、目标用户、解决的痛点、差异化、"为什么是现在"、证据清单（真实截图/演示/数据）。
- 证据不足 → 诚实标注"待补充"，不许编。

### 2. README 生成（见 lhg-ol-readme）
- 结构：H1 → 一句话介绍 → 一键安装代码块（GEO 答案块）→ 演示 → 功能 → 安装 → 用法 → 许可。
- 徽章只在有真实 CI/版本时加；演示视频标注时长；LICENSE 文件必须存在且类型一致。

### 3. launch 素材（见 lhg-ol-assets）
- 输出到 `launch/` 目录：`x-thread.md`（X 推文串）、`hn-post.md`（Show HN 帖子）、`ph-launch.md`（Product Hunt 描述）、`demo-script.md`（演示文案+分镜）。
- 多平台文案差异化，不许同一文案复制粘贴发所有平台。

### 4. 一键成片指引
- 基于 demo-script.md 给出成片指引：90 秒三段式（痛点 15s → 演示 60s → 收尾 15s）、封面帧要求、配文模板。
- 本插件只出指引与文案，不做视频渲染（渲染可用 brag 等工具另行完成）。

### 5. 发布前自检（见 lhg-ol-audit）
- 跑 `scripts/audit/oss_launch_audit.py`，blocker 清零才算做完。
- commit 时 hook 会拦截虚构数据与占位符。

## 输出文件
- `launch-brief.json` / `README.md` / `launch/*.md`（4 份素材）/ `audit-report.md`
