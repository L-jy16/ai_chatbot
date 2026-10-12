"""Read-only SQLite inspection with required user scope and bound parameters."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys


def positive_id(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("user ID must be positive")
    return number


def bounded_limit(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError("limit must be 1..100")
    return number


def read_logs(db_path: Path, *, user_id: int, limit: int) -> list[dict]:
    sql = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")
    with sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(sql, {"user_id": user_id, "limit": limit})]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--user-id", type=positive_id, required=True)
    parser.add_argument("--limit", type=bounded_limit, default=20)
    args = parser.parse_args()
    try:
        rows = read_logs(args.db, user_id=args.user_id, limit=args.limit)
    except sqlite3.Error as error:
        print(f"Cannot inspect database: {error}", file=sys.stderr)
        return 1
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
