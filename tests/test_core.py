import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_case(self):
        state = core.new_game()
        self.assertTrue(core.file_case(state, 1))
        self.assertFalse(core.file_case(state, 1))

    def test_02_no_dispatch_without_police(self):
        state = core.new_game()
        state["police"] = 0
        result = core.dispatch(state, 1)
        self.assertFalse(result)

    def test_03_detention_exact(self):
        state = core.new_game()
        self.assertEqual(core.detention_days(state, 1, 5), 4)

    def test_04_cancel_returns_police(self):
        state = core.new_game()
        core.dispatch(state, 1)
        core.cancel_dispatch(state, 1)
        self.assertEqual(state["police"], 3)

    def test_05_polluted_evidence_invalid(self):
        state = core.new_game()
        core.file_case(state, 1)
        state["cases"][1]["polluted"] = True
        result = core.add_evidence(state, 1, "E1")
        self.assertFalse(result)

    def test_06_arrest_failure_no_cost(self):
        state = core.new_game()
        core.file_case(state, 1)
        state["cases"][1]["resisted"] = True
        state["police"] = 2
        result = core.arrest(state, 1)
        self.assertFalse(result)
        self.assertEqual(state["police"], 2)

    def test_07_alarm_clears_at_large(self):
        state = core.new_game()
        core.file_case(state, 1)
        state["cases"][1]["at_large"] = True
        core.clear_alarm(state, 1)
        self.assertFalse(state["cases"][1]["at_large"])

    def test_08_load_preserves_case_id(self):
        state = core.new_game()
        state["case_id"] = 4
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["case_id"], 4)


if __name__ == "__main__":
    unittest.main()
