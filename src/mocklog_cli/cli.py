"""Command-line entry point for mocklog-cli."""
from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime, timezone

from .core import (
    DEFAULT_WEIGHTS,
    MocklogError,
    format_combined,
    format_json,
    generate_entries,
    parse_levels,
)

# Fixed reference instant used as the timestamp origin whenever a --seed is
# given, so seeded runs are byte-for-byte reproducible (timestamps included).
_SEEDED_START_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mocklog-cli",
        description=(
            "Generate realistic-looking synthetic log lines for testing log "
            "parsers and dashboards. All output is randomly generated fake "
            "data — it does not come from, or describe, any real system."
        ),
    )
    parser.add_argument("--count", type=int, default=100, help="Number of log lines to generate (default: 100)")
    parser.add_argument(
        "--format", choices=["combined", "json"], default="combined", help="Output format (default: combined)"
    )
    parser.add_argument(
        "--levels",
        default=None,
        help=(
            "Comma-separated LEVEL or LEVEL=WEIGHT pairs controlling the level mix, "
            "e.g. 'INFO=70,WARN=20,ERROR=10' (default: a realistic mostly-INFO mix)"
        ),
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.count < 1:
        print("mocklog-cli: error: --count must be at least 1", file=sys.stderr)
        return 2

    try:
        weights = parse_levels(args.levels) if args.levels else dict(DEFAULT_WEIGHTS)
    except MocklogError as exc:
        print(f"mocklog-cli: error: {exc}", file=sys.stderr)
        return 2

    if args.seed is not None:
        rng = random.Random(args.seed)
        start_time = _SEEDED_START_TIME
    else:
        rng = random.Random()
        start_time = None

    try:
        entries = generate_entries(args.count, rng, weights, start_time=start_time)
    except MocklogError as exc:
        print(f"mocklog-cli: error: {exc}", file=sys.stderr)
        return 2

    formatter = format_json if args.format == "json" else format_combined
    for entry in entries:
        print(formatter(entry))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
