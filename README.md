# 📋 Work Report Skill

> 按 **SMART 原则**自动生成日报/周报的 AI Skill。兼容 **Claude Code** 和 **Trae IDE**。

## 快速开始

### 1. 下载

```bash
git clone https://github.com/<your-username>/work-report-skill.git
cd work-report-skill
```

### 2. 安装

```bash
python3 install.py              # 自动检测并安装到 Claude Code / Trae
python3 install.py --claude     # 仅 Claude Code
python3 install.py --trae       # 仅 Trae IDE
```

### 3. 使用

在 AI 对话中直接说：

- "帮我写日报"
- "生成本周周报"
- "今天的工作总结"

---

## 功能

| 功能 | 说明 |
|------|------|
| 🤖 **自动登录拉取** | 对接公司内部系统，自动登录拉取签到/工作数据 |
| 🔍 **API 自动探测** | 遇到新系统时，AI 自动逆向工程 API（从 JS 源码提取接口+凭证） |
| 📝 **SMART 日报** | 目标→完成情况→阻塞→明日计划→小结 |
| 📊 **SMART 周报** | 目标回顾→完成→未完成根因→数据看板→风险→下周计划→复盘 |
| 🎨 **自定义模板** | 粘贴一篇历史报告，AI 自动学习你的格式 |
| 💾 **自动回填** | 生成报告后自动保存到公司系统（仅草稿，不提交） |
| 📎 **多数据源** | 系统URL+账号 / 粘贴 / CSV / 飞书考勤 / 口头描述 |
| 🔌 **多平台** | Claude Code + Trae IDE 通用 |

## 目录结构

```
work-report/
├── SKILL.md                  # 核心 Skill 定义（含 API 探测协议）
├── README.md                 # 本文件
├── install.py                # 一键安装脚本
├── scripts/
│   ├── login_and_fetch.py    # 自动登录 + 数据拉取
│   └── save_report.py        # 自动回填日报/周报到系统
└── templates/
    └── custom-daily.md       # 用户自定义日报格式（示例）
```

## 对接你的公司系统

**已有系统：** 某消防行业公司 CRM 系统已适配，有现成脚本可参考。

**新系统：** Skill 内置了完整的 **API 自动探测协议**（SKILL.md Phase 2B Step 4），AI 会自动：

1. 抓取首页 HTML → 定位 JS 包
2. 搜索 `baseURL`、`client_id`、`client_secret`
3. 验证 OAuth2 登录接口
4. 探测数据查询/回填接口
5. 生成新的登录脚本

你只需提供系统 URL 和账号密码。

**安全提醒：** 脚本中只存客户端凭证（client_id/secret，来自前端 JS），**不存用户密码**。密码通过命令行传入。

## 支持平台

| 平台 | 安装路径 | 状态 |
|------|---------|------|
| Claude Code | `~/.claude/skills/work-report/` | ✅ 兼容 |
| Trae IDE | `~/.trae/skills/work-report/` | ✅ 兼容（v3.3.21+） |

## 许可

MIT
