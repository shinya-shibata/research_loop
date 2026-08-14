import sys
import re
from datetime import date
from pathlib import Path

LOG_PATH = Path("memory/research-log.md")
REVIEWS_DIR = Path("memory/claude-reviews")
SNAPSHOT_DIR = Path("pending_review")


def extract_field(text: str, *labels: str) -> str:
    for label in labels:
        m = re.search(rf"## {re.escape(label)}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        if m:
            return m.group(1).strip()
    return "(N/A)"


def main(round_num: int):
    snapshot = (SNAPSHOT_DIR / f"round_{round_num}.md").read_text(encoding="utf-8")
    claude_review = (SNAPSHOT_DIR / f"round_{round_num}_claude.md").read_text(encoding="utf-8")

    topic = extract_field(snapshot, "Research Topic")
    hypothesis = extract_field(snapshot, "Latest Hypothesis / Derivation")
    verify = extract_field(snapshot, "Verification Result")

    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    review_path = REVIEWS_DIR / f"round_{round_num}.md"
    review_path.write_text(f"""---
title: Round {round_num} Claude Review
date: {date.today().isoformat()}
round: {round_num}
topic: {topic[:60]}
---

## Proposed Hypothesis (Summary)
{hypothesis[:500]}

## Claude Response (Full Text)
{claude_review}
""", encoding="utf-8")

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"""
## Round {round_num} — {date.today().isoformat()}
- Topic: {topic}
- Verification Result: {verify[:200]}
- Claude Review Summary: See [[claude-reviews/round_{round_num}.md]]
- Next Direction (Opening of Claude's guidance): {claude_review.strip().splitlines()[0][:150]}
---
""")

    print(f"Writeback complete: updated {review_path} and {LOG_PATH}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
