import os
import json
import re
import math
from datetime import datetime, timezone
from collections import Counter
from jinja2 import Environment, FileSystemLoader

from src.config import SITE_NAME, SITE_URL, SITE_DESC
from src.similarity import find_related, similarity_matrix
from src.topics import cluster_articles

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSITIVE = set("""
breakthrough impressive innovative remarkable milestone success growth surge
record soar jump boost rally gain strong momentum optimistic promising
pioneering breakthrough award win victory achieve launch partnership funding
investment expand growth opportunity potential leader leading top best
excellent outstanding incredible revolutionary transformative exciting bright
""".split())

NEGATIVE = set("""
loss fail decline drop fall slump crisis risk threat danger breach
violate exploit abuse leak hack attack lawsuit sue court battle dispute
struggle problem issue concern worry cut layoff fire resign quit crisis
collapse bankrupt debt deficit loss damage harm hurt pain suffer tragic
deadly fatal worst terrible poor weak broken flawed争议 controversy
""".split())

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

def compute_mood(text):
    if not text:
        return "neutral"
    words = re.findall(r"[a-z]+", text.lower())
    if not words:
        return "neutral"
    pos = sum(1 for w in words if w in POSITIVE)
    neg = sum(1 for w in words if w in NEGATIVE)
    score = (pos - neg) / max(len(words) * 0.01, 1)
    if score > 0.5:
        return "positive"
    if score < -0.5:
        return "negative"
    return "neutral"

def compute_reading_time(text):
    if not text:
        return 1
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 200))

def generate(articles, briefing_raw=None, mashups=None):
    grouped = {}
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

    # Topic clustering using sklearn
    cluster_articles(flat)
    cluster_groups = {}
    for a in flat:
        tid = a.get("topic_id", 0)
        cluster_groups.setdefault(tid, []).append(a)

    articles_out = []
    keywords_bag = Counter()
    for i, a in enumerate(flat):
        summary = a["summary"]
        mood = compute_mood(summary)
        entry = {
            "id": i,
            "title": a["title"],
            "source": a.get("source", ""),
            "url": a.get("url", ""),
            "image_url": a.get("image_url", ""),
            "summary": summary,
            "trend": a.get("trend", ""),
            "date": a.get("date", ""),
            "mood": mood,
            "reading_time": compute_reading_time(summary),
            "keywords": a.get("keywords", [])[:5],
            "topic_label": a.get("topic_label", "General"),
            "topic_id": a.get("topic_id", 0),
        }
        reason = a.get("reasoning", {})
        if reason.get("analyst"):
            entry["reasoning"] = reason
        articles_out.append(entry)
        for kw in entry["keywords"]:
            if isinstance(kw, str):
                keywords_bag[kw.lower()] += 1

    # Keyword cloud: top 30 keywords
    top_kw = [{"word": w, "count": c} for w, c in keywords_bag.most_common(30)]

    # TF-IDF related articles
    for entry in articles_out:
        related = find_related(articles_out, entry["id"], top_n=3)
        if related:
            entry["related"] = related

    # Topic groups for navigation
    topic_groups = []
    seen_topics = set()
    for a in articles_out:
        tl = a.get("topic_label", "General")
        if tl not in seen_topics:
            seen_topics.add(tl)
            topic_groups.append({"label": tl, "count": sum(1 for x in articles_out if x.get("topic_label") == tl)})

    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        site_desc=SITE_DESC,
        updated=updated,
        articles=articles_out,
        articles_json=json.dumps(articles_out, ensure_ascii=False),
        topic_groups=topic_groups,
        mashups_json=json.dumps(mashups or [], ensure_ascii=False),
        top_keywords=json.dumps(top_kw, ensure_ascii=False),
        briefing=briefing,
    )

    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    moods = Counter(a["mood"] for a in articles_out)
    print(f"Generated {out_dir}\\index.html — {len(articles_out)} articles, {len(mashups or [])} mashups")
    print(f"  Mood: {dict(moods)} | Keywords: {len(top_kw)} unique")

    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
