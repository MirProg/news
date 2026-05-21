import os
import json
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
    diff = datetime.now(timezone.utc) - dt
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

def generate(articles, briefing_raw=None, mashups=None):
    grouped = OrderedDict()
    seen_titles = set()
    for i, a in enumerate(articles):
        key = a.get("source") or "General"
        if key not in grouped:
            grouped[key] = []
        a["date"] = format_date(a.get("published"))
        if a["title"] not in seen_titles:
            seen_titles.add(a["title"])
            a["summary"] = a.get("ai_content") or a.get("summary_raw", "")
            grouped[key].append(a)

    env = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")))
    template = env.get_template("index.html")

    flat = []
    for items in grouped.values():
        flat.extend(items)

    updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    briefing = parse_briefing(briefing_raw)

    articles_out = []
    for i, a in enumerate(flat):
        entry = {
            "id": i,
            "title": a["title"],
            "source": a.get("source", ""),
            "url": a.get("url", ""),
            "image_url": a.get("image_url", ""),
            "summary": a["summary"],
            "trend": a.get("trend", ""),
            "date": a.get("date", ""),
        }
        reason = a.get("reasoning", {})
        if reason.get("analyst"):
            entry["reasoning"] = reason
        articles_out.append(entry)

    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        site_desc=SITE_DESC,
        updated=updated,
        articles=articles_out,
        articles_json=json.dumps(articles_out, ensure_ascii=False),
        mashups_json=json.dumps(mashups or [], ensure_ascii=False),
        briefing=briefing,
    )

    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {out_dir}\\index.html — {len(articles_out)} articles, {len(mashups or [])} mashups")
    if briefing:
        print(f"  HAL's briefing: {len(briefing)} sections")

    # Also write root copy for GitHub Pages
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
