import re
import sympy as sp

def verify_node(state):
    hypothesis_text = state.get("hypothesis", "")
    
    # プロンプト内からPythonコード（SymPy定義）を探すパターン
    code_blocks = re.findall(r"```python(.*?)```", hypothesis_text, re.DOTALL)
    
    if not code_blocks:
        return {
            "verify_result": "検証コードが提示されなかったため未検証（要修正扱い）",
            "verify_ok": False
        }
        
    code = code_blocks[0]
    local_vars = {"sp": sp}
    
    try:
        exec(code, {}, local_vars)

        # 完全一致の lhs/rhs があれば最優先
        pairs = []
        if local_vars.get("lhs") is not None and local_vars.get("rhs") is not None:
            pairs.append(("lhs", "rhs"))

        # lhs_xxx / rhs_xxx のような接頭辞ペアも拾う（round_1のlhs_var/rhs_varなど）
        lhs_keys = {k[4:]: k for k in local_vars if k.startswith("lhs_")}
        rhs_keys = {k[4:]: k for k in local_vars if k.startswith("rhs_")}
        for suffix in lhs_keys.keys() & rhs_keys.keys():
            pairs.append((lhs_keys[suffix], rhs_keys[suffix]))

        if not pairs:
            return {
                "verify_result": (
                    "lhs/rhs（または lhs_xxx/rhs_xxx ペア）がコード内で定義されていません。"
                    "hypothesis側のプロンプトで変数名を再度明示するか、命名規則を確認してください。"
                ),
                "verify_ok": False,
            }

        # すべてのペアを検証し、1つでも不一致なら要修正
        details = []
        all_equal = True
        for lname, rname in pairs:
            diff = sp.simplify(local_vars[lname] - local_vars[rname])
            is_equal = (diff == 0)
            all_equal = all_equal and is_equal
            details.append(f"{lname} - {rname} = {diff} (等価: {is_equal})")

        result_msg = "SymPy検証結果:\n" + "\n".join(details)
        return {"verify_result": result_msg, "verify_ok": all_equal}
    except Exception as e:
        return {"verify_result": f"SymPy実行エラー: {str(e)}", "verify_ok": False}
