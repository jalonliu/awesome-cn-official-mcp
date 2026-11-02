---
name: add-cn-mcp
description: 向 awesome-cn-official-mcp 项目添加新的中国官方 MCP/Skill 条目。当用户提供推文 URL、文档 URL 或描述一个新服务时使用。
---

# Add Chinese MCP/Skill Service

向 `D:\DSH\awesome-cn-official-mcp` 项目添加新条目并自动推送。

## 触发条件

用户说：
- "添加 XXX 的 MCP"
- "把这篇推文里的 MCP 加进去：https://..."
- "收录 XXX 的 Skill"
- 提供新的国内服务 MCP/Skill 链接

## 工作流程

1. **解析输入**
   - 如果用户提供 URL：运行 `python scripts/add_service.py --url <url> --skip-check`
   - 如果用户提供描述：询问具体 URL 和关键信息（名称、鉴权方式等）

2. **补充信息**（如果 URL 推断不足）
   - MCP 类型：stdio / remote / both
   - 鉴权方式：none / api_key / oauth / account / enterprise
   - 备注说明

3. **重建并验证**
   ```bash
   cd D:\DSH\awesome-cn-official-mcp
   python scripts/build_readme.py
   python scripts/check.py --no-network
   ```

4. **提交推送**
   ```bash
   git add -A
   git commit -m "feat: add <服务名> (<id>)"
   git push
   ```

## 已知服务分类参考

| 分类 | 示例服务 |
| --- | --- |
| 出行和生活 | 高德、百度地图、滴滴、美团、淘宝、麦当劳、瑞幸、飞猪、同程 |
| 办公和协作 | 飞书、钉钉、企微、腾讯文档、WPS、语雀、有道云笔记 |
| 笔记阅读网盘 | 微信读书、夸克网盘、百度网盘、微云、flomo |
| 搜索内容企业数据 | 知乎、博查、企查查、天眼查、抖音、巨量引擎 |
| 设计创作 | MasterGo、墨刀、Pixso、可灵、MiniMax、网易云音乐 |
| 支付金融 | 支付宝、微信支付、银联、同花顺、东方财富 |
| 云和开发 | 阿里云、腾讯云、华为云、火山引擎、智谱、Gitee、极狐 GitLab |

## 重要

- 只收录 **official: true**（服务方自己发布），不收录社区第三方实现
- 每条必须有 `docs` URL
- 涉及付款的操作必须标注 "需人工确认"
- MCP 类型必填：stdio 或 remote
- 鉴权方式必填：none/api_key/oauth/account/enterprise
