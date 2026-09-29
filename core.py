"""警局核心逻辑：案件、警力、拘留和证据。"""

import json


def new_game():
    return {
        "cases": {},
        "police": 3,
        "detention": {},
        "day": 1,
        "case_id": 0,
        "dispatches": {},
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    if not isinstance(text, str) or not text.strip():
        return new_game()
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return new_game()
    if not isinstance(data, dict):
        return new_game()
    base = new_game()
    for key, default in base.items():
        value = data.get(key, default)
        if key in ("police", "day", "case_id"):
            value = value if isinstance(value, int) and value >= 0 else default
        elif not isinstance(value, dict):
            value = default
        base[key] = value
    return base


def file_case(state, case_id):
    if state is None or not isinstance(case_id, int):
        return False
    cases = state.setdefault("cases", {})
    if case_id in cases:
        return False
    cases[case_id] = {"evidence": [], "at_large": False}
    if case_id > state.get("case_id", 0):
        state["case_id"] = case_id
    return True


def dispatch(state, case_id):
    if state is None or not isinstance(case_id, int):
        return False
    dispatches = state.setdefault("dispatches", {})
    if dispatches.get(case_id):
        return False
    if state.get("police", 0) <= 0:
        return False
    state["police"] -= 1
    dispatches[case_id] = True
    return True


def detention_days(state, case_id, end_day):
    if state is None or not isinstance(case_id, int):
        return 0
    if not isinstance(end_day, int):
        return 0
    start_day = state.get("day", 1)
    if end_day < start_day:
        days = 0
    else:
        days = end_day - start_day
    detention = state.setdefault("detention", {})
    if case_id not in detention or detention[case_id] < days:
        detention[case_id] = days
    return days


def cancel_dispatch(state, case_id):
    if state is None or not isinstance(case_id, int):
        return False
    dispatches = state.setdefault("dispatches", {})
    if not dispatches.get(case_id):
        return False
    del dispatches[case_id]
    state["police"] = state.get("police", 0) + 1
    return True


def add_evidence(state, case_id, evidence):
    if state is None or not isinstance(case_id, int):
        return False
    case = state.get("cases", {}).get(case_id)
    if case is None:
        return False
    if case.get("polluted"):
        return False
    if not isinstance(evidence, str) or not evidence.strip():
        return False
    if evidence in case.get("evidence", []):
        return False
    case["evidence"].append(evidence)
    return True


def arrest(state, case_id):
    if state is None or not isinstance(case_id, int):
        return False
    case = state.get("cases", {}).get(case_id)
    if case is None:
        return False
    if case.get("resisted"):
        return False
    case["arrested"] = True
    case["at_large"] = False
    return True


def clear_alarm(state, case_id):
    if state is None or not isinstance(case_id, int):
        return False
    case = state.get("cases", {}).get(case_id)
    if case is None:
        return False
    case["at_large"] = False
    return True


def demo():
    """固定日期、固定输入的演示流程，覆盖成功与失败分支。"""
    state = new_game()
    lines = []

    def record(label, ok):
        lines.append("%s: %s" % (label, "ok" if ok else "fail"))

    record("立案1", file_case(state, 1))
    record("重复立案1", file_case(state, 1))
    record("出警1", dispatch(state, 1))
    record("重复出警1", dispatch(state, 1))
    record("证据E1", add_evidence(state, 1, "E1"))
    record("重复证据E1", add_evidence(state, 1, "E1"))
    record("拘留至第5天(共4天=%d)" % detention_days(state, 1, 5),
           detention_days(state, 1, 5) == 4)
    state["cases"][1]["resisted"] = True
    police_before = state["police"]
    failed_arrest = arrest(state, 1)
    record("拒捕失败且不扣物资",
           (not failed_arrest) and state["police"] == police_before)
    state["cases"][1]["resisted"] = False
    record("取消出警返还警力", cancel_dispatch(state, 1))
    record("再次取消出警", cancel_dispatch(state, 1))
    record("抓捕成功", arrest(state, 1))
    state["cases"][1]["at_large"] = True
    record("解除警报", clear_alarm(state, 1)
           and not state["cases"][1]["at_large"])
    state["cases"][1]["polluted"] = True
    record("污染证据不计有效", not add_evidence(state, 1, "E2"))
    state["police"] = 0
    record("警力不足不出警", not dispatch(state, 2))
    loaded = load_state(save_state(state))
    record("读档编号不重复", loaded["case_id"] == state["case_id"])
    text = "\n".join(lines)
    print(text)
    return text


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main():
    state = new_game()
    print("警局 - 命令: file/dispatch/detention/cancel/evidence/arrest/alarm/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        command = parts[0]
        args = parts[1:]
        if command == "demo":
            demo()
            continue
        if command == "day":
            if len(args) == 1 and _parse_int(args[0]) is not None:
                state["day"] = _parse_int(args[0])
                print("ok")
            else:
                print("error: day 需要一个整数")
            continue
        if command == "file":
            if args:
                case_id = _parse_int(args[0])
            else:
                case_id = state["case_id"] + 1
            print("ok" if file_case(state, case_id) else "fail")
            continue
        if command in ("dispatch", "cancel", "arrest", "alarm"):
            if len(args) != 1 or _parse_int(args[0]) is None:
                print("error: %s 需要案件编号" % command)
                continue
            case_id = _parse_int(args[0])
            if command == "dispatch":
                result = dispatch(state, case_id)
            elif command == "cancel":
                result = cancel_dispatch(state, case_id)
            elif command == "arrest":
                result = arrest(state, case_id)
            else:
                result = clear_alarm(state, case_id)
            print("ok" if result else "fail")
            continue
        if command == "detention":
            if len(args) != 2 or _parse_int(args[0]) is None \
                    or _parse_int(args[1]) is None:
                print("error: detention 需要 案件编号 结束日期")
                continue
            print(detention_days(state, _parse_int(args[0]),
                                 _parse_int(args[1])))
            continue
        if command == "evidence":
            if len(args) < 2 or _parse_int(args[0]) is None:
                print("error: evidence 需要 案件编号 证据内容")
                continue
            result = add_evidence(state, _parse_int(args[0]),
                                  " ".join(args[1:]))
            print("ok" if result else "fail")
            continue
        print("error: 未知命令 %s" % command)


if __name__ == "__main__":
    main()
