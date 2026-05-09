# GitHub AI高Star内容爬虫设计文档

## 概述

一个CLI工具，用于爬取GitHub上与AI相关的高star仓库，帮助用户关注最新的AI技术动态。

## 技术架构

采用Python + Go混合架构，发挥各自优势：
- **Python**：爬虫核心逻辑、API交互、数据解析、配置管理
- **Go**：并发调度、限流控制、高性能数据处理

## 项目结构

```
github-ai-scraper/
├── pyproject.toml          # Python项目配置
├── go.mod                  # Go模块配置
├── src/
│   └── ai_scraper/
│       ├── __init__.py
│       ├── cli.py          # CLI入口
│       ├── config.py       # 配置管理
│       ├── api/
│       │   ├── __init__.py
│       │   ├── github.py   # GitHub API客户端
│       │   └── rate_limiter.py  # API限流
│       ├── models/
│       │   ├── __init__.py
│       │   └── repository.py  # 数据模型
│       ├── storage/
│       │   ├── __init__.py
│       │   └── database.py    # SQLite操作
│       └── filters/
│           ├── __init__.py
│           └── ai_filter.py   # AI关键词/Topic过滤
├── cmd/
│   └── scheduler/           # Go高性能组件
│       ├── main.go          # 入口
│       ├── scheduler.go     # 并发调度
│       ├── limiter.go       # 令牌桶限流
│       └── processor.go     # 数据处理
├── data/
│   └── ai_scraper.db        # SQLite数据库（运行时生成）
└── docs/
    └── superpowers/
        └── specs/          # 设计文档
```

## 核心数据模型

### Repository（仓库信息）

```python
@dataclass
class Repository:
    id: int                      # GitHub仓库ID
    name: str                    # 仓库名 (owner/repo)
    full_name: str               # 完整名称
    description: Optional[str]   # 描述
    stars: int                   # Star数
    language: Optional[str]      # 主要语言
    topics: List[str]            # Topic标签列表
    created_at: datetime         # 创建时间
    updated_at: datetime         # 更新时间
    pushed_at: datetime          # 最后推送时间
    url: str                     # GitHub URL

    # 可选扩展字段（根据配置爬取）
    open_issues: Optional[int]   # Open Issues数
    forks: Optional[int]         # Fork数
    contributors: Optional[int]  # 贡献者数量
```

### RepoSnapshot（快照，用于趋势分析）

```python
@dataclass
class RepoSnapshot:
    repo_id: int
    stars: int
    snapshot_at: datetime        # 快照时间
```

### FilterConfig（筛选配置）

```python
@dataclass
class FilterConfig:
    min_stars: int = 100         # 最小Star数
    keywords: List[str]          # AI关键词列表
    topics: List[str]            # AI Topic列表
    languages: List[str]         # 语言过滤（可选）
    exclude_keywords: List[str]  # 排除关键词
```

### ScrapeConfig（爬取配置）

```python
@dataclass
class ScrapeConfig:
    data_fields: List[str]       # 需要爬取的字段
    max_results: int             # 最大结果数
    concurrency: int             # 并发数
    cache_ttl: int               # 缓存有效期（秒）
```

## Python核心模块

### GitHub API客户端 (`api/github.py`)

**职责：** 与GitHub REST API交互，获取仓库数据

```python
class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.session = aiohttp.ClientSession()
        self.token = token

    async def search_repositories(query: str, sort: str, order: str) -> List[Repository]:
        """搜索仓库"""

    async def get_repository(owner: str, repo: str) -> Repository:
        """获取单个仓库详情"""

    async def get_contributors(owner: str, repo: str) -> int:
        """获取贡献者数量"""

    async def get_rate_limit() -> RateLimitInfo:
        """获取API配额状态"""
```

**搜索策略：**
- 使用GitHub Search API：`q=stars:>100 topic:ai topic:machine-learning ...`
- 分页获取，支持断点续爬
- 自动处理API错误和重试

### AI过滤器 (`filters/ai_filter.py`)

**职责：** 判断仓库是否为AI相关

```python
class AIFilter:
    # 预设关键词（可配置扩展）
    DEFAULT_KEYWORDS = [
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "neural network", "llm", "gpt", "transformer", "nlp", "computer vision",
        "reinforcement learning", "pytorch", "tensorflow", "huggingface"
    ]

    # 预设Topic标签
    DEFAULT_TOPICS = [
        "ai", "machine-learning", "deep-learning", "neural-network",
        "natural-language-processing", "computer-vision", "llm", "gpt",
        "pytorch", "tensorflow", "huggingface", "openai", "langchain"
    ]

    def is_ai_related(repo: Repository, config: FilterConfig) -> bool:
        """判断是否AI相关：名称/描述匹配关键词 或 topics匹配"""

    def score_relevance(repo: Repository) -> float:
        """计算AI相关度评分（用于排序）"""
```

### 数据库存储 (`storage/database.py`)

**职责：** SQLite数据持久化

**表结构：**
```sql
-- 仓库主表
CREATE TABLE repositories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    full_name TEXT,
    description TEXT,
    stars INTEGER,
    language TEXT,
    topics TEXT,           -- JSON数组
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    pushed_at TIMESTAMP,
    url TEXT,
    open_issues INTEGER,
    forks INTEGER,
    contributors INTEGER,
    relevance_score REAL,
    first_seen_at TIMESTAMP,
    last_updated_at TIMESTAMP
);

-- 快照表（趋势分析）
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY,
    repo_id INTEGER,
    stars INTEGER,
    snapshot_at TIMESTAMP,
    FOREIGN KEY (repo_id) REFERENCES repositories(id)
);

-- 索引
CREATE INDEX idx_stars ON repositories(stars DESC);
CREATE INDEX idx_updated ON repositories(last_updated_at);
```

```python
class Database:
    def save_repository(repo: Repository) -> None:
        """保存或更新仓库"""

    def save_snapshot(repo_id: int, stars: int) -> None:
        """保存快照"""

    def get_trending(days: int = 7) -> List[TrendResult]:
        """获取趋势仓库（Star增长最快）"""

    def search_local(query: str) -> List[Repository]:
        """本地搜索"""
```

## Go高性能组件

### 并发调度器 (`scheduler.go`)

**职责：** 管理并发爬取任务，协调Python和Go之间的工作

```go
type Scheduler struct {
    maxWorkers    int
    taskQueue     chan Task
    resultQueue   chan Result
    rateLimiter   *TokenBucket
}

type Task struct {
    ID       string
    Type     string  // "search", "fetch", "process"
    Payload  map[string]interface{}
}

type Result struct {
    TaskID   string
    Success  bool
    Data     interface{}
    Error    error
}

func (s *Scheduler) Start() error           // 启动调度器
func (s *Scheduler) Submit(task Task)       // 提交任务
func (s *Scheduler) GetResults() []Result   // 获取结果
func (s *Scheduler) Shutdown()              // 优雅关闭
```

**工作流程：**
1. Python CLI启动，调用Go scheduler二进制
2. Python将爬取任务通过stdin/JSON传递给Go
3. Go调度器分配worker并发执行
4. 结果通过stdout返回给Python

### 令牌桶限流器 (`limiter.go`)

**职责：** 精确控制API请求频率，避免触发GitHub限制

```go
type TokenBucket struct {
    capacity     int       // 桶容量（最大请求数）
    tokens       int       // 当前令牌数
    refillRate   int       // 每秒补充令牌数
    refillPeriod time.Duration
    mutex        sync.Mutex
}

func (tb *TokenBucket) Wait(ctx context.Context) error  // 等待获取令牌
func (tb *TokenBucket) TryAcquire() bool                // 尝试获取（非阻塞）
func (tb *TokenBucket) SetRate(requestsPerHour int)     // 动态调整速率
```

**限流策略：**
- 无Token：60请求/小时 → 1请求/分钟
- 有Token：5000请求/小时 → ~83请求/分钟
- 可配置安全余量（如保留10%配额）

### 数据处理器 (`processor.go`)

**职责：** 高性能批量数据处理、趋势计算

```go
type Processor struct {
    db *sql.DB
}

// 批量计算Star增长趋势
func (p *Processor) CalculateTrends(repoIDs []int, days int) map[int]TrendResult

// 聚合统计（按语言、Topic分组）
func (p *Processor) AggregateStats(repos []Repository) AggregationResult

// 并行处理仓库数据
func (p *Processor) ProcessBatch(repos []Repository) error
```

### Python-Go通信机制

**方式：subprocess + JSON流**

```python
# Python端
import subprocess
import json

proc = subprocess.Popen(
    ['scheduler', '--config', config_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# 发送任务
task = {"id": "1", "type": "search", "payload": {...}}
proc.stdin.write((json.dumps(task) + "\n").encode())
proc.stdin.flush()

# 接收结果
result = json.loads(proc.stdout.readline())
```

## CLI命令设计

### 命令结构

```bash
# 基础命令
ai-scraper scrape                    # 执行爬取
ai-scraper scrape --config my.yaml   # 使用配置文件
ai-scraper scrape --min-stars 500    # 覆盖最小Star数

# 查看结果
ai-scraper list                      # 列出所有仓库
ai-scraper list --sort stars         # 按Star排序
ai-scraper list --lang python        # 按语言过滤
ai-scraper list --limit 20           # 限制数量

# 趋势分析
ai-scraper trending                  # 显示趋势仓库
ai-scraper trending --days 7         # 最近7天
ai-scraper trending --top 10         # Top 10

# 配置管理
ai-scraper config init               # 初始化配置文件
ai-scraper config set token xxx      # 设置GitHub Token
ai-scraper config show               # 显示当前配置

# 数据管理
ai-scraper db stats                  # 数据库统计
ai-scraper db clean --days 30        # 清理30天前的快照
ai-scraper db export --format csv    # 导出数据
```

### 输出格式

**表格输出（默认）：**
```
┌─────────────────────────────┬───────┬──────────┬─────────────────────┐
│ Name                        │ Stars │ Language │ Description         │
├─────────────────────────────┼───────┼──────────┼─────────────────────┤
│ openai/whisper              │ 58.2k │ Python   │ Robust Speech...    │
│ langchain-ai/langchain      │ 82.1k │ Python   │ Building applic...  │
│ ...                         │       │          │                     │
└─────────────────────────────┴───────┴──────────┴─────────────────────┘
```

**JSON输出（`--format json`）：**
```json
{
  "repositories": [
    {"name": "openai/whisper", "stars": 58200, ...}
  ],
  "total": 150,
  "scraped_at": "2026-05-09T10:30:00Z"
}
```

### 配置文件格式 (`ai-scraper.yaml`)

```yaml
# GitHub配置
github:
  token: ${GITHUB_TOKEN}  # 支持环境变量
  cache_ttl: 3600         # 缓存1小时

# 筛选配置
filter:
  min_stars: 100
  keywords:
    - ai
    - machine-learning
    - llm
  topics:
    - ai
    - machine-learning
  languages:
    - python
    - typescript
  exclude_keywords:
    - awesome
    - list

# 爬取配置
scrape:
  data_fields:
    - stars
    - language
    - topics
    - contributors
  max_results: 500
  concurrency: 5

# 数据库配置
database:
  path: ./data/ai_scraper.db

# Go组件配置
scheduler:
  enabled: true
  workers: 4
```

## 错误处理

### API错误
- 401 Unauthorized → 提示Token无效或过期
- 403 Rate Limited → 自动等待重置，显示剩余时间
- 503 Service Unavailable → 指数退避重试（最多3次）

### 网络错误
- 连接超时 → 重试并记录日志
- DNS解析失败 → 检查网络，提示用户

### 数据错误
- 解析失败 → 跳过该条目，记录警告
- 数据库写入失败 → 回滚事务，保留数据一致性

### Go组件错误
- 进程启动失败 → 降级为纯Python模式运行
- 通信超时 → 重启Go进程

## 测试策略

### Python测试
- 单元测试：API客户端、过滤器、数据库操作
- Mock GitHub API响应
- 使用pytest + pytest-asyncio

### Go测试
- 单元测试：调度器、限流器、处理器
- 基准测试：并发性能、内存占用
- 使用标准testing包

### 集成测试
- 端到端爬取流程
- Python-Go通信测试
- 使用测试数据库

## 项目依赖

### Python依赖
```
aiohttp>=3.9.0      # 异步HTTP客户端
click>=8.1.0        # CLI框架
pydantic>=2.0.0     # 数据验证
rich>=13.0.0        # 终端美化输出
pyyaml>=6.0         # 配置文件解析
aiosqlite>=0.19.0   # 异步SQLite
```

### Go依赖
```
github.com/mattn/go-sqlite3  # SQLite驱动
```

## 模块职责总结

| 模块 | 技术选型 | 职责 |
|------|----------|------|
| CLI入口 | Python + Click | 用户交互、命令解析 |
| API客户端 | Python + aiohttp | GitHub API调用 |
| 数据过滤 | Python | AI相关性判断 |
| 数据存储 | Python + SQLite | 持久化、查询 |
| 并发调度 | Go | 任务分发、worker管理 |
| 限流控制 | Go | 令牌桶算法 |
| 数据处理 | Go | 趋势计算、聚合统计 |
