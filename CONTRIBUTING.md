# Contributing to 中国官方 MCP & Skill 收录目录

感谢你对本项目感兴趣！

## 添加新服务

1. 编辑 `data/services.json`，在对应 category 下追加条目
2. 遵循 [`data/schema.json`](data/schema.json) 的结构定义
3. 运行 `python scripts/build_readme.py` 重建目录
4. 运行 `python scripts/check.py --no-network` 确保通过校验
5. 提交 PR

## 字段说明

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `id` | ✅ | 小写短横线唯一标识，如 `amap`、`baidu-maps` |
| `name` | ✅ | 中文名 |
| `name_en` | | 英文名（可选） |
| `vendor` | ✅ | 运营主体名称 |
| `category` | ✅ | 见 [schema.json](data/schema.json) 枚举 |
| `official` | ✅ | 必须为 `true` |
| `mcp` | ✅ | 必须有 `available` 字段 |
| `skill` | ✅ | 必须有 `available` 字段 |
| `auth` | ✅ | 鉴权方式枚举 |
| `docs` | ✅ | 官方文档首页 URL |
| `verified_at` | ✅ | 首次收录日期，格式 `YYYY-MM-DD` |
| `notes` | | 补充说明（如是否需要客户端、哪些操作需人工确认） |
| `source` | | 信息来源（URL 或推文 ID） |
| `status` | | 巡检脚本自动写入，勿手动修改 |

## MCP vs Skill

- **MCP**: Model Context Protocol server，支持远程（`remote`）或本地（`stdio`）
- **Skill**: OpenClaw / Claude Code 等平台的技能定义，通常为 `SKILL.md`

若服务同时提供两者，分别填写；若某项不可用，设 `available: false` 即可。

## 本地检查

```bash
# 安装依赖（Python 3.10+）
python -m pip install -r requirements.txt

# 校验 JSON 结构
python scripts/check.py --no-network

# 重建 README 目录
python scripts/build_readme.py
```

## 提交规范

- 每条 PR 只修改一个服务
- 确保 `docs` 链接可访问（或标注预计失效原因）
- 若新增 `mcp.install` 命令，注明支持的 OS 和工具（`npx` / `uvx` / 其他）
