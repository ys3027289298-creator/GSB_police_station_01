"""警局核心逻辑：案件、警力、拘留和证据。"""

import json


def new_game():
    return {
        "cases": {},
        "police": 3,
        "detention": {},
        "day": 1,
        "case_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["case_id"] += 1
    return state


def file_case(state, case_id):
    state["cases"][case_id] = {"evidence": [], "at_large": False}
    return True


def dispatch(state, case_id):
    state["police"] -= 1
    return True


def detention_days(state, case_id, end_day):
    return (end_day - state["day"]) - 1


def cancel_dispatch(state, case_id):
    return True


def add_evidence(state, case_id, evidence):
    state["cases"][case_id]["evidence"].append(evidence)
    return True


def arrest(state, case_id):
    if state["cases"][case_id].get("resisted"):
        state["police"] -= 1
        return False
    return True


def clear_alarm(state, case_id):
    return True


def main():
    print("警局 - 命令: file/dispatch/detention/cancel/evidence/arrest/alarm/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
