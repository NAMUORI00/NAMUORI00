import os
import requests
import re

CATEGORIES = {
    "🧠 AI & Agentic Research": [
        "ai", "llm", "agent", "researcher", "scientist", "machine-learning",
        "deep-learning", "rag", "langchain", "openai", "huggingface",
        "pytorch", "transformer", "gpt", "gemini", "agentic",
    ],
    "🛠️ MCP & Dev Automation": [
        "mcp", "workflow", "automation", "n8n", "figma", "blender",
        "unity", "task-manager",
    ],
    "🎧 Voice, Media & Tools": [
        "voice", "audio", "music", "spleeter", "demucs", "osc",
        "vrchat", "whisper", "tts", "stt", "ytdlp", "mort",
        "media", "ffmpeg", "video",
    ],
    "🌐 Infra, Data & Viz": [
        "supabase", "grafana", "bokeh", "react", "chart", "diagram",
        "visualization", "docker", "kubernetes", "terraform",
        "obsidian", "quartz", "note", "typst",
    ],
}

def categorize(repo):
    """Try to categorize a repo by checking name + description against keywords."""
    text = f"{repo.get('full_name', '')} {repo.get('description', '')}".lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return cat
    return "💡 기타 관심사"

def main():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    USERNAME = "NAMUORI00"

    # Fetch recent 30 stars
    url = f"https://api.github.com/users/{USERNAME}/starred?per_page=30"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    stars = response.json()

    # Group by category, max 4 per category
    grouped = {}
    for repo in stars:
        cat = categorize(repo)
        if cat not in grouped:
            grouped[cat] = []
        if len(grouped[cat]) < 4:
            grouped[cat].append(repo)

    # Build markdown
    lines = []
    # Define category order
    cat_order = list(CATEGORIES.keys()) + ["💡 기타 관심사"]
    for cat in cat_order:
        repos = grouped.get(cat, [])
        if not repos:
            continue
        lines.append(f"<details>")
        lines.append(f"  <summary><b>{cat}</b></summary>")
        lines.append(f"")
        for repo in repos:
            name = repo["full_name"]
            url = repo["html_url"]
            desc = (repo.get("description") or "").replace("\n", " ").strip()
            if len(desc) > 80:
                desc = desc[:77] + "..."
            star_count = repo.get("stargazers_count", 0)
            star_str = f"⭐ {star_count:,}" if star_count > 0 else ""
            lines.append(f"  - [{name}]({url}) {star_str}<br/><sub>{desc}</sub>")
        lines.append(f"</details>")
        lines.append(f"")

    stars_md = "\n".join(lines)

    # Read and replace
    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"(<!-- START_SECTION:stars -->).*?(<!-- END_SECTION:stars -->)",
        f"\\1\n{stars_md}\\2",
        content,
        flags=re.DOTALL,
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Updated stars section with {len(stars)} repos in {len(grouped)} categories.")

if __name__ == "__main__":
    main()
