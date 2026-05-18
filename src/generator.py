import os
import re
from datetime import datetime, timezone
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader

from src.config import SITE_NAME, SITE_URL, SITE_DESC

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def format_date(dt):
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - dt
    if diff.days == 0:
        return "Today"
    if diff.days == 1:
        return "Yesterday"
    if diff.days < 7:
        return f"{diff.days} days ago"
    return dt.strftime("%b %d, %Y")

def parse_briefing(raw):
    if not raw:
        return None
    sections = []
    current_title = None
    current_items = []
    current_text = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        header_match = re.match(r"^[#*]*\s*([A-Z][A-Za-z\s/]+):?\s*$", line)
        if header_match:
            if current_title is not None:
                sections.append({
                    "title": current_title,
                    "items": current_items,
                    "text": " ".join(current_text),
                })
            current_title = header_match.group(1)
            current_items = []
            current_text = []
        elif line.startswith("-") or line.startswith("*"):
            item = line.lstrip("-* ").strip()
            current_items.append(item)
        else:
            current_text.append(line)
    if current_title is not None:
        sections.append({
            "title": current_title,
            "items": current_items,
            "text": " ".join(current_text),
        })
    return sections if sections else None

def generate(articles, briefing_raw=None):
    grouped = OrderedDict()
    seen_titles = set()
    for a in articles:
        key = a.get("source") or "General"
        if key not in grouped:
            grouped[key] = []
        a["date"] = format_date(a.get("published"))
        if a["title"] not in seen_titles:
            seen_titles.add(a["title"])
            a["content"] = a.get("ai_content") or a.get("summary_raw", "")
            grouped[key].append(a)

    env = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")))
    template = env.get_template("index.html")

    sources = list(grouped.keys())
    updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    briefing = parse_briefing(briefing_raw)

    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        site_desc=SITE_DESC,
        updated=updated,
        sources=sources,
        grouped=[(k, grouped[k]) for k in sources],
        briefing=briefing,
    )

    out_dir = os.path.join(HERE, "output")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {out_dir}\\index.html — {len(articles)} articles, {len(sources)} sources")
    total_kw = sum(len(a.get("keywords", [])) for a in articles)
    print(f"  {total_kw} keywords extracted")
    if briefing:
        print(f"  Executive briefing: {len(briefing)} sections")
