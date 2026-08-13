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
あなたは統計学・漸近理論の共同研究者です。
研究課題: {state['topic']}

これまでの経過:
批評A: {state.get('critique_a', '（初回）')}
批評B: {state.get('critique_b', '')}
第三の意見: {state.get('third_opinion', '')}
人間（Claude）のレビュー: {state.get('human_feedback', '')}

上記すべてを踏まえ、次の一手となる具体的な導出・命題を提示してください。
数式は必ずSymPyで再現可能な形（変数 lhs / rhs を定義するPythonコード）でも併記してください。
"""
    text = call_role("hypothesis", prompt)
    return {"hypothesis": text, "round_num": state["round_num"] + 1}


def _critique_prompt(state):
    return f"""
以下の導出を批判的にレビューしてください。特に:
- 検証結果と矛盾する主張がないか
- 暗黙の仮定
- 反例になりそうな極端なケース

導出:
{state['hypothesis']}

検証結果:
{state['verify_result']}

最後の行に「妥当」または「要修正」とだけ書いてください。
"""


def critique_node(state):
    prompt = _critique_prompt(state)
    critique_a = call_role("critique_a", prompt)
    critique_b = call_role("critique_b", prompt)
    disagreement = ("要修正" in critique_a[-30:]) != ("要修正" in critique_b[-30:])
    return {"critique_a": critique_a, "critique_b": critique_b, "critique_disagreement": disagreement}


def third_opinion_node(state):
    prompt = f"""
以下の導出について、他のレビュアーの意見は見せずに、独立した第三者として妥当性を評価してください。

導出:
{state['hypothesis']}

検証結果:
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
        f.write(f"""# レビュー依頼 (round {state['round_num']})

## 研究課題
{state['topic']}

## 最新の仮説・導出
{state['hypothesis']}

## 検証結果
{state['verify_result']}  (verify_ok={state['verify_ok']})

## 批評A
{state['critique_a']}

## 批評B
{state['critique_b']}

## 意見の食い違い: {state['critique_disagreement']}

## 第三の意見
{state['third_opinion']}
""")

    reason = (
        "検証で矛盾検出" if not state["verify_ok"]
        else "批評モデル間の意見の食い違い" if state["critique_disagreement"]
        else f"{state['round_num']}ラウンド到達"
    )
    
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url and webhook_url.startswith("http"):
        requests.post(
            webhook_url,
            json={"text": f"🔬 研究ループ一時停止（{reason}）\nスナップショット: {snapshot_path}\n"
                           f"claude.aiでレビュー後、pending_review/round_{state['round_num']}_claude.md に保存し、"
                           f"`python resume.py {state['round_num']}` を実行してください。"},
        )
    print(f"\n[一時停止] 原因: {reason}")
    print(f"スナップショットを作成しました: {snapshot_path}\n")
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

os.makedirs("checkpoints", exist_ok=True)
checkpointer = SqliteSaver.from_conn_string("checkpoints/research.db")
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
    print("研究ループを開始します...")
    graph.invoke(initial_state, config)
