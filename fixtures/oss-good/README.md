# SuperTool

> SuperTool 是一个命令行文件整理工具，一句话自动归档下载文件夹。

```bash
npm install -g supertool
```

当前版本：v1.0.0

## 功能
- 一句话整理下载文件夹
- 自定义归档规则

## 安装
```bash
npm install -g supertool
```

## 快速开始
```bash
supertool ~/Downloads --dry-run
```

## 用法
```bash
# 预览模式（不实际移动文件）
supertool ~/Downloads --dry-run
# 按规则归档
supertool ~/Downloads --rule photos:*.jpg
```

## 演示

![演示](./assets/demo.gif)（约 2MB，循环播放）

[演示视频](https://youtu.be/abc123)（时长 1:32）：一句话整理下载文件夹的完整过程。

## 许可
本项目采用 MIT 许可，详见 LICENSE 文件。

## 贡献
欢迎提 issue 与 PR，详见 CONTRIBUTING.md。

## 路线图
- v1.1：配置文件支持
- v1.2：Windows 支持

topics 建议：cli, file-organizer, productivity
