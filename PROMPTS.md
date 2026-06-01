# Prompts — Dispatcher Hands-on (Session 6)

One worked prompt per TODO for `dispatcher.py`. Copy-paste-ready, written
to match each function's docstring and the exact reason strings the runner
checks. Phrased as the student instructing the AI agent.

> **A note on how to use these.** The student README ships only the TODO 2
> example on purpose — students see the *pattern* and write the other five
> themselves from the docstrings, which keeps the "you decide the rule, the
> agent types it" idea intact. Treat this file as a reference / answer-key
> for stuck students rather than a copy-paste sheet, or hand it out only
> after they've attempted their own.

---

## Optional kickoff

Sets the "one at a time" pair-programming mode before any code is written.

```
Read dispatcher.py with me from top to bottom — especially the dispatch() function and the constants at the top. Don't write any code yet; just confirm you understand the order the gates run in. Then we'll do the six TODOs one at a time.
```

---

## TODO 1 — the inbound gate

```
Implement TODO 1, anomalous(reading). Check the raw reading in this order and return the reason string on the first problem you find, otherwise None:
- if humidity_pct is missing or outside 0–100, return "impossible_humidity"
- then, only if recent_iaq has at least 6 values: if its spread (max minus min) is below 0.5, return "stuck_sensor"
- otherwise, using the mean and standard deviation of recent_iaq, if the current iaq is more than 3 standard deviations from the mean, return "spike"
Return None if none apply. Don't add any other checks.
```

## TODO 2 — schema

*(This is the example already in the README.)*

```
For TODO 2, check_schema(proposal): parse the proposal with json.loads inside a try/except, then validate the parsed object against PROPOSAL_SCHEMA with jsonschema.validate. Return (parsed, None) on success and (None, "schema") on any failure. Do not coerce types — the string "30" must fail, not be cast to an integer.
```

## TODO 3 — range / identity

```
Implement TODO 3, check_range_identity(cmd), where cmd is a schema-valid open_window command. If cmd["room"] is not in KNOWN_ROOMS, return "unknown_room". If cmd["duration_min"] is outside DURATION_MIN..DURATION_MAX inclusive, return "duration_range". Otherwise return None.
```

## TODO 4 — hysteresis

```
Implement TODO 4, check_hysteresis(cmd, reading, last_command). last_command is either None or a dict like {"room": ..., "ts": <ISO timestamp>}. If it's None or for a different room than cmd["room"], return None. Otherwise use datetime.fromisoformat to get the seconds between reading["timestamp"] and last_command["ts"], and if that gap is at least 0 and less than COOLDOWN_S, return "hysteresis". Otherwise return None.
```

## TODO 5 — safety

```
Implement TODO 5, check_safety(cmd, reading). If cmd["room"] is not the same as reading["room"], return "safety_room_mismatch". Otherwise, if reading["temperature_c"] is below MIN_OPEN_TEMP_C, return "safety_too_cold". Otherwise return None.
```

## TODO 6 — logging

```
Implement TODO 6, _log_and_return(log, scenario, accept, reason, action). Append one readable line to log containing scenario["id"] and the verdict — "ACCEPT" if accepted, or "REJECT (<reason>)" if not — then return the dict {"accept": accept, "reason": reason, "action": action}.
```

---

When all six are in place, run `python3 runner.py` until it prints
**ALL MATCH** — 30 of 30 (13 accepted · 3 anomaly · 6 schema · 4 range ·
2 hysteresis · 2 safety).
