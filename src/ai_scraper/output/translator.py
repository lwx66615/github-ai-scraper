"""Simple translation module for repository descriptions."""

import re
from typing import Optional


# 常见 AI 项目关键词翻译字典（按优先级排序）
TRANSLATION_DICT = {
    # 完整短语优先翻译
    "production-ready platform": "生产就绪的平台",
    "personal ai assistant": "个人 AI 助手",
    "workflow automation platform": "工作流自动化平台",
    "ai coding assistant": "AI 编程助手",
    "coding assistant": "编程助手",
    "code generation": "代码生成",
    "image generation": "图像生成",
    "text generation": "文本生成",
    "speech recognition": "语音识别",
    "speech synthesis": "语音合成",
    "face recognition": "人脸识别",
    "object detection": "物体检测",
    "natural language processing": "自然语言处理",
    "large language model": "大语言模型",
    "machine learning": "机器学习",
    "deep learning": "深度学习",
    "neural network": "神经网络",
    "computer vision": "计算机视觉",
    "reinforcement learning": "强化学习",
    "generative ai": "生成式 AI",
    "artificial intelligence": "人工智能",
    "retrieval-augmented generation": "检索增强生成",
    "stable diffusion": "Stable Diffusion",
    "web ui": "网页界面",
    "webui": "网页界面",
    "open source": "开源",
    "open-source": "开源",
    "self-host": "自托管",
    "self-hosted": "自托管",
    "production-ready": "生产就绪",
    "user-friendly": "用户友好",
    "cross-platform": "跨平台",
    "real-time": "实时",
    "high performance": "高性能",
    "lightweight": "轻量级",
    "knowledge base": "知识库",
    "workflow automation": "工作流自动化",
    "image upscaling": "图像放大",
    "face swap": "换脸",
    "video generation": "视频生成",
    "text to image": "文本生成图像",
    "text to speech": "文本转语音",
    "speech to text": "语音转文本",
    "language model": "语言模型",
    "vision model": "视觉模型",
    "multimodal": "多模态",
    "getting started": "入门",
    "get started": "入门",
    "best practices": "最佳实践",
    "awesome list": "精选列表",
    "awesome": "精选",
    "alternative to": "...的替代方案",
    "next generation": "下一代",
    "next-gen": "下一代",
    "powered by": "基于",
    "based on": "基于",
    "built with": "使用...构建",
    "written in": "使用...编写",
    "designed for": "专为...设计",
    "easy to use": "易于使用",
    "free and open source": "免费开源",

    # AI 相关术语
    "llm": "大语言模型",
    "nlp": "自然语言处理",
    "chatbot": "聊天机器人",
    "chatgpt": "ChatGPT",
    "gpt": "GPT",
    "transformer": "Transformer",
    "diffusion": "扩散模型",
    "rag": "检索增强生成",
    "embedding": "嵌入",
    "vector": "向量",
    "prompt": "提示词",
    "prompts": "提示词",
    "agent": "代理",
    "agents": "代理",
    "assistant": "助手",
    "conversation": "对话",
    "conversational": "对话式",
    "context": "上下文",
    "memory": "记忆",
    "reasoning": "推理",
    "planning": "规划",
    "autonomous": "自主",
    "intelligent": "智能",
    "smart": "智能",

    # 技术术语
    "framework": "框架",
    "platform": "平台",
    "toolkit": "工具包",
    "library": "库",
    "api": "API",
    "sdk": "SDK",
    "cli": "命令行工具",
    "gui": "图形界面",
    "dashboard": "仪表盘",
    "interface": "界面",
    "workflow": "工作流",
    "automation": "自动化",
    "integration": "集成",
    "pipeline": "管道",
    "orchestration": "编排",
    "deployment": "部署",
    "training": "训练",
    "fine-tuning": "微调",
    "inference": "推理",
    "model": "模型",
    "models": "模型",
    "database": "数据库",
    "storage": "存储",
    "search": "搜索",
    "retrieval": "检索",
    "document": "文档",
    "pdf": "PDF",
    "markdown": "Markdown",
    "server": "服务器",
    "client": "客户端",
    "backend": "后端",
    "frontend": "前端",
    "service": "服务",
    "services": "服务",
    "endpoint": "端点",
    "request": "请求",
    "response": "响应",

    # 动词
    "build": "构建",
    "building": "构建",
    "create": "创建",
    "develop": "开发",
    "deploy": "部署",
    "run": "运行",
    "manage": "管理",
    "analyze": "分析",
    "process": "处理",
    "generate": "生成",
    "extract": "提取",
    "convert": "转换",
    "scrape": "抓取",
    "crawl": "爬取",
    "monitor": "监控",
    "track": "追踪",
    "visualize": "可视化",
    "optimize": "优化",
    "scale": "扩展",
    "integrate": "集成",
    "connect": "连接",
    "support": "支持",
    "supports": "支持",

    # 形容词
    "simple": "简单",
    "fast": "快速",
    "efficient": "高效",
    "powerful": "强大",
    "flexible": "灵活",
    "extensible": "可扩展",
    "modular": "模块化",
    "customizable": "可定制",
    "scalable": "可扩展",
    "robust": "稳健",
    "secure": "安全",
    "privacy": "隐私",
    "free": "免费",
    "modern": "现代",
    "latest": "最新",

    # 名词
    "developer": "开发者",
    "developers": "开发者",
    "user": "用户",
    "users": "用户",
    "team": "团队",
    "organization": "组织",
    "enterprise": "企业",
    "business": "商业",
    "application": "应用",
    "applications": "应用",
    "project": "项目",
    "projects": "项目",
    "repository": "仓库",
    "code": "代码",
    "data": "数据",
    "file": "文件",
    "files": "文件",
    "community": "社区",
    "resources": "资源",
    "tools": "工具",
    "utilities": "实用工具",
    "extensions": "扩展",
    "plugins": "插件",
    "tutorial": "教程",
    "documentation": "文档",
    "examples": "示例",
    "demo": "演示",
    "sample": "示例",
    "template": "模板",
    "benchmark": "基准测试",
    "testing": "测试",
    "experiment": "实验",
    "research": "研究",
    "education": "教育",
    "learning": "学习",
    "course": "课程",
    "lesson": "课程",
    "roadmap": "路线图",
    "guide": "指南",
    "handbook": "手册",
    "collection": "合集",
    "list": "列表",
    "curated": "精选",
    "version": "版本",
    "release": "发布",
    "update": "更新",
    "feature": "功能",
    "features": "功能",
    "capability": "能力",
    "capabilities": "能力",
    "functionality": "功能",
    "component": "组件",
    "module": "模块",
    "package": "包",
}


def translate_description(description: Optional[str]) -> str:
    """Translate repository description to Chinese.

    Uses a dictionary-based approach for common AI terms.
    For descriptions that are already in Chinese, returns as-is.
    For mixed content, preserves readability.

    Args:
        description: Original English description.

    Returns:
        Translated description with Chinese terms mixed naturally.
    """
    if description is None:
        return "暂无描述"

    # Check if already contains significant Chinese characters
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', description)
    if len(chinese_chars) > len(description) * 0.3:  # More than 30% Chinese
        return description

    # Clean the description
    cleaned = " ".join(description.split())

    # Don't translate if it's very short (likely a name or brand)
    if len(cleaned) < 20:
        return cleaned

    # Sort by length (longest first) to avoid partial matches
    sorted_terms = sorted(TRANSLATION_DICT.keys(), key=len, reverse=True)

    translated = cleaned
    for term in sorted_terms:
        # Case-insensitive replacement, but preserve word boundaries
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        if pattern.search(translated):
            translated = pattern.sub(TRANSLATION_DICT[term], translated)

    # Clean up any leftover English fragments that make it awkward
    # Remove awkward patterns like "代理ic" -> "代理"
    translated = re.sub(r'代理ic', '代理', translated)
    translated = re.sub(r'开发ment', '开发', translated)
    translated = re.sub(r'集成s', '集成', translated)
    translated = re.sub(r'构建ing', '构建', translated)
    translated = re.sub(r'分析er', '分析器', translated)
    translated = re.sub(r'生成ive', '生成式', translated)

    # If translation made it worse (too many fragments), return original
    chinese_ratio = len(re.findall(r'[\u4e00-\u9fff]', translated)) / max(len(translated), 1)
    if 0.1 < chinese_ratio < 0.3:
        # Partial translation, might be awkward - return original
        return description

    return translated


def get_bilingual_description(description: Optional[str]) -> tuple[str, str]:
    """Get both original and translated description.

    Args:
        description: Original description.

    Returns:
        (original, translated) tuple.
    """
    original = description or "暂无描述"
    translated = translate_description(description)

    # If translation is same as original (no changes), don't duplicate
    if original == translated:
        return (original, "")

    return (original, translated)