import os
import requests
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from llm_router import call_role, CONFIG
from nodes.verify import verify_node

load_dotenv()

class ResearchState(TypedDict):
    topic: str
    round_num: int
    hypothesis: str
    verify_result: Optional[str]
    verify_ok: bool
    critique_a: str
    critique_b: str
    critique_disagreement: bool
    third_opinion: str
    human_feedback: Optional[str]
    paused: bool


def hypothesis_node(state):
    prompt = f"""
You are a research collaborator in mathematical statistics and asymptotic theory.
Research topic: {state['topic']}

Progress so far:
Critique A: {state.get('critique_a', '(Initial round)')}
Critique B: {state.get('critique_b', '')}
Third opinion: {state.get('third_opinion', '')}
Human (Claude) review: {state.get('human_feedback', '')}

Based on all of the above, present the next concrete proposition and mathematical derivation.
You MUST also include runnable Python code defining variables `lhs` and `rhs` so that mathematical formulas can be verified with SymPy.
"""
    text = call_role("hypothesis", prompt)
    return {"hypothesis": text, "round_num": state["round_num"] + 1}


def _critique_prompt(state):
    return f"""
Critically review the following derivation, specifically checking for:
- Any claims that contradict the verification results
- Implicit assumptions
- Extreme edge cases that could serve as counterexamples

Derivation:
{state['hypothesis']}

Verification result:
{state['verify_result']}

On the final line, write only 'VALID' or 'NEEDS_REVISION'.
"""


def critique_node(state):
    prompt = _critique_prompt(state)
    critique_a = call_role("critique_a", prompt)
    critique_b = call_role("critique_b", prompt)

    def is_revision_needed(c: str) -> bool:
        tail = c[-50:].upper()
        return "NEEDS_REVISION" in tail or "REVISED" in tail

    disagreement = is_revision_needed(critique_a) != is_revision_needed(critique_b)
    return {"critique_a": critique_a, "critique_b": critique_b, "critique_disagreement": disagreement}


def third_opinion_node(state):
    prompt = f"""
Evaluate the validity of the following derivation as an independent third party, without seeing any other reviewers' opinions.

Derivation:
{state['hypothesis']}

Verification result:
{state['verify_result']}
"""
    text = call_role("third_opinion", prompt)
    return {"third_opinion": text}


def decision_router(state) -> str:
    rounds_limit = CONFIG["settings"]["rounds_before_pause"]
    if not state["verify_ok"]:
        return "pause"
    if state["critique_disagreement"]:
        return "pause"
    if state["round_num"] % rounds_limit == 0:
        return "pause"
    return "continue"


def pause_node(state):
    os.makedirs("pending_review", exist_ok=True)
    snapshot_path = f"pending_review/round_{state['round_num']}.md"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        f.write(f"""# Review Request (Round {state['round_num']})

## Research Topic
{state['topic']}

## Latest Hypothesis / Derivation
{state['hypothesis']}

## Verification Result
{state['verify_result']}  (verify_ok={state['verify_ok']})

## Critique A
{state['critique_a']}

## Critique B
{state['critique_b']}

## Disagreement: {state['critique_disagreement']}

## Third Opinion
{state['third_opinion']}
""")

    reason = (
        "Contradiction detected in verification" if not state["verify_ok"]
        else "Disagreement between critique models" if state["critique_disagreement"]
        else f"Reached {state['round_num']} rounds"
    )
    
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url and webhook_url.startswith("http"):
        requests.post(
            webhook_url,
            json={"text": f"🔬 Research loop paused ({reason})\nSnapshot: {snapshot_path}\n"
                           f"After reviewing on claude.ai, save to pending_review/round_{state['round_num']}_claude.md and "
                           f"run `python resume.py {state['round_num']}`."},
        )
    print(f"\n[Paused] Reason: {reason}")
    print(f"Snapshot created: {snapshot_path}\n")
    return {"paused": True}


builder = StateGraph(ResearchState)
builder.add_node("hypothesis", hypothesis_node)
builder.add_node("verify", verify_node)
builder.add_node("critique", critique_node)
builder.add_node("third_opinion", third_opinion_node)
builder.add_node("pause", pause_node)

builder.set_entry_point("hypothesis")
builder.add_edge("hypothesis", "verify")
builder.add_edge("verify", "critique")
builder.add_edge("critique", "third_opinion")
builder.add_conditional_edges("third_opinion", decision_router, {
    "pause": "pause",
    "continue": "hypothesis",
})
builder.add_edge("pause", END)

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

os.makedirs("checkpoints", exist_ok=True)
conn = sqlite3.connect("checkpoints/research.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    project_id = CONFIG["project"]["id"]
    config = {"configurable": {"thread_id": project_id}}
    initial_state = {
        "topic": CONFIG["project"]["topic"],
        "round_num": 0,
        "hypothesis": "",
        "verify_result": None,
        "verify_ok": True,
        "critique_a": "",
        "critique_b": "",
        "critique_disagreement": False,
        "third_opinion": "",
        "human_feedback": None,
        "paused": False,
    }
    print("Starting research loop...")
    graph.invoke(initial_state, config)
