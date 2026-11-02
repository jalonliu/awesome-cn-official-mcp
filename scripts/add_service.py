#!/usr/bin/env python3
"""从推文/文档 URL 自动解析并添加 MCP/Skill 条目到 data/services.json。

用法:
  python scripts/add_service.py --url https://x.com/.../status/...
  python scripts/add_service.py --url https://developer.amap.com/...
  python scripts/add_service.py --interactive   # 手动填写
  python scripts/add_service.py --batch tweets.txt   # 批量处理推文列表
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SERVICES = DATA / "services.json"
SCHEMA = DATA / "schema.json"

# 已知服务 ID → 名称映射（用于推断 category）
KNOWN = {
    "amap": ("高德地图", "出行和生活"),
    "baidu-maps": ("百度地图", "出行和生活"),
    "tencent-maps": ("腾讯地图", "出行和生活"),
    "didi": ("滴滴出行", "出行和生活"),
    "meituan": ("美团", "出行和生活"),
    "taobao": ("淘宝", "出行和生活"),
    "mcdonalds-cn": ("麦当劳中国", "出行和生活"),
    "luckin": ("瑞幸咖啡", "出行和生活"),
    "fliggy": ("飞猪", "出行和生活"),
    "tongcheng": ("同程商旅", "出行和生活"),
    "feishu": ("飞书", "办公和协作"),
    "dingtalk": ("钉钉", "办公和协作"),
    "wecom": ("企业微信", "办公和协作"),
    "tencent-docs": ("腾讯文档", "办公和协作"),
    "tencent-meeting": ("腾讯会议", "办公和协作"),
    "wps": ("WPS", "办公和协作"),
    "kingsoft-docs": ("金山文档", "办公和协作"),
    "yuque": ("语雀", "办公和协作"),
    "qq-mail": ("QQ 邮箱", "办公和协作"),
    "weread": ("微信读书", "笔记阅读网盘"),
    "ima": ("腾讯 ima", "笔记阅读网盘"),
    "getnote": ("Get 笔记", "笔记阅读网盘"),
    "flomo": ("flomo", "笔记阅读网盘"),
    "yinxiang": ("印象笔记", "笔记阅读网盘"),
    "youdao": ("有道云笔记", "笔记阅读网盘"),
    "quark-drive": ("夸克网盘", "笔记阅读网盘"),
    "weiyun": ("腾讯微云", "笔记阅读网盘"),
    "baidu-pan": ("百度网盘", "笔记阅读网盘"),
    "zhihu": ("知乎", "搜索内容企业数据"),
    "bocha": ("博查搜索", "搜索内容企业数据"),
    "qcc": ("企查查", "搜索内容企业数据"),
    "tianyancha": ("天眼查", "搜索内容企业数据"),
    "douyin": ("抖音开放平台", "搜索内容企业数据"),
    "oceanengine": ("巨量引擎", "搜索内容企业数据"),
    "mastergo": ("MasterGo", "设计创作"),
    "modao": ("墨刀", "设计创作"),
    "pixso": ("Pixso", "设计创作"),
    "kling": ("可灵", "设计创作"),
    "minimax": ("MiniMax", "设计创作"),
    "netease-music": ("网易云音乐", "设计创作"),
    "alipay": ("支付宝", "支付金融"),
    "wechat-pay": ("微信支付", "支付金融"),
    "unionpay": ("银联", "支付金融"),
    "ifind": ("同花顺 iFinD", "支付金融"),
    "ifind-wencai": ("同花顺问财", "支付金融"),
    "eastmoney": ("东方财富妙想", "支付金融"),
    "aliyun": ("阿里云", "云和开发"),
    "tencent-cloud": ("腾讯云", "云和开发"),
    "huawei-cloud": ("华为云", "云和开发"),
    "volcengine": ("火山引擎", "云和开发"),
    "baidu-ai": ("百度智能云", "云和开发"),
    "qiniu": ("七牛云", "云和开发"),
    "zhipu": ("智谱", "云和开发"),
    "gitee": ("Gitee", "云和开发"),
    "gitlab-cn": ("极狐 GitLab", "云和开发"),
}

CATEGORY_OPTIONS = [
    "出行和生活", "办公和协作", "笔记阅读网盘",
    "搜索内容企业数据", "设计创作", "支付金融", "云和开发", "其他"
]

AUTH_OPTIONS = ["none", "api_key", "oauth", "account", "enterprise", "unknown"]
MCP_TYPE_OPTIONS = ["stdio", "remote", "both"]


def load_services() -> list[dict]:
    return json.loads(SERVICES.read_text(encoding="utf-8"))


def save_services(services: list[dict]) -> None:
    SERVICES.write_text(json.dumps(services, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def infer_from_url(url: str) -> dict:
    """从 URL 推断基础字段。"""
    domain = urlparse(url).hostname or ""
    path = urlparse(url).path.lower()

    hints: dict = {"docs": url}

    # 根据域名/路径推断服务类型
    if "amap" in domain or "高德" in path:
        hints["id"] = "amap"
        hints["name"] = "高德地图"
        hints["vendor"] = "高德地图"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "地理编码、路径规划、POI 搜索、天气"
    elif "lbs.baidu.com" in domain or "百度地图" in url:
        hints["id"] = "baidu-maps"
        hints["name"] = "百度地图"
        hints["vendor"] = "百度地图"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "国内首个兼容 MCP 协议的地图服务"
    elif "lbs.qq.com" in domain or "腾讯地图" in url:
        hints["id"] = "tencent-maps"
        hints["name"] = "腾讯地图"
        hints["vendor"] = "腾讯地图"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "remote"
        hints["auth"] = "api_key"
        hints["notes"] = "远程 MCP，Key 在位置服务控制台申请"
    elif "didichuxing" in domain:
        hints["id"] = "didi"
        hints["name"] = "滴滴出行"
        hints["vendor"] = "滴滴出行"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "remote"
        hints["auth"] = "api_key"
        hints["notes"] = "估价、下单、行程状态、取消；有沙箱端点"
    elif "meituan" in domain:
        hints["id"] = "meituan"
        hints["name"] = "美团"
        hints["vendor"] = "美团"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "account"
        hints["notes"] = "开放平台 AI Hub 提供 MCP 列表"
    elif "taobao" in domain or "tblifecdn" in domain:
        hints["id"] = "taobao"
        hints["name"] = "淘宝"
        hints["vendor"] = "阿里巴巴淘宝"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "account"
        hints["notes"] = "需安装淘宝桌面客户端；下单付款需人工最终确认"
    elif "mcd.cn" in domain:
        hints["id"] = "mcdonalds-cn"
        hints["name"] = "麦当劳中国"
        hints["vendor"] = "麦当劳中国"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "remote"
        hints["auth"] = "oauth"
        hints["notes"] = "附近门店、菜单、营养查询"
    elif "lkcoffee" in domain:
        hints["id"] = "luckin"
        hints["name"] = "瑞幸咖啡"
        hints["vendor"] = "瑞幸咖啡"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "remote"
        hints["auth"] = "account"
        hints["notes"] = "找附近门店、浏览商品、下单；付款需人工确认"
    elif "flyai" in domain or "fliggy" in domain:
        hints["id"] = "fliggy"
        hints["name"] = "飞猪"
        hints["vendor"] = "飞猪"
        hints["category"] = "出行和生活"
        hints["skill_available"] = True
        hints["auth"] = "account"
        hints["notes"] = "官方 Skill 仓库 alibaba-flyai/flyai-skill"
    elif "ly.com" in domain or "tongcheng" in domain:
        hints["id"] = "tongcheng"
        hints["name"] = "同程商旅"
        hints["vendor"] = "同程旅行"
        hints["category"] = "出行和生活"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "TMC 开放平台，同时提供 MCP 与 CLI Skill"
    elif "feishu" in domain or "larksuite" in domain:
        hints["id"] = "feishu"
        hints["name"] = "飞书"
        hints["vendor"] = "飞书"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "oauth"
        hints["notes"] = "官方 larksuite/cli，覆盖 MCP、命令行工具与 Skill"
    elif "dingtalk" in domain or "dingding" in domain:
        hints["id"] = "dingtalk"
        hints["name"] = "钉钉"
        hints["vendor"] = "阿里巴巴钉钉"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "企业内部应用需管理员开通"
    elif "work.weixin.qq.com" in domain:
        hints["id"] = "wecom"
        hints["name"] = "企业微信"
        hints["vendor"] = "腾讯企业微信"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "官方 AICLI，含 MCP 与 Skill"
    elif "docs.qq.com" in domain:
        hints["id"] = "tencent-docs"
        hints["name"] = "腾讯文档"
        hints["vendor"] = "腾讯文档"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "remote"
        hints["auth"] = "account"
        hints["notes"] = "在线文档的读写 MCP"
    elif "cloud.tencent.com" in domain and "meeting" in path:
        hints["id"] = "tencent-meeting"
        hints["name"] = "腾讯会议"
        hints["vendor"] = "腾讯会议"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "会议创建/查询等能力，需企业版权限"
    elif "wps.cn" in domain or "wps" in domain:
        hints["id"] = "wps"
        hints["name"] = "WPS"
        hints["vendor"] = "金山软件 WPS"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "文档创建与编辑类能力"
    elif "kdocs" in domain or "kingsoft" in domain:
        hints["id"] = "kingsoft-docs"
        hints["name"] = "金山文档"
        hints["vendor"] = "金山办公"
        hints["category"] = "办公和协作"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "官方 Skill 仓库 kdocs-app/kdocs-skill"
    elif "yuque" in domain:
        hints["id"] = "yuque"
        hints["name"] = "语雀"
        hints["vendor"] = "阿里巴巴语雀"
        hints["category"] = "办公和协作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "知识库文档读写"
    elif "agently" in domain or "qq.com" in domain and "mail" in path:
        hints["id"] = "qq-mail"
        hints["name"] = "QQ 邮箱"
        hints["vendor"] = "腾讯"
        hints["category"] = "办公和协作"
        hints["skill_available"] = True
        hints["auth"] = "account"
        hints["notes"] = "腾讯官方 AgentlyMail，邮件收发与检索"
    elif "weread" in domain:
        hints["id"] = "weread"
        hints["name"] = "微信读书"
        hints["vendor"] = "腾讯微信读书"
        hints["category"] = "笔记阅读网盘"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "书架、笔记、划线读取"
    elif "ima.qq.com" in domain:
        hints["id"] = "ima"
        hints["name"] = "腾讯 ima"
        hints["vendor"] = "腾讯 ima"
        hints["category"] = "笔记阅读网盘"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "知识库问答接口"
    elif "biji.com" in domain:
        hints["id"] = "getnote"
        hints["name"] = "Get 笔记"
        hints["vendor"] = "Get 笔记"
        hints["category"] = "笔记阅读网盘"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "同时提供 MCP 与 Skill"
    elif "flomoapp" in domain:
        hints["id"] = "flomo"
        hints["name"] = "flomo"
        hints["vendor"] = "flomo"
        hints["category"] = "笔记阅读网盘"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "卡片记录与检索"
    elif "yinxiang" in domain or "evernote" in domain:
        hints["id"] = "yinxiang"
        hints["name"] = "印象笔记"
        hints["vendor"] = "印象笔记"
        hints["category"] = "笔记阅读网盘"
        hints["skill_available"] = True
        hints["auth"] = "account"
        hints["notes"] = "经 SkillHub 分发的官方 Skill"
    elif "youdao" in domain:
        hints["id"] = "youdao"
        hints["name"] = "有道云笔记"
        hints["vendor"] = "网易有道"
        hints["category"] = "笔记阅读网盘"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "account"
        hints["notes"] = "同时提供 MCP 与 Skill"
    elif "quark.cn" in domain:
        hints["id"] = "quark-drive"
        hints["name"] = "夸克网盘"
        hints["vendor"] = "阿里巴巴夸克"
        hints["category"] = "笔记阅读网盘"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "网盘文件检索与整理"
    elif "weiyun.com" in domain:
        hints["id"] = "weiyun"
        hints["name"] = "腾讯微云"
        hints["vendor"] = "腾讯微云"
        hints["category"] = "笔记阅读网盘"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "微云开放 Skill 接入页"
    elif "pan.baidu.com" in domain:
        hints["id"] = "baidu-pan"
        hints["name"] = "百度网盘"
        hints["vendor"] = "百度"
        hints["category"] = "笔记阅读网盘"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "文件列表、上传下载、分享链接管理"
    elif "zhihu" in domain:
        hints["id"] = "zhihu"
        hints["name"] = "知乎"
        hints["vendor"] = "知乎"
        hints["category"] = "搜索内容企业数据"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "account"
        hints["notes"] = "官方 zhihu_cli：内容搜索与问答"
    elif "bocha" in domain:
        hints["id"] = "bocha"
        hints["name"] = "博查搜索"
        hints["vendor"] = "博查"
        hints["category"] = "搜索内容企业数据"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "中文联网搜索，国内直连"
    elif "qcc.com" in domain:
        hints["id"] = "qcc"
        hints["name"] = "企查查"
        hints["vendor"] = "企查查"
        hints["category"] = "搜索内容企业数据"
        hints["mcp_type"] = "remote"
        hints["auth"] = "api_key"
        hints["notes"] = "工商、风险、知产、经营等 10 组企业数据 MCP"
    elif "tianyancha" in domain or "tyc" in domain:
        hints["id"] = "tianyancha"
        hints["name"] = "天眼查"
        hints["vendor"] = "天眼查"
        hints["category"] = "搜索内容企业数据"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "企业工商与风险信息查询"
    elif "open-douyin" in domain or "douyin" in domain:
        hints["id"] = "douyin"
        hints["name"] = "抖音开放平台"
        hints["vendor"] = "字节跳动抖音"
        hints["category"] = "搜索内容企业数据"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "oauth"
        hints["notes"] = "视频发布、数据查询等开放能力"
    elif "oceanengine" in domain:
        hints["id"] = "oceanengine"
        hints["name"] = "巨量引擎"
        hints["vendor"] = "字节跳动巨量引擎"
        hints["category"] = "搜索内容企业数据"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "广告投放数据查询与操作"
    elif "mastergo" in domain:
        hints["id"] = "mastergo"
        hints["name"] = "MasterGo"
        hints["vendor"] = "MasterGo"
        hints["category"] = "设计创作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "设计稿读取与生成"
    elif "modao.cc" in domain:
        hints["id"] = "modao"
        hints["name"] = "墨刀"
        hints["vendor"] = "墨刀"
        hints["category"] = "设计创作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "原型与设计文件 MCP"
    elif "pixso" in domain:
        hints["id"] = "pixso"
        hints["name"] = "Pixso"
        hints["vendor"] = "Pixso"
        hints["category"] = "设计创作"
        hints["mcp_type"] = "remote"
        hints["auth"] = "api_key"
        hints["notes"] = "远端 MCP，无需本地安装"
    elif "klingai" in domain or "kling" in domain:
        hints["id"] = "kling"
        hints["name"] = "可灵"
        hints["vendor"] = "快手可灵"
        hints["category"] = "设计创作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "视频/图像生成，官方 Skill 仓库 klingai-tech/skills"
    elif "minimax" in domain:
        hints["id"] = "minimax"
        hints["name"] = "MiniMax"
        hints["vendor"] = "MiniMax"
        hints["category"] = "设计创作"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "语音合成、视频生成等"
    elif "music.163.com" in domain:
        hints["id"] = "netease-music"
        hints["name"] = "网易云音乐"
        hints["vendor"] = "网易云音乐"
        hints["category"] = "设计创作"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "官方 ncmcli，歌单与搜索能力"
    elif "alipay" in domain or "open.alipay.com" in domain:
        hints["id"] = "alipay"
        hints["name"] = "支付宝"
        hints["vendor"] = "阿里巴巴支付宝"
        hints["category"] = "支付金融"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "需商户号与密钥；涉及付款必须人工确认"
    elif "pay.weixin.qq.com" in domain:
        hints["id"] = "wechat-pay"
        hints["name"] = "微信支付"
        hints["vendor"] = "腾讯微信支付"
        hints["category"] = "支付金融"
        hints["skill_available"] = True
        hints["auth"] = "enterprise"
        hints["notes"] = "商户支付 Skill，付款需人工最终确认"
    elif "unionpay" in domain or "up.10010.com" in domain:
        hints["id"] = "unionpay"
        hints["name"] = "银联"
        hints["vendor"] = "中国银联"
        hints["category"] = "支付金融"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "enterprise"
        hints["notes"] = "开放平台 MCP 解决方案页"
    elif "10jqka" in domain or "ifind" in domain:
        hints["id"] = "ifind"
        hints["name"] = "同花顺 iFinD"
        hints["vendor"] = "同花顺"
        hints["category"] = "支付金融"
        hints["mcp_type"] = "remote"
        hints["auth"] = "account"
        hints["notes"] = "金融数据终端 MCP，需 iFinD 账号"
    elif "10jqka" in domain and "wencai" in domain:
        hints["id"] = "ifind-wencai"
        hints["name"] = "同花顺问财"
        hints["vendor"] = "同花顺"
        hints["category"] = "支付金融"
        hints["skill_available"] = True
        hints["auth"] = "none"
        hints["notes"] = "自然语言选股与问数"
    elif "dfcf" in domain or "eastmoney" in domain:
        hints["id"] = "eastmoney"
        hints["name"] = "东方财富妙想"
        hints["vendor"] = "东方财富"
        hints["category"] = "支付金融"
        hints["skill_available"] = True
        hints["auth"] = "account"
        hints["notes"] = "金融 Skill Hub"
    elif "aliyun.com" in domain and "mcp" in path:
        hints["id"] = "aliyun"
        hints["name"] = "阿里云"
        hints["vendor"] = "阿里云"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "remote"
        hints["auth"] = "api_key"
        hints["notes"] = "OpenAPI 全量 MCP，产品维度另有独立 server"
    elif "tencent.com" in domain and "mcp" in path:
        hints["id"] = "tencent-cloud"
        hints["name"] = "腾讯云"
        hints["vendor"] = "腾讯云"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "云 API MCP + Skill 双形态"
    elif "huaweicloud" in domain:
        hints["id"] = "huawei-cloud"
        hints["name"] = "华为云"
        hints["vendor"] = "华为云"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "官方仓库同时提供 Skill"
    elif "volcengine" in domain or "bytegoofy" in domain:
        hints["id"] = "volcengine"
        hints["name"] = "火山引擎"
        hints["vendor"] = "字节跳动火山引擎"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "TOS、ECS 等多产品 MCP"
    elif "ai.baidu.com" in domain:
        hints["id"] = "baidu-ai"
        hints["name"] = "百度智能云"
        hints["vendor"] = "百度智能云"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "千帆平台 MCP 能力"
    elif "qiniu云" in domain or "qiniu.com" in domain:
        hints["id"] = "qiniu"
        hints["name"] = "七牛云"
        hints["vendor"] = "七牛云"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "对象存储、上传、CDN"
    elif "bigmodel" in domain or "zhipuai" in domain:
        hints["id"] = "zhipu"
        hints["name"] = "智谱"
        hints["vendor"] = "智谱 AI"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "联网搜索 MCP"
    elif "gitee.com" in domain:
        hints["id"] = "gitee"
        hints["name"] = "Gitee"
        hints["vendor"] = "Gitee"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "仓库、Issue、PR 管理"
    elif "gitlab.cn" in domain or "jihu" in domain:
        hints["id"] = "gitlab-cn"
        hints["name"] = "极狐 GitLab"
        hints["vendor"] = "极狐 GitLab"
        hints["category"] = "云和开发"
        hints["mcp_type"] = "stdio"
        hints["auth"] = "api_key"
        hints["notes"] = "gitlab.cn 官方 MCP 公告页"
    else:
        # 尝试从 Known 映射
        for key, (name, cat) in KNOWN.items():
            if key in url.lower() or key in domain.lower():
                hints["id"] = key
                hints["name"] = name
                hints["category"] = cat
                break

    return hints


def prompt_input(prompt: str, default: str = "") -> str:
    """交互式输入。"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def add_service(hints: dict, interactive: bool = False) -> dict | None:
    """收集完整信息并返回新 entry。"""
    today = date.today().isoformat()

    # ID 必须唯一
    existing_ids = {s["id"] for s in load_services()}
    service_id = hints.get("id", "")
    if not service_id:
        service_id = prompt_input("服务 ID (小写短横线，如 amap): ", "")
    while not service_id or service_id in existing_ids:
        if service_id in existing_ids:
            print(f"  ⚠️  ID '{service_id}' 已存在")
        service_id = prompt_input("服务 ID: ", "").lower().replace(" ", "-")

    name = hints.get("name", "")
    if not name:
        name = prompt_input("中文名: ", "")
    name_en = hints.get("name_en", "")
    if not name_en:
        name_en = prompt_input("英文名 (可选): ", "")

    vendor = hints.get("vendor", name)
    if not vendor:
        vendor = prompt_input("运营主体: ", name)

    category = hints.get("category", "")
    if not category:
        print(f"可用分类: {', '.join(CATEGORY_OPTIONS)}")
        category = prompt_input("分类: ", "其他")

    auth = hints.get("auth", "unknown")
    if not auth:
        print(f"鉴权方式: {', '.join(AUTH_OPTIONS)}")
        auth = prompt_input("鉴权方式: ", "unknown")

    mcp_available = hints.get("mcp_available", True)
    mcp_type = hints.get("mcp_type", "")
    if mcp_available:
        if not mcp_type:
            print(f"MCP 类型: {', '.join(MCP_TYPE_OPTIONS)}")
            mcp_type = prompt_input("MCP 类型 (stdio/remote/both): ", "stdio")
        mcp_url = hints.get("mcp_url", hints.get("docs", ""))
    else:
        mcp_type = ""
        mcp_url = ""

    skill_available = hints.get("skill_available", False)
    skill_url = hints.get("skill_url", hints.get("docs", ""))

    notes = hints.get("notes", "")
    if not notes:
        notes = prompt_input("备注 (可选): ", "")

    docs = hints.get("docs", "")
    if not docs:
        docs = prompt_input("文档首页 URL: ", "")

    source = hints.get("source", "")
    if not source:
        source = prompt_input("来源 (可选，如推文 URL): ", "")

    client_required = hints.get("client_required", "")
    if not client_required and "需安装" in notes:
        client_required = prompt_input("是否需要客户端 (如 '淘宝桌面客户端', 留空则无需): ", "")

    entry: dict = {
        "id": service_id,
        "name": name,
        "name_en": name_en or None,
        "vendor": vendor,
        "category": category,
        "official": True,
        "mcp": {
            "available": mcp_available,
            "type": mcp_type if mcp_available else None,
            "url": mcp_url or None,
            "install": None,
        },
        "skill": {
            "available": skill_available,
            "url": skill_url or None,
        },
        "auth": auth,
        "docs": docs,
        "notes": notes or None,
        "source": source or None,
        "verified_at": today,
        "last_checked": today,
        "status": "active",
    }
    if client_required:
        entry["client_required"] = client_required

    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description="从 URL 或交互方式添加 MCP/Skill 条目")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="推文或文档 URL")
    group.add_argument("--interactive", action="store_true", help="手动交互式添加")
    group.add_argument("--batch", help="包含推文 URL 列表的文件（每行一条）")
    ap.add_argument("--skip-check", action="store_true", help="跳过 README 重建和提交")
    args = ap.parse_args()

    services = load_services()

    if args.batch:
        urls = Path(args.batch).read_text(encoding="utf-8").splitlines()
        urls = [u.strip() for u in urls if u.strip()]
        entries = []
        for url in urls:
            hints = infer_from_url(url)
            entry = add_service(hints, interactive=False)
            if entry:
                entries.append(entry)
                print(f"  ✓ 添加: {entry['name']} ({entry['id']})")
    elif args.url:
        hints = infer_from_url(args.url)
        entry = add_service(hints, interactive=False)
        if entry:
            services.append(entry)
            print(f"✓ 添加: {entry['name']} ({entry['id']})")
            print(f"  分类: {entry['category']}")
            print(f"  MCP: {'✅' if entry['mcp']['available'] else '—'} {entry['mcp'].get('type') or ''}")
            print(f"  Skill: {'✅' if entry['skill']['available'] else '—'}")
            print(f"  文档: {entry['docs']}")
    else:
        entry = add_service({}, interactive=True)
        if entry:
            services.append(entry)
            print(f"\n✓ 已添加: {entry['name']}")

    if not args.skip_check:
        save_services(services)
        print(f"\n📦 已保存到 data/services.json (共 {len(services)} 条)")

        # 重建 README
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_readme.py")],
            cwd=str(ROOT), capture_output=True, text=True
        )
        if result.returncode == 0:
            print("📄 README.md 已重建")
        else:
            print(f"⚠️  README 重建失败: {result.stderr}")

        # 运行检查
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check.py"), "--no-network"],
            cwd=str(ROOT), capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ 结构校验通过")
        else:
            print(f"❌ 结构校验失败:\n{result.stdout}\n{result.stderr}")
            return 1

        # 提交推送
        import subprocess
        subprocess.run(["git", "add", "-A"], cwd=str(ROOT), check=False)
        subprocess.run(
            ["git", "commit", "-m", f"feat: add {entry['name']} ({entry['id']})"],
            cwd=str(ROOT), check=False
        )
        subprocess.run(
            ["git", "push"],
            cwd=str(ROOT), check=False,
            env={**os.environ, "GH_TOKEN": os.environ.get("GH_TOKEN", "")}
        )
        print("🚀 已推送到 GitHub")

    return 0


if __name__ == "__main__":
    import os
    sys.exit(main())
