import sys
from pathlib import Path
from graph import graph
from llm_router import CONFIG

def main(round_num: int):
    review_file = Path(f"pending_review/round_{round_num}_claude.md")
    if not review_file.exists():
        print(f"Error: Review file {review_file} not found.")
        return

    human_feedback = review_file.read_text(encoding="utf-8")
    project_id = CONFIG["project"]["id"]
    config = {"configurable": {"thread_id": project_id}}

    print(f"Resuming with human review for Round {round_num}...")
    graph.invoke({"human_feedback": human_feedback, "paused": False}, config)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
