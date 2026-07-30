"""Core synthetic log-generation logic for mocklog-cli.

Every value produced here is randomly generated for testing purposes —
none of it reflects any real system, user, or event. All randomness is
driven through a `random.Random` instance passed in by the caller, so
output is fully reproducible when a seed is supplied and easy to test
without touching global state.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]

DEFAULT_WEIGHTS: dict[str, int] = {"INFO": 70, "DEBUG": 15, "WARN": 10, "ERROR": 5}

SERVICES = [
    "auth-service",
    "payment-gateway",
    "user-api",
    "billing-worker",
    "notification-service",
    "search-index",
    "cache-manager",
    "order-processor",
    "email-sender",
    "session-store",
]

HOSTS = [
    "db-01.internal",
    "cache-03.internal",
    "api.internal",
    "auth.internal",
    "queue-02.internal",
    "storage-05.internal",
]

FUNCS = [
    "process_payment",
    "load_user_profile",
    "send_notification",
    "sync_inventory",
    "refresh_token",
    "compute_totals",
]

JOBS = ["nightly-backup", "invoice-export", "cache-warm", "index-rebuild", "usage-rollup"]

FLAGS = ["new-checkout", "dark-mode", "beta-search", "fast-shipping", "trial-extension"]

MESSAGE_TEMPLATES: dict[str, list[str]] = {
    "INFO": [
        "request completed in {ms}ms",
        "user {user_id} logged in",
        "cache warmed for key {cache_key}",
        "scheduled job '{job}' finished successfully",
        "health check passed",
        "connection established to {host}",
        "processed {count} records",
        "configuration reloaded",
    ],
    "DEBUG": [
        "entering function {func}",
        "cache miss for key {cache_key}",
        "retrying request to {host}, attempt {attempt}",
        "payload size: {count} bytes",
        "evaluating feature flag '{flag}'",
    ],
    "WARN": [
        "response time exceeded threshold: {ms}ms",
        "deprecated endpoint called: {func}",
        "retrying after transient error from {host}",
        "queue depth is high: {count} items",
        "rate limit approaching for client {ip}",
    ],
    "ERROR": [
        "failed to connect to {host}: connection refused",
        "unhandled exception in {func}",
        "database query timed out after {ms}ms",
        "authentication failed for user {user_id}",
        "out of memory while processing {count} records",
    ],
}


class MocklogError(ValueError):
    """Raised when log-generation parameters are invalid."""


@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    service: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": self.level,
            "service": self.service,
            "message": self.message,
        }


def parse_levels(spec: str) -> dict[str, int]:
    """Parse a `--levels` spec like 'INFO=70,WARN=20,ERROR=10' or 'WARN,ERROR'.

    A bare level name (no '=') gets an equal-share weight of 1.
    """
    weights: dict[str, int] = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            level, _, weight_str = part.partition("=")
            level = level.strip().upper()
            try:
                weight = int(weight_str.strip())
            except ValueError:
                raise MocklogError(f"invalid weight for level {level!r}: {weight_str!r}")
        else:
            level = part.upper()
            weight = 1
        if level not in LEVELS:
            raise MocklogError(f"unknown level: {level!r} (expected one of {', '.join(LEVELS)})")
        if weight <= 0:
            raise MocklogError(f"weight for level {level!r} must be positive")
        weights[level] = weight

    if not weights:
        raise MocklogError("no levels specified")
    return weights


def _random_ip(rng: random.Random) -> str:
    return ".".join(str(rng.randint(1, 254)) for _ in range(4))


def _message_values(rng: random.Random) -> dict[str, object]:
    return {
        "ms": rng.randint(5, 2500),
        "user_id": rng.randint(1000, 99999),
        "cache_key": f"key:{rng.randint(1, 9999)}",
        "job": rng.choice(JOBS),
        "host": rng.choice(HOSTS),
        "count": rng.randint(1, 5000),
        "func": rng.choice(FUNCS),
        "attempt": rng.randint(1, 5),
        "flag": rng.choice(FLAGS),
        "ip": _random_ip(rng),
    }


def generate_message(level: str, rng: random.Random) -> str:
    templates = MESSAGE_TEMPLATES[level]
    template = rng.choice(templates)
    return template.format(**_message_values(rng))


def weighted_level(rng: random.Random, weights: dict[str, int]) -> str:
    levels = list(weights.keys())
    counts = list(weights.values())
    return rng.choices(levels, weights=counts, k=1)[0]


def generate_entries(
    count: int,
    rng: random.Random,
    weights: dict[str, int] | None = None,
    start_time: datetime | None = None,
) -> list[LogEntry]:
    """Generate `count` synthetic LogEntry objects with increasing timestamps."""
    if count < 1:
        raise MocklogError("count must be at least 1")

    weights = weights or DEFAULT_WEIGHTS
    timestamp = start_time or datetime.now(timezone.utc)

    entries = []
    for _ in range(count):
        level = weighted_level(rng, weights)
        service = rng.choice(SERVICES)
        message = generate_message(level, rng)
        entries.append(LogEntry(timestamp=timestamp, level=level, service=service, message=message))
        timestamp = timestamp + timedelta(seconds=rng.uniform(0.01, 3.0))
    return entries


def format_combined(entry: LogEntry) -> str:
    data = entry.to_dict()
    return f"{data['timestamp']} [{data['level']}] {data['service']}: {data['message']}"


def format_json(entry: LogEntry) -> str:
    return json.dumps(entry.to_dict())
