import re
from src.config import SUMMARY_MAX_SENTENCES, SUMMARY_MAX_CHARS

def summarize(text):
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = []
    char_count = 0
    for s in sentences:
        if len(summary) >= SUMMARY_MAX_SENTENCES:
            break
        s = s.strip()
        if not s:
            continue
        if char_count + len(s) > SUMMARY_MAX_CHARS:
            s = s[:SUMMARY_MAX_CHARS - char_count]
            if s:
                summary.append(s)
            break
        summary.append(s)
        char_count += len(s)
    result = " ".join(summary)
    if result and not result.endswith("."):
        result += "."
    return result
