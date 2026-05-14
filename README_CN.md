# GitHub AI Scraper

[English](README.md) | 简体中文

一个用于从 GitHub 爬取 AI 相关高星仓库的 CLI 工具。

## 功能特性

- 搜索和筛选 AI 相关仓库（按关键词和主题）
- **动态关键词提取** - 自动从爬取的仓库中学习新关键词
- **Markdown/HTML/Excel/RSS 报告生成** - 多种导出格式
- **增量爬取** - 使用 `--since` 参数只获取更新的仓库
- **断点续爬** - 进度跟踪，支持恢复中断的爬取
- **进度条显示** - 爬取过程中可视化进度
- **并发爬取** - 并行请求，更快获取结果
- **多语言搜索** - 支持中文和英文关键词
- **交互式 CLI 模式** - 菜单驱动界面，降低使用门槛
- 本地 SQLite 存储，支持趋势分析
- 可配置的筛选和爬取选项
- GitHub API 令牌支持，智能限流
- 导出为 CSV/JSON/HTML/Excel/RSS 格式
- **REST API 服务** - 通过 HTTP 端点访问数据，可选认证
- **定时爬取** - 基于 Cron 的周期性爬取
- **Webhook 通知** - 事件发生时通知外部服务
- **插件系统** - 通过自定义插件扩展功能
- **仓库健康度评估** - 活跃度、流行度、维护度评分
- **智能分类** - LLM、CV、NLP、MLOps、AI Infrastructure 等类别
- **数据去重** - Fork 和镜像检测，内容相似度
- **安全令牌存储** - 加密存储敏感令牌
- **数据库备份** - 自动备份和恢复功能
- **错误恢复** - 指数退避重试机制

## 安装

```bash
# 从 PyPI 安装
pip install ai-scraper

# 或从源码安装（用于开发）
pip install -e ".[dev]"
```

## 快速开始

```bash
# 设置 GitHub 令牌（可选，可提高速率限制）
export GITHUB_TOKEN=your_token_here

# 爬取 AI 仓库
ai-scraper scrape

# 带进度条爬取
ai-scraper scrape --progress

# 并发爬取（更快）
ai-scraper scrape --concurrent

# 增量爬取（最近 7 天更新的仓库）
ai-scraper scrape --incremental
ai-scraper scrape --since 7d

# 恢复中断的爬取
ai-scraper scrape --resume

# 交互式模式
ai-scraper interactive

# 列出已爬取的仓库
ai-scraper list

# 显示趋势仓库
ai-scraper trending

# 导出数据
ai-scraper db export --format html --output index.html
ai-scraper db export --format xlsx --output repos.xlsx
ai-scraper db export --format rss --output feed.xml

# 启动 REST API 服务（带认证）
ai-scraper serve --port 8080 --auth

# 定时爬取（每天上午 9 点）
ai-scraper schedule --cron "0 9 * * *"

# 备份数据库
ai-scraper db backup
ai-scraper db restore backup_file.db.gz
```

## 配置

创建 `ai-scraper.yaml` 进行自定义配置：

```yaml
github:
  token: ${GITHUB_TOKEN}
  cache_ttl: 3600

filter:
  min_stars: 100
  keywords:
    - ai
    - machine-learning
    - 人工智能  # 中文关键词支持
  topics:
    - ai
    - deep-learning

scrape:
  max_results: 500
  concurrency: 5
  concurrent_requests: 5

database:
  path: ./data/ai_scraper.db
  backup_dir: ./backups
  max_backups: 10

api:
  auth_enabled: true
  api_keys:
    - as_your_api_key_here

webhooks:
  enabled: false
  endpoints:
    - url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
      events: [scrape_complete, trending_found]
```

## 命令列表

| 命令 | 描述 |
|---------|-------------|
| `ai-scraper scrape` | 从 GitHub 爬取 AI 仓库 |
| `ai-scraper scrape --concurrent` | 并发爬取，更快获取结果 |
| `ai-scraper scrape --incremental` | 增量爬取（仅更新的仓库） |
| `ai-scraper scrape --since 7d` | 爬取最近 7 天更新的仓库 |
| `ai-scraper scrape --resume` | 恢复中断的爬取 |
| `ai-scraper scrape --progress` | 爬取时显示进度条 |
| `ai-scraper interactive` | 启动交互式菜单模式 |
| `ai-scraper list` | 列出已爬取的仓库 |
| `ai-scraper trending` | 显示按星数增长的趋势仓库 |
| `ai-scraper serve` | 启动 REST API 服务 |
| `ai-scraper serve --auth` | 启动带认证的 API 服务 |
| `ai-scraper schedule` | 定时周期性爬取 |
| `ai-scraper keywords list` | 列出所有关键词 |
| `ai-scraper keywords extract` | 从数据库提取关键词 |
| `ai-scraper keywords clear` | 清除关键词 |
| `ai-scraper config init` | 初始化配置文件 |
| `ai-scraper config show` | 显示当前配置 |
| `ai-scraper db stats` | 显示数据库统计 |
| `ai-scraper db export` | 导出数据为 CSV/JSON/HTML/Excel/RSS |
| `ai-scraper db clean --invalid` | 删除无效数据的仓库 |
| `ai-scraper db clean --vacuum` | 优化数据库大小 |
| `ai-scraper db backup` | 创建数据库备份 |
| `ai-scraper db restore` | 从备份恢复 |
| `ai-scraper db backups` | 列出可用备份 |

## REST API 端点

运行 `ai-scraper serve` 时可访问：

| 端点 | 描述 |
|----------|-------------|
| `GET /api/repos` | 列出仓库（支持筛选） |
| `GET /api/repos/{id}` | 获取特定仓库 |
| `GET /api/stats` | 获取数据库统计 |
| `GET /api/trending` | 获取趋势仓库 |
| `GET /api/search?q=...` | 搜索仓库 |

认证：启用 `--auth` 时，传递 `X-API-Key` 头。

## 项目结构

```
github-ai-scraper/
├── src/ai_scraper/
│   ├── cli.py              # CLI 入口
│   ├── config.py           # 配置管理
│   ├── interactive.py      # 交互式菜单
│   ├── classifier.py       # 仓库分类系统
│   ├── dedup.py            # 去重工具
│   ├── health.py           # 健康度评估
│   ├── scheduler.py        # 任务调度
│   ├── webhooks.py         # Webhook 通知
│   ├── plugins.py          # 插件系统
│   ├── logging_config.py   # 日志配置
│   ├── api_server.py       # REST API 服务
│   ├── auth.py             # API 认证
│   ├── retry.py            # 错误恢复
│   ├── i18n.py             # 多语言支持
│   ├── scrape_progress.py  # 断点续爬
│   ├── backup.py           # 数据库备份
│   ├── config_watcher.py   # 配置热更新
│   ├── secure_storage.py   # 令牌加密
│   ├── api/
│   │   ├── github.py       # GitHub API 客户端
│   │   └── rate_limiter.py # 令牌桶限流器
│   ├── models/
│   │   └── repository.py   # 数据模型（Pydantic）
│   ├── filters/
│   │   └── ai_filter.py    # AI 相关性过滤器
│   ├── output/
│   │   ├── markdown.py     # Markdown 导出器
│   │   ├── html.py         # HTML 导出器
│   │   ├── excel.py        # Excel 导出器
│   │   └and rss.py          # RSS 导出器
│   └── storage/
│       ├── database.py     # SQLite 存储（同步）
│       └── async_database.py # SQLite 存储（异步）
├── plugins/                # 示例插件
├── tests/                  # 测试套件
├── Dockerfile              # Docker 支持
├── docker-compose.yml      # Docker Compose
├── .github/workflows/      # CI/CD 工作流
└── ai-scraper.yaml         # 默认配置
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 构建 Docker 镜像
docker build -t ai-scraper .
```

## API 速率限制

- 无令牌: 60 次/小时
- 有令牌: 5000 次/小时

设置 `GITHUB_TOKEN` 环境变量可获得更高的限制。

## 许可证

MIT