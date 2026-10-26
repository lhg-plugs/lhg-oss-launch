> **⚠️ 诚实声明：本插件不编造任何数据（star 数/用户量/下载量/排名/性能数字）；所有数字必须有真实来源，否则审计规则（OL-TRUTH-*）与 commit 硬门会拦截。**

<!-- About 简介（推送后填写到仓库 About 栏）：
开源冷启动专家：README→launch 素材→一键成片指引 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-oss-launch
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, open-source, launch, readme -->

# lhg-oss-launch：开源冷启动专家

> **一句话介绍**：开源项目发布前一站式准备——项目信息挖掘 → README（含 GEO 答案块）→ launch 素材（X 推文串/Show HN/PH 描述/演示文案）→ 一键成片指引，49 条发布前自检把虚构数据拦在发布前。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-oss-launch
> /plugin install lhg-oss-launch@lhg-plugs
> ```

**诚实声明（再说一遍）**：本插件所有素材中的数字必须有真实来源；"已有 10000+ stars"这类写法会被审计标为 blocker、commit 时被 hook 拦截。证据不足就诚实标注"待补充"，不许编。

## 它是什么

`lhg-oss-launch` 是一个 Claude Code 插件（plugin 为主、skill 为辅），专为"项目做完了、不知道怎么推出去"的开发者设计：

- **4 个命令**（小白入口）：`oss-launch` 一键全流程（挖掘→README→素材→成片指引→自检）→ `oss-readme` README 生成/改写 → `oss-assets` launch 素材生成 → `oss-audit` 发布前自检
- **4 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：项目信息挖掘、README 编写、launch 素材、发布前自检
- **3 个专家 agent**：README 撰写专家、launch 文案专家、发布评审（一票否决制）
- **1 个硬门 hook**：git commit 前扫描虚构数据（stars/下载量数字）与占位符，命中则拦截（可一键豁免，不骚扰）
- **49 条确定性自查规则**：README 章节 10、许可 5、链接 8、坏链模式 6、演示 4、诚实 8、结构 6、发布节奏 2，纯 Python、零第三方依赖，5 秒出结果

工作流：`oss-launch`（挖掘→README→素材→成片指引）→ `oss-audit`（查一遍），也可以单独用 `oss-readme` 只改 README。

## 4 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-oss-launch:oss-launch` | 冷启动一键生成：挖掘→README→launch 素材→成片指引→自检 | `/lhg-oss-launch:oss-launch ./my-project` |
| `/lhg-oss-launch:oss-readme` | README 生成/改写：GEO 答案块 + 必备章节 | `/lhg-oss-launch:oss-readme ./my-project --lang zh` |
| `/lhg-oss-launch:oss-assets` | launch 素材：X 推文串/HN 帖子/PH 描述/演示文案 | `/lhg-oss-launch:oss-assets ./launch-brief.json` |
| `/lhg-oss-launch:oss-audit` | 发布前自检（脚本 + 人工评审清单） | `/lhg-oss-launch:oss-audit ./my-project` |

## 自查说明

自查 = 确定性脚本（机器）+ 人工评审清单（人）：

1. 先跑 `scripts/audit/oss_launch_audit.py`（49 条规则），零 AI 成本；
2. 发现分三级：**blocker**（必须修：缺安装/用法/许可章节、无 LICENSE、空链接、坏链、example 占位、虚构 stars/下载量；commit 时 hook 会拦截虚构数据）、**warning**（修或写豁免理由）、**nit**（顺手修）；
3. 再按 `lhg-ol-audit` skill 第 4 节人工清单过一遍脚本抓不到的（首屏 30 秒测试、演示是否当前版本、安装命令是否真跑通过）。

blocker 清零才算做完；为清零改规则算作弊，不许。

## 目录结构

```
lhg-oss-launch/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 4 个命令：oss-launch / oss-readme / oss-assets / oss-audit
├── skills/                  # 4 个平台中立 skill（信息挖掘/README/素材/自检）
├── agents/                  # 3 个专家 agent（readme-writer / launch-copywriter / release-reviewer）
├── hooks/                   # 1 个硬门（commit 前虚构数据检查）+ 豁免说明
├── scripts/audit/           # 49 条确定性自查规则（零第三方依赖）
├── fixtures/                # 冒烟测试用例（坏/好对照）
├── smoke_test.py            # 一键冒烟测试
├── ATTRIBUTION.md           # 灵感来源与许可声明
└── LICENSE                  # MIT
```

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你的开源项目做完了，想发 Show HN / Product Hunt / X，但不知道从哪下手时 → 用 `/lhg-oss-launch:oss-launch`，一句话出一套发布装备
- 你的 README 还是"标题+一句话+TODO"时 → `oss-readme` 按 GEO 答案块重写，首屏 30 秒讲清价值
- 你要发 v1.0，想准备推文串和演示视频文案时 → `oss-assets` 一次出 4 份差异化素材 + 90 秒分镜
- 你怕发布时被评论区打假（数据/截图/链接）时 → `oss-audit` 先自己查一遍

**什么时候不用：**

- 项目还没跑通、连一句话都说不清"它是干嘛的"时 → 先回去把项目做完，本插件不负责"无中生有"
- 你想靠"编数据"冷启动（假 star 数、假用户量）→ 本插件会拦截这种内容，请换条路
- 你需要的是视频渲染本身 → 本插件只出文案、分镜与成片指引，渲染请用 brag 等视频工具

**风险点诚实说明：**

- **自检通过 ≠ 发布成功**：49 条规则只检查"发布就绪度"，star 数和流量靠产品本身 + 运气
- **发布时间建议是经验值**：X/HN/PH 的发布时间建议来自公开经验，不是保证
- **演示视频本插件不渲染**：只出 90 秒分镜与口播文案，成片需另行制作
- **benchmark 方法要自己跑**：插件只给"可复现"的方法模板，数字要你自己跑出来

## lhg-plugs 插件矩阵

| 插件 | 一句话 | 安装 |
|---|---|---|
| [lhg-video-edit](https://github.com/lhg-plugs/lhg-video-edit) | 一句话把口播素材剪成爆款短视频 | `/plugin install lhg-video-edit@lhg-plugs` |
| [lhg-fullstack](https://github.com/lhg-plugs/lhg-fullstack) | 小白一句话 → 高质量全栈应用 | `/plugin install lhg-fullstack@lhg-plugs` |
| [lhg-pet-care](https://github.com/lhg-plugs/lhg-pet-care) | 宠物养护专家：档案→时间表→健康 checklist 一键生成 | `/plugin install lhg-pet-care@lhg-plugs` |
| [lhg-oss-launch](https://github.com/lhg-plugs/lhg-oss-launch) | 开源冷启动专家：README→launch 素材→一键成片指引 | `/plugin install lhg-oss-launch@lhg-plugs` |

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（JSON 合法、skill/command/agent 完整性、49 条规则、fixtures 命中、hooks 行为）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-oss-launch/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 抖音：搜「刘老师讲AI实战」
- 微信：lhgsmsw
