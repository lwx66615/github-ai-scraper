# GitHub AI Scraper 推广计划实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 PyPI 发布、GitHub 优化和内容推广，让更多用户发现和使用 ai-scraper

**Architecture:** 分三阶段执行：发布准备 → 正式发布 → 内容推广。Claude 负责代码修改和内容生成，用户负责账号注册、配置和社区发帖。

**Tech Stack:** Python, PyPI, GitHub Actions, Markdown

---

## 阶段 1：发布准备

### Task 1: 完善 pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: 添加项目元数据**

修改 `pyproject.toml`，在 `[project]` 部分添加以下内容：

```toml
[project]
name = "ai-scraper"
version = "0.1.0"
description = "A CLI tool for discovering and scraping AI-related high-star repositories from GitHub and GitLab"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    {name = "lwx66615"}
]
keywords = [
    "ai",
    "github",
    "scraper",
    "machine-learning",
    "cli",
    "gitlab",
    "repositories",
    "trending",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development",
    "Topic :: Utilities",
    "Typing :: Typed",
]
dependencies = [
    "aiohttp>=3.9.0",
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "aiosqlite>=0.19.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "croniter>=2.0.0",
]

[project.urls]
Homepage = "https://github.com/lwx66615/github-ai-scraper"
Repository = "https://github.com/lwx66615/github-ai-scraper"
Documentation = "https://github.com/lwx66615/github-ai-scraper#readme"
Issues = "https://github.com/lwx66615/github-ai-scraper/issues"
Changelog = "https://github.com/lwx66615/github-ai-scraper/releases"
```

- [ ] **Step 2: 提交更改**

```bash
git add pyproject.toml
git commit -m "chore: add project metadata for PyPI publishing"
```

---

### Task 2: 更新 README 安装说明

**Files:**
- Modify: `README.md`
- Modify: `README_CN.md`

- [ ] **Step 1: 更新英文 README 安装说明**

将 `README.md` 中的安装部分从：

```markdown
## Installation

```bash
pip install -e .
```
```

修改为：

```markdown
## Installation

```bash
# Install from PyPI
pip install ai-scraper

# Or install from source for development
pip install -e ".[dev]"
```
```

- [ ] **Step 2: 更新中文 README 安装说明**

将 `README_CN.md` 中的安装部分从：

```markdown
## 安装

```bash
pip install -e .
```
```

修改为：

```markdown
## 安装

```bash
# 从 PyPI 安装
pip install ai-scraper

# 或从源码安装（用于开发）
pip install -e ".[dev]"
```
```

- [ ] **Step 3: 提交更改**

```bash
git add README.md README_CN.md
git commit -m "docs: update installation instructions for PyPI"
```

---

### Task 3: 创建 Release Notes 模板

**Files:**
- Create: `RELEASE_NOTES.md`

- [ ] **Step 1: 创建 Release Notes 文件**

创建 `RELEASE_NOTES.md` 文件：

```markdown
# Release Notes for v0.1.0

## GitHub/GitLab AI Scraper

A CLI tool for discovering and scraping AI-related high-star repositories from GitHub and GitLab.

### Key Features

- **Ready to Use** - Install with `pip install ai-scraper` and start scraping immediately
- **AI-Focused** - Intelligent filtering and classification for AI repositories (LLM, CV, NLP, MLOps, etc.)
- **Automation Ready** - Scheduled scraping, webhook notifications, and trend analysis

### Highlights

- Multi-platform support: GitHub and GitLab (including self-hosted)
- Dynamic keyword extraction from scraped repositories
- Multiple export formats: Markdown, HTML, Excel, RSS
- Interactive CLI mode for easy navigation
- REST API server with optional authentication
- Repository health assessment and deduplication

### Installation

```bash
pip install ai-scraper
```

### Quick Start

```bash
# Set your GitHub token (optional, increases rate limit)
export GITHUB_TOKEN=your_token_here

# Scrape AI repositories
ai-scraper scrape

# Show trending repositories
ai-scraper trending

# Export to Markdown
ai-scraper db export --format markdown --output repos.md
```

### What's Next

- More AI classification categories
- Enhanced trend analysis
- Web UI interface

---

**Full Changelog**: https://github.com/lwx66615/github-ai-scraper/commits/v0.1.0
```

- [ ] **Step 2: 提交更改**

```bash
git add RELEASE_NOTES.md
git commit -m "docs: add release notes template for v0.1.0"
```

---

### Task 4: 创建中文文章大纲

**Files:**
- Create: `docs/promotion/chinese-article-outline.md`

- [ ] **Step 1: 创建文章大纲文件**

```markdown
# 中文文章大纲

## 标题
一行命令发现 GitHub 上的 AI 热门项目 - ai-scraper 开源工具介绍

## 一、痛点引入（200字）
- 手动浏览 GitHub 找 AI 项目效率低
- 信息分散，难以追踪趋势
- 想要定期关注但缺乏工具

## 二、ai-scraper 是什么（150字）
- 一句话介绍：CLI 工具，自动发现和爬取 AI 相关高星仓库
- 支持双平台：GitHub + GitLab
- 开源免费，MIT 协议

## 三、核心卖点（500字）

### 3.1 开箱即用
- pip install ai-scraper 直接安装
- 交互式模式，菜单驱动
- 无需配置即可使用

### 3.2 AI 领域专注
- 智能过滤 AI 相关仓库
- 自动分类：LLM、CV、NLP、MLOps、AI Infrastructure
- 动态关键词提取，自动学习新领域

### 3.3 自动化能力
- 定时爬取（Cron）
- Webhook 通知
- 趋势分析，发现新星项目

## 四、快速上手（300字）

```bash
# 安装
pip install ai-scraper

# 基本使用
ai-scraper scrape              # 爬取 AI 仓库
ai-scraper trending            # 查看趋势
ai-scraper db export --format markdown --output repos.md
```

## 五、进阶玩法（400字）

### 5.1 增量爬取
```bash
ai-scraper scrape --incremental
ai-scraper scrape --since 7d
```

### 5.2 REST API 服务
```bash
ai-scraper serve --port 8080
```

### 5.3 定时任务
```bash
ai-scraper schedule --cron "0 9 * * *"
```

### 5.4 导出报告
- Markdown（带中文翻译）
- HTML
- Excel
- RSS

## 六、实际应用场景（200字）
- 个人学习：追踪 AI 前沿项目
- 团队分享：定期生成报告
- 研究调研：发现相关领域项目

## 七、项目地址与号召（100字）
- GitHub: https://github.com/lwx66615/github-ai-scraper
- 欢迎 Star、Issue、PR
- 持续更新中

## 配图建议
1. CLI 使用截图（进度条展示）
2. 导出的 Markdown 报告截图
3. 趋势分析结果截图
```

- [ ] **Step 2: 提交更改**

```bash
git add docs/promotion/chinese-article-outline.md
git commit -m "docs: add Chinese article outline for promotion"
```

---

### Task 5: 创建英文文章大纲

**Files:**
- Create: `docs/promotion/english-article-outline.md`

- [ ] **Step 1: 创建文章大纲文件**

```markdown
# English Article Outline

## Title
Discover Trending AI Projects on GitHub with ai-scraper

## I. The Problem (150 words)
- Finding quality AI repositories is time-consuming
- GitHub trending is too broad, not AI-specific
- Hard to track projects over time
- No automated way to discover new projects

## II. What is ai-scraper? (100 words)
- A CLI tool for scraping AI-related repositories
- Supports both GitHub and GitLab
- Open source, MIT licensed
- Key stats: stars, activity, classification

## III. Key Features (400 words)

### Ready to Use
- Simple installation: `pip install ai-scraper`
- Interactive mode for beginners
- No complex setup required

### AI-Focused
- Intelligent filtering for AI repositories
- Auto-classification: LLM, CV, NLP, MLOps, AI Infrastructure
- Dynamic keyword extraction

### Automation Ready
- Scheduled scraping with cron
- Webhook notifications
- Trend analysis and star growth tracking

## IV. Quick Start (200 words)

```bash
# Install
pip install ai-scraper

# Basic usage
ai-scraper scrape              # Scrape AI repos
ai-scraper trending            # Show trending repos
ai-scraper list                # List all repos
```

## V. Advanced Usage (300 words)

### Incremental Scraping
```bash
ai-scraper scrape --incremental
ai-scraper scrape --since 7d
```

### REST API Server
```bash
ai-scraper serve --port 8080
# Access at http://localhost:8080/api/repos
```

### Export Options
```bash
ai-scraper db export --format markdown --output repos.md
ai-scraper db export --format html --output index.html
ai-scraper db export --format xlsx --output repos.xlsx
```

## VI. Use Cases (150 words)
- Personal learning: Track AI frontier projects
- Team sharing: Generate weekly reports
- Research: Discover projects in specific domains
- Content creation: Find trending topics

## VII. Call to Action (50 words)
- GitHub: https://github.com/lwx66615/github-ai-scraper
- Stars, Issues, and PRs welcome!
- Actively maintained

## Suggested Images
1. CLI screenshot with progress bar
2. Markdown report sample
3. Trending repos output
```

- [ ] **Step 2: 提交更改**

```bash
git add docs/promotion/english-article-outline.md
git commit -m "docs: add English article outline for promotion"
```

---

### Task 6: 推送更改到远程仓库

- [ ] **Step 1: 推送所有提交**

```bash
git push origin master
```

---

## 阶段 2：正式发布（用户操作）

### Task 7: 用户注册 PyPI 账号

**执行者：用户**

- [ ] **Step 1: 注册 PyPI 账号**

1. 访问 https://pypi.org/account/register/
2. 填写用户名、邮箱、密码
3. 验证邮箱

- [ ] **Step 2: 创建 API Token**

1. 登录 PyPI
2. 进入 Account settings → API tokens
3. 点击 "Add API token"
4. 选择 "Entire account (all projects)"
5. 复制生成的 Token（格式：`pypi-...`）

**重要：Token 只显示一次，请妥善保存**

---

### Task 8: 用户配置 GitHub Secret

**执行者：用户**

- [ ] **Step 1: 添加 PYPI_TOKEN Secret**

1. 打开 https://github.com/lwx66615/github-ai-scraper/settings/secrets/actions
2. 点击 "New repository secret"
3. Name: `PYPI_TOKEN`
4. Value: 粘贴 PyPI API Token
5. 点击 "Add secret"

---

### Task 9: 用户添加 GitHub Topics

**执行者：用户**

- [ ] **Step 1: 添加仓库 Topics**

1. 打开 https://github.com/lwx66615/github-ai-scraper
2. 点击仓库描述下方的 "Topics" 编辑按钮（齿轮图标）
3. 添加以下 Topics：
   - `ai`
   - `github-api`
   - `scraper`
   - `machine-learning`
   - `python`
   - `cli-tool`
4. 点击 "Save"

---

### Task 10: 创建 v0.1.0 Release

**执行者：Claude 协助，用户确认**

- [ ] **Step 1: 创建 git tag**

```bash
git tag -a v0.1.0 -m "Release v0.1.0: First public release"
git push origin v0.1.0
```

- [ ] **Step 2: 在 GitHub 创建 Release**

1. 打开 https://github.com/lwx66615/github-ai-scraper/releases/new
2. 选择 tag: `v0.1.0`
3. Release title: `v0.1.0 - First Public Release`
4. Description: 复制 `RELEASE_NOTES.md` 内容
5. 点击 "Publish release"

- [ ] **Step 3: 等待 CI 完成**

GitHub Actions 会自动构建并发布到 PyPI。
查看进度：https://github.com/lwx66615/github-ai-scraper/actions

---

### Task 11: 验证 PyPI 发布

- [ ] **Step 1: 验证安装**

```bash
# 在全新环境中测试
pip install ai-scraper
ai-scraper --help
ai-scraper scrape --help
```

预期输出：显示帮助信息，无报错

- [ ] **Step 2: 验证 PyPI 页面**

访问 https://pypi.org/project/ai-scraper/
确认页面显示正常，描述和链接正确

---

## 阶段 3：内容推广（用户操作为主）

### Task 12: 用户撰写并发布中文文章

**执行者：用户**

- [ ] **Step 1: 撰写文章**

参考 `docs/promotion/chinese-article-outline.md` 撰写文章

- [ ] **Step 2: 发布到掘金**

1. 登录 https://juejin.cn/
2. 发布文章
3. 标签：`开源`, `GitHub`, `AI`, `Python`

- [ ] **Step 3: 同步到知乎**

1. 登录 https://zhuanlan.zhihu.com/
2. 发布文章
3. 话题：`开源项目`, `GitHub`, `人工智能`

---

### Task 13: 用户撰写并发布英文文章

**执行者：用户**

- [ ] **Step 1: 撰写文章**

参考 `docs/promotion/english-article-outline.md` 撰写文章

- [ ] **Step 2: 发布到 Dev.to**

1. 登录 https://dev.to/
2. 发布文章
3. Tags: `python`, `github`, `ai`, `opensource`, `cli`

---

### Task 14: 用户提交 Awesome 列表

**执行者：用户**

- [ ] **Step 1: 提交到 awesome-ai**

1. Fork https://github.com/owainlewis/awesome-ai
2. 在 README.md 中添加：
   `- [ai-scraper](https://github.com/lwx66615/github-ai-scraper) - CLI tool for discovering AI repos on GitHub`
3. 提交 PR

- [ ] **Step 2: 提交到 awesome-machine-learning**

1. Fork https://github.com/josephmisiti/awesome-machine-learning
2. 在合适分类下添加项目链接
3. 提交 PR

- [ ] **Step 3: 提交到 awesome-python**

1. Fork https://github.com/vinta/awesome-python
2. 在 "Command-line Tools" 分类下添加项目链接
3. 提交 PR

---

### Task 15: 用户社区分享

**执行者：用户**

- [ ] **Step 1: V2EX 发帖**

1. 登录 https://www.v2ex.com/
2. 选择"分享"节点
3. 发布项目介绍，附上文章链接

- [ ] **Step 2: Hacker News Show HN**

1. 登录 https://news.ycombinator.com/
2. 提交 Show HN: ai-scraper - CLI tool for discovering AI repos
3. 附上 GitHub 链接

- [ ] **Step 3: Reddit 发帖**

1. 在 r/Python 发帖介绍项目
2. 在 r/MachineLearning 发帖介绍项目

---

## 检查清单

### 发布前检查
- [ ] pyproject.toml 已完善
- [ ] README 安装说明已更新
- [ ] Release Notes 已准备
- [ ] 所有更改已推送到 GitHub

### 发布后检查
- [ ] PyPI 页面正常显示
- [ ] `pip install ai-scraper` 安装成功
- [ ] CLI 命令正常运行
- [ ] GitHub Topics 已添加

### 推广检查
- [ ] 中文文章已发布
- [ ] 英文文章已发布
- [ ] 至少 1 个 Awesome 列表已收录
- [ ] 社区分享已完成

---

## 成功指标

- PyPI 发布成功，用户可正常安装
- 首周 GitHub star 增长 > 50
- 至少 2 篇文章发布并获得阅读量
- 至少 1 个 Awesome 列表收录
