import random
import unittest
from datetime import datetime, timezone

from mocklog_cli.core import (
    LEVELS,
    MocklogError,
    format_combined,
    format_json,
    generate_entries,
    parse_levels,
    weighted_level,
)


class TestParseLevels(unittest.TestCase):
    def test_parses_weighted_pairs(self) -> None:
        weights = parse_levels("INFO=70,ERROR=30")
        self.assertEqual(weights, {"INFO": 70, "ERROR": 30})

    def test_bare_level_gets_weight_one(self) -> None:
        weights = parse_levels("WARN,ERROR")
        self.assertEqual(weights, {"WARN": 1, "ERROR": 1})

    def test_unknown_level_raises(self) -> None:
        with self.assertRaises(MocklogError):
            parse_levels("TRACE=5")

    def test_zero_weight_raises(self) -> None:
        with self.assertRaises(MocklogError):
            parse_levels("INFO=0")

    def test_empty_spec_raises(self) -> None:
        with self.assertRaises(MocklogError):
            parse_levels("")


class TestGenerateEntries(unittest.TestCase):
    def test_generates_requested_count(self) -> None:
        entries = generate_entries(10, random.Random(1))
        self.assertEqual(len(entries), 10)

    def test_zero_count_raises(self) -> None:
        with self.assertRaises(MocklogError):
            generate_entries(0, random.Random(1))

    def test_levels_restricted_to_given_weights(self) -> None:
        entries = generate_entries(50, random.Random(2), weights={"ERROR": 1})
        self.assertTrue(all(e.level == "ERROR" for e in entries))

    def test_reproducible_with_same_seed(self) -> None:
        entries_a = generate_entries(20, random.Random(42))
        entries_b = generate_entries(20, random.Random(42))
        self.assertEqual([e.message for e in entries_a], [e.message for e in entries_b])

    def test_timestamps_are_non_decreasing(self) -> None:
        entries = generate_entries(20, random.Random(3))
        timestamps = [e.timestamp for e in entries]
        self.assertEqual(timestamps, sorted(timestamps))


class TestWeightedLevel(unittest.TestCase):
    def test_only_returns_known_levels(self) -> None:
        rng = random.Random(7)
        for _ in range(50):
            level = weighted_level(rng, {"INFO": 70, "DEBUG": 15, "WARN": 10, "ERROR": 5})
            self.assertIn(level, LEVELS)


class TestFormatters(unittest.TestCase):
    def test_combined_format_layout(self) -> None:
        entry = generate_entries(1, random.Random(5))[0]
        line = format_combined(entry)
        self.assertIn(f"[{entry.level}]", line)
        self.assertIn(entry.service, line)
        self.assertIn(entry.message, line)

    def test_json_format_is_parseable(self) -> None:
        import json

        entry = generate_entries(1, random.Random(6))[0]
        data = json.loads(format_json(entry))
        self.assertEqual(data["level"], entry.level)
        self.assertEqual(data["service"], entry.service)
        self.assertEqual(data["message"], entry.message)


if __name__ == "__main__":
    unittest.main()
