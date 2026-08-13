import sys
import re
from datetime import date
from pathlib import Path

LOG_PATH = Path("memory/research-log.md")
REVIEWS_DIR = Path("memory/claude-reviews")
SNAPSHOT_DIR = Path("pending_review")


def extract_field(text: str, label: str) -> str:
    m = re.search(rf"## {label}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else "(該当なし)"


def main(round_num: int):
    snapshot = (SNAPSHOT_DIR / f"round_{round_num}.md").read_text(encoding="utf-8")
    claude_review = (SNAPSHOT_DIR / f"round_{round_num}_claude.md").read_text(encoding="utf-8")

    topic = extract_field(snapshot, "研究課題")
    hypothesis = extract_field(snapshot, "最新の仮説・導出")
    verify = extract_field(snapshot, "検証結果")

    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    review_path = REVIEWS_DIR / f"round_{round_num}.md"
    review_path.write_text(f"""---
title: Round {round_num} Claudeレビュー
date: {date.today().isoformat()}
round: {round_num}
topic: {topic[:60]}
---

## 提示した仮説（要約）
{hypothesis[:500]}

## Claudeの回答（全文）
{claude_review}
""", encoding="utf-8")

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"""
## Round {round_num} — {date.today().isoformat()}
- 課題: {topic}
- 検証結果: {verify[:200]}
- Claudeレビュー要約: [[claude-reviews/round_{round_num}.md]] を参照
- 次の方向性（Claude指示の冒頭）: {claude_review.strip().splitlines()[0][:150]}
---
""")

    print(f"書き戻し完了: {review_path} と {LOG_PATH} に反映しました")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
