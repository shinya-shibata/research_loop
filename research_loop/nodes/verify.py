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
        lhs = local_vars.get("lhs")
        rhs = local_vars.get("rhs")
        
        if lhs is not None and rhs is not None:
            diff = sp.simplify(lhs - rhs)
            is_equal = (diff == 0)
            result_msg = f"SymPy検証成功: lhs - rhs = {diff} (等価: {is_equal})"
            return {"verify_result": result_msg, "verify_ok": is_equal}
        else:
            return {"verify_result": "lhs または rhs がコード内で定義されていません", "verify_ok": False}
    except Exception as e:
        return {"verify_result": f"SymPy実行エラー: {str(e)}", "verify_ok": False}
