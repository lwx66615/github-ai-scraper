"""Markdown exporter for generating beautiful reports."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from ai_scraper.models import Repository
from ai_scraper.output.translator import translate_description


# 分类映射（英文 -> 中文）
CATEGORY_NAMES = {
    "LLM": "大语言模型",
    "Chatbot": "聊天机器人",
    "Generative AI": "生成式 AI",
    "Computer Vision": "计算机视觉",
    "NLP": "自然语言处理",
    "Machine Learning": "机器学习",
    "Deep Learning": "深度学习",
    "MLOps": "机器学习运维",
    "AI Infrastructure": "AI 基础设施",
    "AI Ethics": "AI 伦理",
    "Reinforcement Learning": "强化学习",
    "Robotics": "机器人",
    "AutoML": "自动化机器学习",
    "Data Science": "数据科学",
    "AI Tools": "AI 工具",
    "Other": "其他",
}

# 语言图标
LANGUAGE_ICONS = {
    "Python": "🐍",
    "TypeScript": "📘",
    "JavaScript": "💛",
    "Java": "☕",
    "Go": "🐹",
    "Rust": "🦀",
    "C++": "⚡",
    "C": "⚙️",
    "Jupyter Notebook": "📊",
    "HTML": "🌐",
    "CSS": "🎨",
    "Ruby": "💎",
    "PHP": "🐘",
    "Swift": "🍎",
    "Kotlin": "🎯",
    "Lua": "🌙",
    "Shell": "🖥️",
    "Dart": "🎯",
    "Scala": "🔴",
    "R": "📈",
    "MATLAB": "📐",
    "Julia": "💜",
    "Haskell": "λ",
    "Elixir": "💧",
    "Clojure": "🧬",
    "F#": "🔷",
    "OCaml": "🐫",
    "Nim": "👑",
    "Crystal": "💎",
    "Elm": "🌳",
    "V": "⚡",
    "Zig": "⚡",
    "Nim": "👑",
}

# 热门程度图标
STAR_LEVELS = [
    (100000, "🔥🔥🔥🔥🔥", "超热门"),
    (50000, "🔥🔥🔥🔥", "非常热门"),
    (10000, "🔥🔥🔥", "热门"),
    (5000, "🔥🔥", "较热门"),
    (1000, "🔥", "值得关注"),
    (0, "⭐", "新星"),
]


class MarkdownExporter:
    """Export repositories to beautiful Markdown format."""

    def __init__(self, output_dir: Path, filename: str = "repositories.md"):
        """Initialize the exporter.

        Args:
            output_dir: Directory for output files.
            filename: Name of the output file.
        """
        self.output_dir = Path(output_dir)
        self.filename = filename

    def export_repositories(self, repos: list[Repository]) -> Path:
        """Export repositories to a Markdown file.

        Args:
            repos: List of repositories to export.

        Returns:
            Path to the created file.
        """
        # Create output directory if needed
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate content
        content = self._generate_content(repos)

        # Write file
        output_path = self.output_dir / self.filename
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def _generate_content(self, repos: list[Repository]) -> str:
        """Generate the full Markdown content."""
        lines = []

        lines.append("# AI Repositories")
        lines.append("")
        lines.append(f"**更新时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**总计:** {len(repos)} 个仓库")
        lines.append("")
        lines.append("| Name | Stars | Language | Description | URL |")
        lines.append("|------|-------|----------|-------------|-----|")

        for repo in repos:
            name = repo.full_name
            stars = f"{repo.stars:,}"
            language = repo.language or "-"
            description = self._clean_description(repo.description)
            url = f"[GitHub]({repo.url})"
            lines.append(f"| {name} | {stars} | {language} | {description} | {url} |")

        return "\n".join(lines)

    def _format_repo_card(self, repo: Repository) -> str:
        """Format a single repository as a beautiful card.

        Args:
            repo: Repository to format.

        Returns:
            Markdown formatted card.
        """
        lang_icon = LANGUAGE_ICONS.get(repo.language or "", "📁")
        star_level = self._get_star_level(repo.stars)

        # 项目标题
        title = f"### [{repo.full_name}]({repo.url})"
        subtitle = f"{lang_icon} {repo.language or '未知'} | {star_level[0]} {self._format_number(repo.stars)} Stars | {star_level[1]}"

        lines = []
        lines.append(title)
        lines.append("")
        lines.append(f"**{subtitle}**")
        lines.append("")

        # 描述 - 原文和中文翻译
        original_desc = self._clean_description(repo.description, 200)
        translated_desc = translate_description(repo.description)

        # 如果翻译后不同，显示双语
        if translated_desc != original_desc and translated_desc != (repo.description or "暂无描述"):
            lines.append(f"> {original_desc}")
            lines.append(f"> ")
            lines.append(f"> **中文:** {translated_desc}")
        else:
            lines.append(f"> {original_desc}")
        lines.append("")

        # Topics 标签
        if repo.topics:
            topics_display = " ".join(f"`{topic}`" for topic in repo.topics[:8])
            lines.append(f"**标签:** {topics_display}")

        return "\n".join(lines)

    def _group_by_stars(self, repos: list[Repository]) -> list[tuple[str, list[Repository]]]:
        """Group repositories by star count.

        Args:
            repos: List of repositories.

        Returns:
            List of (group_name, repos) tuples.
        """
        groups = [
            ("🔥 超热门项目 (100K+ Stars)", []),
            ("🌟 热门项目 (50K-100K Stars)", []),
            ("⭐ 优质项目 (10K-50K Stars)", []),
            ("💡 新兴项目 (1K-10K Stars)", []),
            ("🌱 新星项目 (<1K Stars)", []),
        ]

        for repo in repos:
            if repo.stars >= 100000:
                groups[0][1].append(repo)
            elif repo.stars >= 50000:
                groups[1][1].append(repo)
            elif repo.stars >= 10000:
                groups[2][1].append(repo)
            elif repo.stars >= 1000:
                groups[3][1].append(repo)
            else:
                groups[4][1].append(repo)

        return groups

    def _get_star_level(self, stars: int) -> tuple[str, str]:
        """Get star level icon and description.

        Args:
            stars: Star count.

        Returns:
            (icon, description) tuple.
        """
        for threshold, icon, desc in STAR_LEVELS:
            if stars >= threshold:
                return (icon, desc)
        return ("⭐", "新星")

    def _format_number(self, num: int) -> str:
        """Format large numbers with K/M suffix.

        Args:
            num: Number to format.

        Returns:
            Formatted string.
        """
        if num >= 1000000:
            return f"{num / 1000000:.1f}M"
        elif num >= 1000:
            return f"{num / 1000:.1f}K"
        return str(num)

    def _get_language_stats(self, repos: list[Repository]) -> dict[str, int]:
        """Get language distribution statistics.

        Args:
            repos: List of repositories.

        Returns:
            Dictionary of language counts.
        """
        stats = {}
        for repo in repos:
            lang = repo.language or "Unknown"
            stats[lang] = stats.get(lang, 0) + 1
        return stats

    def _generate_language_chart(self, languages: dict[str, int]) -> str:
        """Generate a simple text-based language distribution chart.

        Args:
            languages: Language statistics.

        Returns:
            Markdown formatted chart.
        """
        # Sort by count
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]

        lines = []
        for lang, count in sorted_langs:
            icon = LANGUAGE_ICONS.get(lang, "📁")
            bar_len = min(20, int(count / max(languages.values()) * 20))
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"| {icon} {lang or '未知'} | `{bar}` | {count} |")

        return "\n".join(lines)

    def _clean_description(self, description: Optional[str], max_len: int = 50) -> str:
        """Clean description for display.

        Args:
            description: Original description.
            max_len: Maximum length.

        Returns:
            Cleaned description.
        """
        if description is None:
            return ""

        # Remove newlines and collapse spaces
        cleaned = " ".join(description.split())

        # Escape pipe characters
        cleaned = cleaned.replace("|", r"\|")

        # Truncate if needed
        if len(cleaned) > max_len:
            cleaned = cleaned[:max_len] + "..."

        return cleaned