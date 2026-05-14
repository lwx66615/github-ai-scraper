# GitHub AI Scraper 推广计划设计文档

## 背景

GitHub AI Scraper 是一个用于爬取 AI 相关高星仓库的 CLI 工具，功能完善但尚未发布到 PyPI，用户只能通过本地安装使用。需要制定推广计划让更多人发现和使用该项目。

## 目标

- 让用户能直接通过 `pip install ai-scraper` 安装使用
- 在技术社区获得关注和用户
- 建立 GitHub star 基础

## 目标受众

双语并行推广：
- 中文用户：掘金、知乎、V2EX
- 英文用户：Hacker News、Reddit、Dev.to

## 核心卖点

1. **开箱即用** — 简单安装即可使用，交互式模式降低门槛
2. **AI 领域专注** — 专为发现 AI 热门项目设计，智能分类和过滤
3. **自动化能力** — 定时爬取、Webhook 通知、趋势分析

## 推广方案：发布优先型

核心思路：先完成 PyPI 发布，让用户能直接安装，再逐步完善其他渠道。

### 整体计划结构

```
阶段 1：发布准备（1-2天）
├── 1.1 PyPI 账号注册与配置
├── 1.2 完善 pyproject.toml
├── 1.3 GitHub 仓库优化
└── 1.4 创建 v0.1.0 Release

阶段 2：正式发布（1天）
├── 2.1 发布到 PyPI
├── 2.2 验证安装可用性
└── 2.3 GitHub Release 发布

阶段 3：内容推广（3-5天）
├── 3.1 撰写中文文章（掘金/知乎）
├── 3.2 撰写英文文章（Dev.to/Medium）
├── 3.3 提交 Awesome 列表
├── 3.4 社区分享（V2EX/Hacker News/Reddit）
└── 3.5 持续监控与反馈
```

预计总时长：5-8 天

---

## 阶段 1：发布准备

### 1.1 PyPI 账号注册与配置

| 任务 | 说明 |
|------|------|
| 注册 PyPI 账号 | 访问 pypi.org 注册，需要邮箱验证 |
| 创建 API Token | 登录后进入 Account settings → API tokens → Add API token |
| 配置 GitHub Secret | 在仓库 Settings → Secrets → Actions 添加 `PYPI_TOKEN` |

### 1.2 完善 pyproject.toml

需要添加的内容：
- `description`：更详细的项目描述
- `keywords`：`ai`, `github`, `scraper`, `machine-learning`, `cli`
- `classifiers`：Python 版本、许可证、开发状态等
- `urls`：Homepage、Repository、Documentation 链接

### 1.3 GitHub 仓库优化

| 任务 | 说明 |
|------|------|
| 添加 Topics | `ai`, `github-api`, `scraper`, `machine-learning`, `python`, `cli-tool` |
| 完善 About | 添加项目描述和官网链接 |
| 添加演示 GIF | 录制 CLI 使用过程（可选但推荐） |

### 1.4 创建 v0.1.0 Release

- 打 git tag `v0.1.0`
- 在 GitHub 创建 Release，编写 Release Notes
- 自动触发 CI 发布到 PyPI

---

## 阶段 2：正式发布

### 2.1 发布到 PyPI

通过 GitHub Release 自动触发：
- Release workflow 已配置好，会自动构建并上传到 PyPI
- 需确保 `PYPI_TOKEN` Secret 已正确配置

### 2.2 验证安装可用性

发布后验证步骤：
```bash
# 在全新环境中测试
pip install ai-scraper
ai-scraper --help
ai-scraper scrape --help
```

### 2.3 GitHub Release 发布

Release Notes 内容建议：
- 简要介绍项目功能
- 列出主要特性（突出开箱即用、AI 专注、自动化）
- 安装命令：`pip install ai-scraper`
- 快速开始示例
- 致谢和后续计划

---

## 阶段 3：内容推广

### 3.1 中文文章（掘金/知乎）

**文章大纲**：
- 标题：《一行命令发现 GitHub 上的 AI 热门项目 - ai-scraper 开源工具介绍》
- 痛点：手动找 AI 项目效率低、信息分散、难以追踪趋势
- 解决方案：ai-scraper 的三大卖点
- 快速上手：安装 + 基本使用示例
- 进阶玩法：定时爬取、REST API、导出报告
- 项目地址和 Star 号召

**发布平台**：掘金（优先）、知乎专栏、微信公众号

### 3.2 英文文章

**文章大纲**：
- Title: "Discover Trending AI Projects on GitHub with ai-scraper"
- Problem: Finding quality AI repos is time-consuming
- Solution: ai-scraper features and benefits
- Quick Start: Installation and basic usage
- Advanced Features: Scheduling, API, exports
- Call to action: GitHub repo link

**发布平台**：Dev.to（优先）、Medium

### 3.3 提交 Awesome 列表

目标列表（按优先级）：
1. awesome-ai
2. awesome-machine-learning
3. awesome-python
4. awesome-cli-apps

提交方式：通过 PR 添加项目链接和简短描述

### 3.4 社区分享

| 平台 | 内容形式 | 时机 |
|------|----------|------|
| V2EX | 分享节点发帖 | 中文文章发布后 |
| Hacker News | Show HN | 英文文章发布后 |
| Reddit | r/MachineLearning, r/Python | 英文文章发布后 |
| Twitter/X | 简短介绍 + 链接 | 发布当天 |

### 3.5 指导步骤

#### PyPI 注册步骤

1. 访问 https://pypi.org/account/register/
2. 填写用户名、邮箱、密码
3. 验证邮箱
4. 登录后进入 Account settings → API tokens
5. 点击 "Add API token"，选择 "Entire account (all projects)"
6. 复制生成的 Token（格式：`pypi-...`）

#### GitHub Secret 配置步骤

1. 打开 https://github.com/lwx66615/github-ai-scraper/settings/secrets/actions
2. 点击 "New repository secret"
3. Name: `PYPI_TOKEN`
4. Value: 粘贴 PyPI API Token
5. 点击 "Add secret"

#### GitHub Topics 添加步骤

1. 打开 https://github.com/lwx66615/github-ai-scraper
2. 点击仓库描述下方的 "Topics" 编辑按钮（齿轮图标）
3. 添加以下 Topics：`ai`, `github-api`, `scraper`, `machine-learning`, `python`, `cli-tool`
4. 点击 "Save"

#### Awesome 列表提交步骤

1. 找到目标 awesome 列表的 GitHub 仓库
2. Fork 该仓库
3. 在 README.md 中找到合适位置添加项目链接
4. 格式：`[ai-scraper](https://github.com/lwx66615/github-ai-scraper) - CLI tool for discovering AI repos on GitHub`
5. 提交 PR，说明项目为何适合加入该列表

---

## 任务分工

| 任务类型 | 执行者 |
|----------|--------|
| 代码修改、配置文件更新 | Claude 执行 |
| 账号注册、Secret 配置 | 用户操作 |
| 文章撰写 | 用户撰写，Claude 提供大纲 |
| 社区发帖 | 用户操作 |
| 验证测试 | Claude 协助 |

---

## 成功指标

- PyPI 发布成功，用户可正常安装
- 首周 GitHub star 增长 > 50
- 至少 2 篇文章发布并获得阅读量
- 至少 1 个 Awesome 列表收录