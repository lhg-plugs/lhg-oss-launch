---
name: lhg-ol-audit
description: 发布前自检方法论：49 条确定性规则分类解读、诚实红线、人工评审清单。适用于开源项目发布前的最后一道检查。
license: MIT
compatibility: 平台中立（Claude Code / 豆包 / Workbuddy 等 agent 平台通用）
metadata:
  version: 1.0.0
  domain: oss-launch
---

# lhg-ol-audit：发布前自检

> **诚实声明**：本 skill 不编造任何数据；自检通过不等于发布一定成功；本 skill 只检查"发布就绪度"，不承诺流量与 star 数。

## 1. 何时使用

- README 与 launch 素材写完、公开发布之前的最后一道检查。
- 收到一个仓库，想快速判断"它发布就绪了吗"时。
- `/lhg-oss-launch:oss-audit` 命令全程按本 skill 执行。

**检查哲学**：机器先行（49 条确定性规则，零 AI 成本），人工补漏（脚本抓不到的 10 项）。blocker 清零才算做完；为清零改规则算作弊。

## 2. 49 条规则分类解读

脚本：`scripts/audit/oss_launch_audit.py`（用法见第 3 节）。规则分 8 类：

### OL-README 章节类（10 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-README-001 | 缺安装章节 | blocker |
| OL-README-002 | 缺用法章节 | blocker |
| OL-README-003 | 缺许可章节 | blocker |
| OL-README-004 | 缺演示材料（截图/GIF/视频） | warning |
| OL-README-005 | 缺功能列表 | warning |
| OL-README-006 | 首屏无一句话介绍（H1 后 8 行内无 ≥10 字介绍句） | warning |
| OL-README-007 | 缺贡献指南 | nit |
| OL-README-008 | 徽章图片用 http 链接 | warning |
| OL-README-009 | 无版本号声明 | nit |
| OL-README-010 | 超 300 行无目录 | nit |

### OL-LIC 许可类（5 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-LIC-001 | LICENSE 文件缺失 | blocker |
| OL-LIC-002 | LICENSE 文件为空 | blocker |
| OL-LIC-003 | LICENSE 内容无法识别 | warning |
| OL-LIC-004 | README 许可声明与 LICENSE 文件不一致 | warning |
| OL-LIC-005 | package.json 缺 license 字段 | warning |

### OL-LINK 链接类（8 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-LINK-001 | 空链接 `[文本]()` | blocker |
| OL-LINK-002 | http 非 https 外链 | warning |
| OL-LINK-003 | 相对链接目标文件不存在 | blocker |
| OL-LINK-004 | 锚点无对应标题 | warning |
| OL-LINK-005 | 图片缺 alt 文本 | nit |
| OL-LINK-006 | 同一 URL 重复 ≥5 次 | warning |
| OL-LINK-007 | 链接含空格未编码 | warning |
| OL-LINK-008 | "点击这里"类无意义链接文本 | nit |

### OL-BADLINK 坏链模式类（6 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-BADLINK-001 | example.com/org/net 占位 | blocker |
| OL-BADLINK-002 | localhost 链接 | warning |
| OL-BADLINK-003 | TODO/FIXME 残留 | warning |
| OL-BADLINK-004 | 本地图片/附件不存在 | blocker |
| OL-BADLINK-005 | your-username/YOUR_REPO 占位 | blocker |
| OL-BADLINK-006 | coming soon 占位 | warning |

### OL-DEMO 演示类（4 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-DEMO-001 | 视频无时长标注 | warning |
| OL-DEMO-002 | GIF 无大小/时长说明 | nit |
| OL-DEMO-003 | 演示视频超 3 分钟 | warning |
| OL-DEMO-004 | 演示章节只有视频无文字说明 | warning |

### OL-TRUTH 诚实类（8 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-TRUTH-001 | stars 数字无依据 | blocker |
| OL-TRUTH-002 | 下载量/用户数无依据 | blocker |
| OL-TRUTH-003 | "最快/第一/唯一"绝对化宣称 | warning |
| OL-TRUTH-004 | 排名声明无时间 | warning |
| OL-TRUTH-005 | 好评宣称无来源 | warning |
| OL-TRUTH-006 | "被XX公司采用"无来源 | warning |
| OL-TRUTH-007 | 性能数字无复现方式 | warning |
| OL-TRUTH-008 | 融资/收入数字 | warning |

### OL-STRUCT 结构类（6 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-STRUCT-001 | 前 40 行无 GEO 答案块（一句话+安装命令） | warning |
| OL-STRUCT-002 | 无 .github 目录 | nit |
| OL-STRUCT-003 | 无 topics 建议 | nit |
| OL-STRUCT-004 | 无 .gitignore | warning |
| OL-STRUCT-005 | README 版本与 package.json 不一致 | warning |
| OL-STRUCT-006 | 无路线图 | nit |

### OL-PUB 发布节奏类（2 条）
| 规则 | 含义 | 级别 |
|---|---|---|
| OL-PUB-001 | launch 素材无发布时间建议 | nit |
| OL-PUB-002 | 多平台文案首段完全相同 | warning |

## 3. 脚本用法

```bash
# 人类可读报告
python3 scripts/audit/oss_launch_audit.py --target <仓库目录> --format text
# JSON（供 hook / CI）
python3 scripts/audit/oss_launch_audit.py --target <仓库目录> --format json
# exit code：0=无 blocker，2=有 blocker
```

## 4. 人工评审清单（脚本抓不到的 10 项）

1. [ ] 首屏 30 秒测试：找个没见过项目的人，能否说出"这是什么、给谁用、怎么装"？
2. [ ] 演示材料是当前版本的真实截图吗？
3. [ ] 所有数字（star/下载/性能）都有真实来源吗？
4. [ ] 四份 launch 素材的调性真的不一样吗？
5. [ ] 安装命令在干净环境跑通过吗？
6. [ ] 用法示例的命令都真实可跑吗？
7. [ ] 徽章的 CI 状态是绿的吗？
8. [ ] 贡献指南里的流程自己走过一遍吗？
9. [ ] 路线图里的条目是认真的吗（不是画饼）？
10. [ ] 准备好回答 HN 评论区的三个刁钻问题了吗？

## 5. 反模式

1. **为过而改阈值**：把"重复 5 次"改成"重复 10 次"让 warning 消失——作弊，不许。
2. **warning 当没看见**：warning 需要"修或写豁免理由"，不能静默忽略。
3. **只跑脚本不看清单**：脚本是底稿，第 4 节人工清单必须过一遍。
4. **占位符"下次再改"**：example.com、TODO 跟着发布等于公开处刑。
5. **数字"先写上再说"**：虚构数据一旦发布，截图会流传很久；删了也没用。

## 6. 自检与反馈

### 质检门（本 skill 自查）
- [ ] 49 条规则分类解读是否与脚本实现一致（rule_id 一一对应）？
- [ ] 人工清单 10 项是否覆盖脚本盲区（真实性、可跑性、调性）？
- [ ] 诚实类规则是否覆盖了常见的虚构数据类型？

### 标准冒烟用例
对 `fixtures/oss-bad` 跑脚本：期望 17 个埋点规则全命中、exit code 为 2；对 `fixtures/oss-good` 跑：期望零 blocker、exit code 为 0。

### 一键反馈
发现规则误报/漏报，以 `[QC] lhg-ol-audit <rule_id> <一句话>` 为标题提交到 https://github.com/lhg-plugs/lhg-oss-launch/issues，正文写清"触发文本 → 实际判定 → 期望判定"。

## 出品：刘洪光

本 skill 由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills
- 视频号：搜「刘洪光实名上网」
- 微信：lhgsmsw
