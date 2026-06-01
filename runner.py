"""
runner.py — run your dispatcher against the 30 scenarios and see how it did.

    python3 runner.py

It imports `dispatch` from dispatcher.py, feeds it every scenario, and
compares the result to the expected outcome. When every scenario matches
you will see ALL MATCH. Until then it tells you, per scenario, what it
expected and what your dispatcher returned.

(Instructor: `python3 runner.py dispatcher_solution` runs the reference.)
"""
import importlib
import json
import os
import sys

SCENARIOS = os.path.join(os.path.dirname(__file__), "scenarios.json")


def main():
    module_name = sys.argv[1] if len(sys.argv) > 1 else "dispatcher"
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:  # noqa: BLE001
        print(f"Could not import '{module_name}': {e}")
        sys.exit(2)

    with open(SCENARIOS) as f:
        scenarios = json.load(f)

    log = []
    passed = 0
    fails = []

    for sc in scenarios:
        exp = sc["expected"]
        try:
            res = mod.dispatch(sc, log)
        except NotImplementedError as e:
            print(f"  {sc['id']:<28} → not implemented yet ({e}). "
                  f"Finish the TODOs in {module_name}.py, then re-run.")
            fails.append(sc["id"])
            continue
        except Exception as e:  # noqa: BLE001
            print(f"  {sc['id']:<28} → your dispatcher raised {type(e).__name__}: {e}")
            fails.append(sc["id"])
            continue

        ok = (bool(res.get("accept")) == exp["accept"]
              and (res.get("reason") or None) == (exp.get("reason") or None))
        if ok:
            passed += 1
        else:
            fails.append(sc["id"])
            exp_str = "ACCEPT" if exp["accept"] else f"REJECT ({exp['reason']})"
            got_str = ("ACCEPT" if res.get("accept")
                       else f"REJECT ({res.get('reason')})")
            note = f"   — {sc['note']}" if sc.get("note") else ""
            print(f"  ✗ {sc['id']:<28} expected {exp_str:<26} got {got_str}{note}")

    total = len(scenarios)
    print("\n" + "-" * 64)
    if passed == total:
        print(f"  ✅ ALL MATCH — {passed}/{total} scenarios handled correctly.")
        print(f"     The dispatcher logged {len(log)} decisions "
              f"(one per scenario). A few of them:")
        for line in log[:4]:
            print(f"       {line}")
    else:
        print(f"  {passed}/{total} correct — {len(fails)} to go: "
              f"{', '.join(fails[:8])}{' …' if len(fails) > 8 else ''}")
        if len(log) not in (total, 0):
            print(f"     (heads up: {len(log)} log entries for {total} scenarios — "
                  f"is every path logging exactly once?)")
    print("-" * 64)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
