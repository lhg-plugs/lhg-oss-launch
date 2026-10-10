# 灵感来源与致谢（Attribution）

本插件的**方法论灵感**来自以下公开资料的高层思路，**所有实现代码、检测规则与文案均为原创**，未复制任何第三方的原文案与代码。

| 来源 | 说明 | 出处 | 借鉴了什么思路 |
|---|---|---|---|
| latent-spaces/brag | 开源 Claude Code 插件，MIT 许可 | https://github.com/latent-spaces/brag（2026-10-11 访问时仓库主体；另有多个 fork 镜像） | "一句话把项目变成可分享的 launch 视频（含配乐/动效/分享文案）"的**模式思路**：launch 素材应该"一句话输入、多形态输出"。本插件的 `/oss-launch:oss-assets` 命令与一键成片指引受此启发。**未复制其文案、代码与视频生成实现** |
| jaskirat1616/grok-skills `skills/viral-launch` | 开源 Agent Skill（许可见其仓库） | https://github.com/jaskirat1616/grok-skills/blob/HEAD/skills/viral-launch/SKILL.md | "先审视项目→一句话定义 launch 角度→仓库就绪→做素材→设计传播环→定义指标→保持诚实"七步工作流的**高层框架思路**。**未复制其文案** |
| oleg-koval/agent-skills `viral-launch` | 开源 Agent Skill（许可见其仓库） | https://github.com/oleg-koval/agent-skills | 同上，viral-launch 多平台适配版本的高层思路。**未复制其文案** |

## 声明

1. **借鉴思路，实现与文案均为原创**：以上来源的具体文案、原文表述、代码均未被复制。本插件的 skill 方法论文案、审计规则、命令流程、hook 脚本均为独立撰写。
2. **诚实红线**：本插件不编造任何数据、star 数、用户量、排名；所有 launch 素材中的数字必须有真实来源，否则审计规则（OL-TRUTH-*）会拦截。
3. **未核实项**：未逐一核实各来源仓库的许可文本细节；引用链接以 2026-10-11 访问时为准。
4. **不编造**：本文件未编造任何数据、star 数、排名。

## 本插件自身的许可

本插件原创部分采用 MIT 许可（见 `LICENSE` 文件），版权所有：刘洪光（https://github.com/lhg-skills）。
