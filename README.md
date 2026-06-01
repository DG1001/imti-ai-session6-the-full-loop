# Exercise: Build the Dispatcher

**AI in Technical Systems — Session 6 Hands-on**

You have ~30 minutes of hands-on work today. The goal is to build the one
piece of code that stands between a language model and a real relay: the
**dispatcher**. It is plain, deterministic Python — no model, no GPU — and
that is exactly the point. The model decides; the dispatcher decides
whether to *honour* that decision.

---

## How to start

If you cloned this repository: open it in XaresAICoder (or your local
VS Code), install the one dependency with
`pip install -r requirements.txt --break-system-packages`, then read the
rest of this README and open `dispatcher.py`.

If you are working with the AI agent inside XaresAICoder, the agent
already knows the rules of this exercise (see `AGENTS.md`). Talk to it —
but **you** decide what each rule does, and you read every line it writes.
The agent is the typist; you are the engineer.

There is **no LLM, no GPU, and no network** needed for today's work. The
model's proposals are *frozen* in `scenarios.json` — pre-recorded text —
so the exercise is deterministic and you can run it instantly in your
2 GB container.

---

## The story

Last session you watched a small local model turn sensor readings into
JSON commands for a single function, `open_window(room, duration_min)`.
On a clear prompt it was right almost every time — but "almost" is the
whole problem. You cannot prove a probabilistic model will be right on
every input it will ever meet, and a relay is not a place for "almost".

So today you build the deterministic wrapper that makes the model safe to
wire up. It sits on **both** sides of the model, drawn as a U:

- an **inbound gate** that checks the raw sensor reading *before* the
  model is even consulted, and
- an **outbound gate** that checks the model's proposed command *before*
  it reaches the relay.

The model never gets more reliable today. What changes is that there is
now a small block of code, around it on both sides, that you can read,
test, and reason about completely.

---

## The setup

In this repository you will find:

- `dispatcher.py` — **your work**. Six TODOs to complete. The
  orchestration (`dispatch()`) is already written — read it first,
  because the *order* of the gates is itself a design decision.
- `scenarios.json` — 30 frozen scenarios. Each one is a sensor reading
  plus the model's (pre-recorded) proposed command, plus the outcome a
  correct dispatcher should reach.
- `runner.py` — runs your dispatcher against all 30 and tells you, one by
  one, where you do not yet match. Run it as often as you like.
- `AGENTS.md` — the rules for the AI agent.
- `requirements.txt` — one dependency, `jsonschema`.

---

## The exercise — six rules, two gates (~30 min)

Open `dispatcher.py` and complete the six TODOs. Each one has a docstring
that tells you exactly what it must do and which reason string to return.

| # | Function | Gate | Job |
|---|----------|------|-----|
| 1 | `anomalous()` | inbound | Veto a reading you cannot trust |
| 2 | `check_schema()` | outbound | Is the proposal a well-formed command? |
| 3 | `check_range_identity()` | outbound | Real room? Duration in [1, 30]? |
| 4 | `check_hysteresis()` | outbound | No chatter — re-command too soon? |
| 5 | `check_safety()` | outbound | Hard rules that override a valid command |
| 6 | `_log_and_return()` | both | Record every decision with its reason |

Then run:

```bash
python3 runner.py
```

Keep going until it prints **ALL MATCH** — 30 of 30. Until then it shows
you each scenario you miss, what it expected, and what your dispatcher
returned.

### How to work with the agent

Ask for one TODO at a time. Decide the rule yourself, then have the agent
write it. For example:

> For TODO 2, parse the proposal with `json.loads` inside a try/except,
> then validate the parsed object against `PROPOSAL_SCHEMA` with
> `jsonschema.validate`. Return `(parsed, None)` on success and
> `(None, "schema")` on any failure. Do not coerce types.

Read what it writes before you run it.

---

## The scenarios that will trip you up

Some of the 30 are deliberately built to fool a careless dispatcher.
Three to watch for, because each teaches a reflex:

- **A re-command 3 seconds after the last one** on the same room. Valid
  on its own — so a naïve dispatcher takes both, and the fan chatters. A
  correct one rejects the second on **hysteresis**.
- **A `duration_min` of the string `"30"`** instead of the integer `30`.
  The tempting "fix" is to coerce it. Don't — reject it on **schema**. If
  you coerce, you have quietly accepted malformed input.
- **A perfectly valid proposal built on a broken reading** — a flatlined
  sensor, a humidity of 110 %, a spike. A dispatcher that only checks the
  *proposal* waves these through. A correct one vetoes them at the
  **inbound** gate, before the proposal even matters. *A flawless
  proposal on a bad reading is still wrong.*

---

## The honest reading

When the runner prints ALL MATCH, look at the log your dispatcher built.
Of the 30 cycles, more than half were stopped — some before the model's
proposal was even examined. None of that made the *model* any better. It
made the *system* safe, by wrapping a component you cannot fully certify
in code you can.

That is the engineering of the full loop. The AI was the easy part.

---

## When you're done

Write down — for yourself — answers to:

1. Which rule was hardest to state precisely as code, and why?
2. Where did you have to make a judgement call (how cold is "too cold",
   how long is the cooldown)? A stakeholder might have chosen differently
   — could you defend yours from the log?
3. How many of the 30 cycles never reached the model because the inbound
   gate vetoed the reading? That number is free safety.
4. If this dispatcher ran a real 230 V relay, which single rule would you
   be most nervous about getting wrong?

We will discuss in the wrap-up.

---

## If you finish early

Pick one — these are what you would do on a real project:

- **Add a rule.** Reject an `open_window` when humidity is already very
  high (opening would not help). Decide the threshold, add the check to
  `check_safety()`, and invent a scenario for it.
- **Make the log useful.** Have `_log_and_return()` also record the
  reading's room and IAQ, then print a one-line summary at the end: how
  many accepted, and a count of rejections by reason. That breakdown is
  exactly what you would monitor in production.
- **Tighten the spike detector.** The inbound gate flags a spike at 3
  standard deviations. Try 2.5. Does any clean scenario start failing?
  What does that tell you about how to choose the threshold?
- **Argue with a rule.** Find a scenario whose rejection you think is too
  strict, or too lax. Change the rule, see what else moves, and decide
  whether you have made the system better or just made this one test
  happier.
