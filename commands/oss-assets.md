---
description: launch 素材生成：X 推文串 / Show HN 帖子 / Product Hunt 描述 / 演示文案+分镜，多平台差异化，输出到 launch/ 目录。
argument-hint: [launch-brief.json 路径]
---

# /lhg-oss-launch:oss-assets —— launch 素材生成

用户输入在 `$ARGUMENTS` 中：`[launch-brief.json 路径]`。

加载 `lhg-ol-info`（读 brief）与 `lhg-ol-assets` skill 执行；可分派给 `launch-copywriter` agent。

> **诚实声明**：素材中不出现无依据的数字（star/用户量/排名）；绝对化宣称必须给限定条件。

## 流程

1. **读 brief**：一句话价值主张、目标用户、痛点、差异化、证据清单。
2. **写 4 份素材**（输出到 `launch/`）：
   - `x-thread.md`：X 推文串（首推钩子 + 3~5 推展开 + 收尾 CTA），中文语境可直接用中文
   - `hn-post.md`：Show HN 帖子（标题 + 正文：做了什么/为什么做/技术点/求反馈）
   - `ph-launch.md`：Product Hunt 描述（tagline 60 字符内 + 首评话术）
   - `demo-script.md`：演示文案 + 分镜（90 秒三段式：痛点 15s → 演示 60s → 收尾 15s）
3. **差异化检查**：4 份素材首段不许完全相同；各按平台调性改写。
4. **成片指引**：基于 demo-script.md 输出一键成片指引（封面帧/字幕/配文模板）。

## 输出要求
- 每份素材顶部标注建议发布时间（如"北京时间周二~周四上午"）。
- 无证据支撑的效果数字一律不写。
