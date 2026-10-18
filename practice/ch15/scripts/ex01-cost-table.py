"""從 results/ex01/*.json 彙整實測成本表（Markdown）"""
import json
import sys
from pathlib import Path

RESULT_DIR = Path(__file__).resolve().parent.parent / "results" / "ex01"
TASKS = ["format", "analysis", "reasoning"]
MODELS = ["haiku", "sonnet", "opus"]


def load_run(task_name, model_name):
    run_file = RESULT_DIR / f"{task_name}-{model_name}.json"
    try:
        return json.loads(run_file.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as err:
        print(f"錯誤：讀取 {run_file} 失敗：{err}", file=sys.stderr)
        return None


def build_table():
    lines = ["| 任務 | model | 實際 model ID | total_cost_usd | duration_ms | 輸出 tokens | cache 建立 / 讀取 tokens | 相對 Haiku |",
             "|---|---|---|---:|---:|---:|---:|---:|"]
    for task_name in TASKS:
        base_cost = None
        for model_name in MODELS:
            run = load_run(task_name, model_name)
            if run is None:
                continue
            usage = run["usage"]
            cost = run["total_cost_usd"]
            if model_name == "haiku":
                base_cost = cost
            ratio = f"{cost / base_cost:.1f}x" if base_cost else "-"
            model_id = next(iter(run.get("modelUsage", {})), "?")
            lines.append(
                f"| {task_name} | {model_name} | {model_id} | {cost:.5f} | {run['duration_ms']} | "
                f"{usage['output_tokens']} | {usage['cache_creation_input_tokens']} / {usage['cache_read_input_tokens']} | {ratio} |")
    return "\n".join(lines)


if __name__ == "__main__":
    table = build_table()
    assert table.count("\n") >= 2, "成本表至少要有一列資料"
    (RESULT_DIR / "cost-table.md").write_text(table + "\n", encoding="utf-8")
    print(table)
