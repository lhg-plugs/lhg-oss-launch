---
description: README 生成/改写：GEO 答案块（H1→一句话→安装命令）+ 必备章节（安装/用法/许可/演示），输出可直接发布的 README.md。
argument-hint: [项目目录] [--lang zh|en]
---

# /lhg-oss-launch:oss-readme —— README 生成

用户输入在 `$ARGUMENTS` 中：`[项目目录] [--lang zh|en]`，缺省中文。

加载 `lhg-ol-info`（先有 launch-brief.json）与 `lhg-ol-readme` skill 执行；可分派给 `readme-writer` agent。

> **诚实声明**：不编造数据；徽章只在有真实 CI/版本时加。

## 流程

1. **读项目**：代码结构、安装方式、现有文档，提炼一句话价值主张（见 lhg-ol-info）。
2. **写 README**：按 lhg-ol-readme 第 3 节结构输出——H1 → 一句话介绍 → 一键安装代码块 → 演示（截图/GIF/视频+时长标注）→ 功能 → 安装 → 用法 → 许可 → 贡献 → 路线图。
3. **配套文件**：检查 LICENSE 文件存在且类型与 README 声明一致；给 topics 关键词建议。
4. **自检**：跑 `oss-audit`，blocker 清零。

## 反模式
- 首屏只有标题和徽章，没有一句话介绍和安装命令。
- 演示视频无时长标注；example.com 占位链接未替换。
