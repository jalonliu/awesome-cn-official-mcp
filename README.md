# 中国官方 MCP & Skill 收录目录

[![Weekly Check](https://github.com/jalonliu/awesome-cn-official-mcp/actions/workflows/weekly-check.yml/badge.svg)](https://github.com/jalonliu/awesome-cn-official-mcp/actions/workflows/weekly-check.yml)
[![Build](https://github.com/jalonliu/awesome-cn-official-mcp/actions/workflows/build.yml/badge.svg)](https://github.com/jalonliu/awesome-cn-official-mcp/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

仅收录**国内服务方官方（first-party）**发布的 MCP Server 与 Skill。

> 定位：机器可读注册表 + 人工友好目录。  
> 数据源：[`data/services.json`](data/services.json)，由脚本自动重建可读目录。

## 收录标准

- **official: true** —— 由服务运营主体自行发布或认证（非第三方社区实现）
- 至少开放 MCP 或 Skill 之一
- 服务面向国内用户
- 有可访问的文档或仓库链接

## 使用方式

```bash
# 安装依赖
python -m venv .venv && source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate                              # Windows

# 重建 README 目录区块
python scripts/build_readme.py

# 巡检：结构校验 + 链接可达性检查
python scripts/check.py --write
python scripts/check.py --no-network --report out.md  # CI 模式
```

## 目录

<!-- CATALOG:START -->

> 数据快照：共 **55** 个国内服务 · **43** 个提供官方 MCP （其中 9 个远程端点）· **26** 个提供官方 Skill。  
> 最后重建：2026-11-02

> 图例：✅ 已开放 · — 未开放 · Key/OAuth/账号授权 = 调用前需要的前置凭据。

### 出行和生活

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| 高德地图 | MCP<sub>stdio</sub> · Skill | Key | [文档](https://developer.amap.com/api/mcp-server/summary) | 地理编码、路径规划、POI 搜索、天气 |
| 百度地图 | MCP<sub>stdio</sub> | Key | [文档](https://lbs.baidu.com/docs/ai?title=mcpserver%2Fbase) | 国内首个兼容 MCP 协议的地图服务 |
| 腾讯地图 | MCP<sub>remote</sub> | Key | [文档](https://lbs.qq.com/service/MCPServer/MCPServerGuide/overview) | 远程 MCP，Key 在位置服务控制台申请 |
| 滴滴出行 | MCP<sub>remote</sub> · Skill | Key | [文档](https://mcp.didichuxing.com/) | 估价、下单、行程状态、取消；有沙箱端点。付款环节需人工确认 |
| 美团 | MCP · Skill | 账号授权 | [文档](https://developer.meituan.com/ai-hub/mcp-list) | 开放平台 AI Hub 提供 MCP 列表；下单类操作需账号授权 |
| 淘宝 | MCP · Skill | 账号授权 | [文档](https://tblifecdn.taobao.com/taobaopc/skills/taobao-native/SKILL.md) | 需安装淘宝桌面客户端；下单付款需人工最终确认 |
| 麦当劳中国 | MCP<sub>remote</sub> | OAuth | [文档](https://open.mcd.cn/mcp/doc) | 附近门店、菜单、营养查询；Bearer token 取自 open.mcd.cn |
| 瑞幸咖啡 | MCP<sub>remote</sub> | 账号授权 | [文档](https://open.lkcoffee.com/docs) | 找附近门店、浏览商品、下单；付款需人工确认 |
| 飞猪 | Skill | 账号授权 | [文档](https://github.com/alibaba-flyai/flyai-skill) | 官方 Skill 仓库 alibaba-flyai/flyai-skill |
| 同程商旅 | MCP · Skill | 企业认证 | [文档](https://tmc.ly.com/zh/resources/updates/open-mcp-skills-cli) | TMC 开放平台，同时提供 MCP 与 CLI Skill |

### 办公和协作

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| 飞书 | MCP · Skill | OAuth | [文档](https://github.com/larksuite/cli) | 官方 larksuite/cli，覆盖 MCP、命令行工具与 Skill 三种形态 |
| 钉钉 | MCP | 企业认证 | [文档](https://open.dingtalk.com/document/ai-dev/dingtalk-server-api-mcp-overview) | 企业内部应用需管理员开通 |
| 企业微信 | MCP · Skill | 企业认证 | [文档](https://work.weixin.qq.com/nl/index/aicli) | 官方 AICLI，含 MCP 与 Skill |
| 腾讯文档 | MCP<sub>remote</sub> | 账号授权 | [文档](https://docs.qq.com/open/document/mcp/) | 在线文档的读写 MCP |
| 腾讯会议 | MCP | 企业认证 | [文档](https://cloud.tencent.com/document/product/1095/133826) | 会议创建/查询等能力，需企业版权限 |
| WPS | MCP | Key | [文档](https://open.wps.cn/documents/app-integration-dev/mcp-server/introduction) | 文档创建与编辑类能力 |
| 金山文档 | Skill | — | [文档](https://github.com/kdocs-app/kdocs-skill) | 官方 Skill 仓库 kdocs-app/kdocs-skill |
| 语雀 | MCP | Key | [文档](https://github.com/yuque/yuque-mcp-server) | 知识库文档读写 |
| QQ 邮箱 | Skill | 账号授权 | [文档](https://github.com/Tencent/AgentlyMail) | 腾讯官方 AgentlyMail，邮件收发与检索 |

### 笔记阅读网盘

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| 微信读书 | Skill | — | [文档](https://weread.qq.com/r/weread-skills) | 书架、笔记、划线读取 |
| 腾讯 ima | Skill | — | [文档](https://ima.qq.com/agent-interface) | 知识库问答接口 |
| Get 笔记 | MCP · Skill | Key | [文档](https://www.biji.com/skill) | 同时提供 MCP 与 Skill |
| flomo | MCP | Key | [文档](https://help.flomoapp.com/advance/mcp) | 卡片记录与检索 |
| 印象笔记 | Skill | 账号授权 | [文档](https://skillhub.cn/skills/yinxiangskill) | 经 SkillHub 分发的官方 Skill |
| 有道云笔记 | MCP · Skill | 账号授权 | [文档](https://note.youdao.com/help-center/skill-guide.html) | 同时提供 MCP 与 Skill |
| 夸克网盘 | Skill | — | [文档](https://www.quark.cn/documents/help/quark-drive-skill) | 网盘文件检索与整理 |
| 腾讯微云 | Skill | — | [文档](https://www.weiyun.com/act/openclaw) | 微云开放 Skill 接入页 |
| 百度网盘 | MCP | Key | [文档](https://pan.baidu.com/union/doc/mcp-server/) | 文件列表、上传下载、分享链接管理 |

### 搜索内容企业数据

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| 知乎 | MCP · Skill | 账号授权 | [文档](https://developer.zhihu.com/docs?key=zhihu_cli) | 官方 zhihu_cli：内容搜索与问答 |
| 博查搜索 | MCP<sub>stdio</sub> | Key | [文档](https://github.com/BochaAI/bocha-search-mcp) | 中文联网搜索，国内直连 |
| 企查查 | MCP<sub>remote</sub> | Key | [文档](https://agent.qcc.com/guide) | 工商、风险、知产、经营等 10 组企业数据 MCP |
| 天眼查 | MCP<sub>stdio</sub> | Key | [文档](https://github.com/tyc-tech/tyc-cli) | 企业工商与风险信息查询 |
| 抖音开放平台 | MCP | OAuth | [文档](https://developer.open-douyin.com/docs/resource/zh-CN/dop/ability/mcp-service/mcp-service-desc) | 视频发布、数据查询等开放能力 |
| 巨量引擎 | MCP | 企业认证 | [文档](https://open.oceanengine.com/mcp) | 广告投放数据查询与操作 |

### 设计创作

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| MasterGo | MCP | Key | [文档](https://mastergo.com/help/ai-features/magic-mcp.html) | 设计稿读取与生成 |
| 墨刀 | MCP | Key | [文档](https://modao.cc/feature/ai-mcp.html) | 原型与设计文件 MCP |
| Pixso | MCP<sub>remote</sub> | Key | [文档](https://pixso.net/developer/zh/mcp/remote-mcp.html) | 远端 MCP，无需本地安装 |
| 可灵 | MCP · Skill | Key | [文档](https://github.com/klingai-tech/skills) | 视频/图像生成，官方 Skill 仓库 klingai-tech/skills |
| MiniMax | MCP<sub>stdio</sub> | Key | [文档](https://github.com/MiniMax-AI/MiniMax-MCP) | 语音合成、视频生成等 |
| 网易云音乐 | Skill | — | [文档](https://music.163.com/st/ncmcli) | 官方 ncmcli，歌单与搜索能力 |

### 支付金融

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| 支付宝 | MCP · Skill | 企业认证 | [文档](https://opendocs.alipay.com/open/0h3gdq) | 需商户号与密钥；涉及付款必须人工确认 |
| 微信支付 | Skill | 企业认证 | [文档](https://pay.weixin.qq.com/doc/v3/merchant/4035576700) | 商户支付 Skill，付款需人工最终确认 |
| 银联 | MCP | 企业认证 | [文档](https://open.unionpay.com/tjweb/solution/detail?solId=613) | 开放平台 MCP 解决方案页 |
| 同花顺 iFinD | MCP<sub>remote</sub> · Skill | 账号授权 | [文档](https://mcp.51ifind.com/) | 金融数据终端 MCP，需 iFinD 账号 |
| 同花顺问财 | Skill | — | [文档](https://search.10jqka.com.cn/skillhub) | 自然语言选股与问数 |
| 东方财富妙想 | Skill | 账号授权 | [文档](https://marketing.dfcfs.com/views/finskillshub/) | 金融 Skill Hub |

### 云和开发

| 服务 | 开放能力 | 鉴权 | 入口 | 备注 |
| --- | --- | --- | --- | --- |
| 阿里云 | MCP<sub>remote</sub> | Key | [文档](https://api.aliyun.com/mcp) | OpenAPI 全量 MCP，产品维度另有独立 server |
| 腾讯云 | MCP · Skill | Key | [文档](https://cloud.tencent.com/document/product/1278/131433) | 云 API MCP + Skill 双形态 |
| 华为云 | MCP<sub>stdio</sub> · Skill | Key | [文档](https://github.com/huaweicloud/huaweicloud-mcp) | 官方仓库同时提供 Skill |
| 火山引擎 | MCP<sub>stdio</sub> | Key | [文档](https://github.com/volcengine/mcp-server) | TOS、ECS 等多产品 MCP |
| 百度智能云 | MCP | Key | [文档](https://ai.baidu.com/ai-doc/REFERENCE/mm9tjwod0) | 千帆平台 MCP 能力 |
| 七牛云 | MCP<sub>stdio</sub> | Key | [文档](https://github.com/qiniu/qiniu-mcp-server) | 对象存储、上传、CDN |
| 智谱 | MCP | Key | [文档](https://docs.bigmodel.cn/cn/coding-plan/mcp/search-mcp-server) | 联网搜索 MCP |
| Gitee | MCP<sub>stdio</sub> | Key | [文档](https://blog.gitee.com/2026/01/22/gitee-official-mcp-server-ai-code-repo/) | 仓库、Issue、PR 管理 |
| 极狐 GitLab | MCP | Key | [文档](https://gitlab.cn/news/cmvg3kvmv000nv30iuo1aifgg) | gitlab.cn 官方 MCP 公告页 |

<!-- CATALOG:END -->

## 数据说明

- 每条条目均为结构化 JSON，包含 `id/name/vendor/category/mcp/skill/auth/docs` 等字段
- `verified_at` 记录该条目首次收录日期，`last_checked` 记录最后一次巡检日期
- `status` 由巡检脚本写入：`active` / `unreachable`

## 已有同类项目

- [zackchewa/awesome-china-mcp](https://github.com/zackchewa/awesome-china-mcp) (66★) — 最接近本项目定位，但混合了社区 MCP Server
- [LeslieLeung/awesome-mcp-server-cn](https://github.com/LeslieLeung/awesome-mcp-server-cn) (48★) — 较早收录，更新频率较低
- [lj22503/awesome-finai-tools-zn](https://github.com/lj22503/awesome-finai-tools-zn) (34★) — 金融垂类

本项目差异化：仅收 first-party 官方条目、JSON 结构化、自动巡检失效链接、自动生成文档目录。

## 贡献指南

参见 [CONTRIBUTING.md](CONTRIBUTING.md)。欢迎 PR：

1. Fork 本仓库
2. 编辑 `data/services.json`（遵循 schema）
3. 运行 `python scripts/build_readme.py` 重建目录
4. 运行 `python scripts/check.py --no-network` 确保无结构错误
5. 提交 PR

## 许可证

MIT © jalonliu
