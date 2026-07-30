# mocklog-cli

A small, dependency-free command-line tool that generates realistic-looking
**synthetic** log lines for testing log parsers, ingestion pipelines, and
dashboards. Every field is randomly generated — service names, messages,
hosts, IDs — and none of it describes a real system or event.

## Why

Testing a log parser or dashboard shouldn't require access to production
logs (or waiting for real traffic to generate interesting cases).
`mocklog-cli` prints a configurable stream of plausible-looking log lines
on demand, in either classic text or JSON-lines format.

## Install

```bash
pip install .
```

This installs a `mocklog-cli` command on your PATH.

## Usage

```bash
mocklog-cli --count 5
```

Example output:

```
2026-07-30T12:34:56Z [INFO] auth-service: user 48213 logged in
2026-07-30T12:34:57Z [INFO] cache-manager: cache warmed for key key:7741
2026-07-30T12:34:58Z [WARN] search-index: queue depth is high: 3902 items
2026-07-30T12:35:00Z [ERROR] billing-worker: database query timed out after 1874ms
2026-07-30T12:35:02Z [INFO] order-processor: processed 2210 records
```

JSON-lines output:

```bash
mocklog-cli --count 2 --format json
```

```
{"timestamp": "2026-07-30T12:34:56Z", "level": "INFO", "service": "user-api", "message": "health check passed"}
{"timestamp": "2026-07-30T12:34:57Z", "level": "DEBUG", "service": "session-store", "message": "cache miss for key key:203"}
```

Control the level mix:

```bash
mocklog-cli --count 10 --levels "ERROR=50,WARN=50"
```

### Options

| Flag         | Description                                                                 |
|--------------|-------------------------------------------------------------------------------|
| `--count N`  | Number of log lines to generate (default: 100)                                |
| `--format`   | Output format: `combined` or `json` (default: `combined`)                     |
| `--levels`   | Comma-separated `LEVEL` or `LEVEL=WEIGHT` pairs, e.g. `INFO=70,WARN=20,ERROR=10` (default: a realistic mostly-INFO mix) |
| `--seed N`   | Random seed for reproducible output                                           |

### Exit codes

- `0` — log lines generated successfully
- `2` — invalid arguments (bad count, unknown level, etc.)

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
