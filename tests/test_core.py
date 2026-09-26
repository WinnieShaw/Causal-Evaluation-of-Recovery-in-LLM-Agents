import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_recovery.core import classify_outcome, paired_effect  # noqa: E402
from causal_recovery.cir import CIRConfig, should_refresh  # noqa: E402


class CoreTest(unittest.TestCase):
    def test_outcome_categories(self):
        self.assertEqual(classify_outcome(0, 1), "rescue")
        self.assertEqual(classify_outcome(1, 0), "harm")
        self.assertEqual(paired_effect(0, 1), 1)

    def test_minimum_delay_gate(self):
        config = CIRConfig(error_threshold=0.5, failure_threshold=0.1)
        self.assertFalse(should_refresh(1.0, 0.1, 0.9, 0, config))
        self.assertTrue(should_refresh(1.0, 0.1, 0.9, 1, config))


if __name__ == "__main__":
    unittest.main()
