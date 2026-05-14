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
