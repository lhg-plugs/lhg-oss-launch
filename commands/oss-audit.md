---
description: 发布前自检：49 条确定性规则（README 章节/LICENSE/链接/坏链/演示时长/虚构数据），blocker 清零才允许发布。
argument-hint: [仓库目录] [--fail-on blocker]
---

# /lhg-oss-launch:oss-audit —— 发布前自检

用户输入在 `$ARGUMENTS` 中：`[仓库目录] [--fail-on 级别]`，缺省 blocker。

先跑脚本、再过人工清单（见 `lhg-ol-audit` skill）。

## 流程

### 1. 确定性脚本（零 AI 成本先行）
```bash
python3 scripts/audit/oss_launch_audit.py --target <仓库目录> --format text
```
- 49 条规则分 8 类：README 章节 10、许可 5、链接 8、坏链模式 6、演示 4、诚实 8、结构 6、发布节奏 2。
- 发现分三级：**blocker**（必须修：缺安装/用法/许可章节、无 LICENSE、空链接、坏链、example 占位、虚构 stars/下载量）、**warning**（修或写豁免理由）、**nit**（顺手修）。
- blocker 清零才算做完；为清零改规则算作弊，不许。

### 2. 人工评审清单（脚本抓不到的）
- 首屏 30 秒测试：找个没见过项目的人，看 README 首屏能否说出"这是什么、给谁用、怎么装"？
- 演示材料真实吗？截图/GIF 是否为当前版本？
- 所有数字（star/下载/性能）都有真实来源吗？
- 4 份 launch 素材的调性真的不一样吗？还是换了个标题而已？

### 3. 输出
- 审计报告（blocker/warning/nit 清单 + 修复建议），存 `audit-report.md`。
