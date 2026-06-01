"""
dispatcher.py  —  YOUR WORK FOR TODAY.

A model has already decided what to do; its proposal is handed to you as
raw text. Your dispatcher is the deterministic code that wraps the model
on BOTH sides and decides whether the proposal ever reaches the relay.

You complete six TODOs:
    TODO 1  anomalous()            — the INBOUND gate (veto a bad reading)
    TODO 2  check_schema()         — is the proposal a well-formed command?
    TODO 3  check_range_identity() — real room? duration in range?
    TODO 4  check_hysteresis()     — no chatter: re-command too soon?
    TODO 5  check_safety()         — hard rules that override a valid command
    TODO 6  _log_and_return()      — record every decision with its reason

The orchestration in dispatch() is already written for you — read it first,
because the *order* of the gates is itself a design decision. Then fill the
six functions. Run `python3 runner.py` until you see ALL MATCH.

Work with the AI agent, but YOU decide what each rule should do. Read every
line it writes. The agent is the typist; you are the engineer.
"""
import json
from datetime import datetime

import jsonschema

# ---- domain facts (given — the dispatcher is told these, it does not learn them)
KNOWN_ROOMS = {"A115", "A116", "B201", "B202", "C103"}
DURATION_MIN, DURATION_MAX = 1, 30          # minutes
COOLDOWN_S = 600                            # min seconds between commands on one room
MIN_OPEN_TEMP_C = 5.0                       # below this, opening is unsafe

# The two — and only two — shapes the model is allowed to emit (structure and
# types only; room identity and duration *range* are your TODO 3, not this).
PROPOSAL_SCHEMA = {
    "oneOf": [
        {
            "type": "object",
            "properties": {
                "action": {"const": "open_window"},
                "room": {"type": "string"},
                "duration_min": {"type": "integer"},
            },
            "required": ["action", "room", "duration_min"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {"action": {"const": "do_nothing"}},
            "required": ["action"],
            "additionalProperties": False,
        },
    ]
}


# ---- TODO 1: the INBOUND gate -------------------------------------------------
def anomalous(reading):
    """Inspect the RAW reading, before the model's proposal is trusted at all.
    Return a reason STRING if the reading must be vetoed, else None.

    A reading dict has: room, timestamp, temperature_c, humidity_pct, iaq,
    and recent_iaq (a list of the most recent IAQ values leading up to now).

    Veto when, in this order:
      - humidity is physically impossible (outside 0–100 %) → "impossible_humidity"
      - the sensor is flatlined (recent_iaq has ~no spread)  → "stuck_sensor"
      - the current iaq is a sudden spike off the recent trend
        (more than 3 standard deviations from the recent mean) → "spike"
    Use recent_iaq only when it has at least 6 samples.
    """
    raise NotImplementedError("TODO 1: implement the inbound anomaly veto")


# ---- TODO 2: schema -----------------------------------------------------------
def check_schema(proposal):
    """`proposal` is the raw model output (usually a string of text).
    Parse it and validate it against PROPOSAL_SCHEMA.

    Return (parsed_command_dict, None) on success, or (None, "schema") on any
    failure: not valid JSON, wrong shape, missing field, extra field, or a
    field of the wrong type. NEVER coerce — the string "30" is NOT the integer
    30; it is a schema failure.
    """
    raise NotImplementedError("TODO 2: parse and schema-validate the proposal")


# ---- TODO 3: range / identity -------------------------------------------------
def check_range_identity(cmd):
    """`cmd` is a schema-valid open_window command. Return a reason or None.
      - room not one of KNOWN_ROOMS                  → "unknown_room"
      - duration_min outside [DURATION_MIN, DURATION_MAX] → "duration_range"
    """
    raise NotImplementedError("TODO 3: check room identity and duration range")


# ---- TODO 4: hysteresis (no chatter) ------------------------------------------
def check_hysteresis(cmd, reading, last_command):
    """Reject re-commanding the SAME room inside the cooldown window.

    `last_command` is None, or {"room": ..., "ts": <ISO timestamp>}: the last
    accepted command on that room. If it exists, is for the same room, and the
    gap between reading["timestamp"] and last_command["ts"] is less than
    COOLDOWN_S seconds → return "hysteresis". Otherwise None.
    Tip: datetime.fromisoformat(...) parses these timestamps.
    """
    raise NotImplementedError("TODO 4: implement the re-command cooldown")


# ---- TODO 5: safety -----------------------------------------------------------
def check_safety(cmd, reading):
    """Hard rules that override an otherwise-valid command. Return reason or None.
      - the command's room is not the room this reading came from
        (reading["room"])                            → "safety_room_mismatch"
      - opening when the room is below MIN_OPEN_TEMP_C → "safety_too_cold"
    """
    raise NotImplementedError("TODO 5: implement the safety rules")


# ---- TODO 6: logging ----------------------------------------------------------
def _log_and_return(log, scenario, accept, reason, action):
    """Record EVERY decision, then return the structured result.

    Append one human-readable entry to `log` (a list) — include the scenario
    id and whether it was accepted or rejected-with-which-reason — and return:
        {"accept": accept, "reason": reason, "action": action}
    """
    raise NotImplementedError("TODO 6: log the decision and return the result")


# ---- orchestration: already written. Read it — the gate ORDER is the design. --
def dispatch(scenario, log):
    reading = scenario["reading"]
    proposal = scenario["proposal"]
    last_command = scenario.get("last_command")

    # 1. inbound gate — veto a bad reading before the model is trusted at all
    reason = anomalous(reading)
    if reason:
        return _log_and_return(log, scenario, False, reason, None)

    # 2. schema — is the proposal even a well-formed command?
    cmd, reason = check_schema(proposal)
    if reason:
        return _log_and_return(log, scenario, False, reason, None)

    # a well-formed do_nothing is always safe to honour
    if cmd["action"] == "do_nothing":
        return _log_and_return(log, scenario, True, None, cmd)

    # 3-5. outbound checks for an open_window command
    for reason in (
        check_range_identity(cmd),
        check_hysteresis(cmd, reading, last_command),
        check_safety(cmd, reading),
    ):
        if reason:
            return _log_and_return(log, scenario, False, reason, None)

    return _log_and_return(log, scenario, True, None, cmd)
