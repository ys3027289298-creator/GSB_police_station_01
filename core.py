"""警局核心逻辑：案件、警力、拘留和证据。"""

import json

MAX_POLICE = 3


def new_game():
    return {
        "cases": {},
        "police": MAX_POLICE,
        "detention": {},
        "dispatched": [],
        "day": 1,
        "case_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state.setdefault("cases", {})
    state.setdefault("detention", {})
    state.setdefault("dispatched", [])
    state.setdefault("police", MAX_POLICE)
    state.setdefault("day", 1)
    state.setdefault("case_id", 0)
    return state


def file_case(state, case_id):
    cases = state.setdefault("cases", {})
    if case_id in cases:
        return False
    cases[case_id] = {"evidence": [], "at_large": False}
    return True


def dispatch(state, case_id):
    if case_id not in state.get("cases", {}):
        return False
    dispatched = state.setdefault("dispatched", [])
    if case_id in dispatched:
        return False
    if state.get("police", 0) <= 0:
        return False
    state["police"] -= 1
    dispatched.append(case_id)
    return True


def detention_days(state, case_id, end_day):
    days = end_day - state.get("day", 1)
    return max(0, days)


def cancel_dispatch(state, case_id):
    dispatched = state.setdefault("dispatched", [])
    if case_id not in dispatched:
        return False
    dispatched.remove(case_id)
    state["police"] = min(MAX_POLICE, state.get("police", 0) + 1)
    return True


def add_evidence(state, case_id, evidence):
    case = state.get("cases", {}).get(case_id)
    if case is None:
        return False
    if case.get("polluted"):
        return False
    if evidence in case["evidence"]:
        return False
    case["evidence"].append(evidence)
    return True


def arrest(state, case_id):
    case = state.get("cases", {}).get(case_id)
    if case is None:
        return False
    if case.get("resisted"):
        return False
    case["at_large"] = False
    return True


def clear_alarm(state, case_id):
    case = state.get("cases", {}).get(case_id)
    if case is None:
        return False
    case["at_large"] = False
    return True


COMMANDS = {"file", "dispatch", "detention", "cancel", "evidence", "arrest", "alarm", "quit"}


def main():
    print("警局 - 命令: file/dispatch/detention/cancel/evidence/arrest/alarm/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        if raw not in COMMANDS:
            print("未知命令")
            continue
        print("ok")


if __name__ == "__main__":
    main()
