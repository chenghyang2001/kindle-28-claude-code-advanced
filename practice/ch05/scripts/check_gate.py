"""Gate 檢查器：python scripts/check_gate.py <0|1|2|3>，全部條件成立 exit 0，否則 exit 1。"""
import importlib
import inspect
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "contracts" / "spec.md"
SIGNAL_SECTIONS = ("## Deliverables", "## Next Steps", "## Open Questions")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_tests(pattern: str) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def spec_functions() -> list[str]:
    return re.findall(r"^### `(\w+)\(", read(SPEC), flags=re.M)


def load_pricing():
    sys.path.insert(0, str(ROOT / "src"))
    if "pricing" in sys.modules:
        return importlib.reload(sys.modules["pricing"])
    return importlib.import_module("pricing")


def gate0() -> list[tuple[str, bool]]:
    spec = read(SPEC)
    return [
        ("spec 四節齊全", all(s in spec for s in
                           ("## 公開介面", "## 行為規則", "## 邊界條件", "## Never modifies"))),
        ("spec Status: APPROVED", "Status: APPROVED" in spec),
        ("公開介面至少 1 個函式", len(spec_functions()) >= 1),
        ("特徵測試對舊模組全綠", run_tests("test_characterization.py")),
    ]


def annotations_complete(func) -> bool:
    sig = inspect.signature(func)
    params_ok = all(p.annotation is not inspect.Parameter.empty for p in sig.parameters.values())
    return params_ok and sig.return_annotation is not inspect.Signature.empty


def gate1() -> list[tuple[str, bool]]:
    pricing_path = ROOT / "src" / "pricing.py"
    try:
        py_compile.compile(str(pricing_path), doraise=True)
        pricing = load_pricing()
        compiled = True
    except (py_compile.PyCompileError, ImportError, FileNotFoundError) as exc:
        print(f"  編譯/匯入失敗：{exc}")
        compiled, pricing = False, None
    funcs = spec_functions()
    sig_ok = compiled and all(
        callable(getattr(pricing, f, None)) and annotations_complete(getattr(pricing, f))
        for f in funcs)
    return [
        ("pricing.py 可編譯可匯入", compiled),
        (f"spec 函式存在且有型別註記 {funcs}", sig_ok),
        ("contracts/CLAUDE.md 含 Never modifies", "Never modifies" in read(ROOT / "contracts" / "CLAUDE.md")),
        ("gate 0 仍成立", all(ok for _, ok in gate0())),
    ]


def signal_ok(name: str) -> bool:
    text = read(ROOT / "signals" / name)
    return bool(text) and all(s in text for s in SIGNAL_SECTIONS)


def snapshot_equal() -> bool:
    try:
        pricing = load_pricing()
        sys.path.insert(0, str(ROOT / "tests"))
        from cases import CASES
        expected = json.loads(read(ROOT / "tests" / "snapshot.json"))
        actual = [pricing.calculate(o, t) for o, t in CASES]
        if actual != expected:
            return False
        # 裁決 1：型別也要一致（120 == 120.0 會騙過 ==）。
        # 與 snapshot 比而非與 legacy 比：Phase 3 後 legacy 委派給 pricing，會變成自己比自己。
        return all({k: type(v) for k, v in a.items()} == {k: type(v) for k, v in b.items()}
                   for a, b in zip(actual, expected))
    except Exception as exc:  # 實作未完成時任何錯誤都算不過關
        print(f"  snapshot 比對失敗：{type(exc).__name__}: {exc}")
        return False


def gate2() -> list[tuple[str, bool]]:
    review = read(ROOT / "signals" / "REVIEW_COMPLETE.md")
    return [
        ("三個信號檔存在且三段完整",
         all(signal_ok(n) for n in ("DONE.md", "BUILD_COMPLETE.md", "REVIEW_COMPLETE.md"))),
        ("REVIEW_COMPLETE: MUST_FIX: 0", re.search(r"MUST_FIX:\s*0\b", review) is not None),
        ("test_pricing.py 全綠", (ROOT / "tests" / "test_pricing.py").exists() and run_tests("test_pricing.py")),
        ("pricing.calculate 與 snapshot 逐筆一致", snapshot_equal()),
        ("pricing.py 無 NotImplementedError", "NotImplementedError" not in read(ROOT / "src" / "pricing.py")),
    ]


def gate3() -> list[tuple[str, bool]]:
    legacy = read(ROOT / "src" / "legacy_order.py")
    magic = re.findall(r"\b(0\.1|0\.05|1000|1500|500|150|100|60|50)\b", legacy)
    return [
        ("legacy 委派給 pricing.calculate", "pricing.calculate" in legacy),
        (f"legacy 無計價魔術數字（找到 {magic}）", not magic),
        ("全部測試綠", run_tests("test*.py")),
        ("README 提到 pricing", "pricing" in read(ROOT / "README.md")),
        ("gate 0–2 仍成立", all(ok for g in (gate0, gate1, gate2) for _, ok in g())),
    ]


GATES = {0: gate0, 1: gate1, 2: gate2, 3: gate3}


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or int(sys.argv[1]) not in GATES:
        print("用法：python scripts/check_gate.py <0|1|2|3>", file=sys.stderr)
        sys.exit(2)
    phase = int(sys.argv[1])
    results = GATES[phase]()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    passed = all(ok for _, ok in results)
    print(f"GATE {phase}: {'PASS' if passed else 'FAIL'}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
