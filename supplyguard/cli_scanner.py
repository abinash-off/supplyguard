"""Run SupplyGuard's local scanner from a terminal."""
import argparse
import json
from pathlib import Path
import sys

from backend.scanner_engine import scan_files

IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox", "dist", "build"}
MAX_FILES = 500
MAX_BYTES = 5_000_000


def collect_files(root: Path) -> list[dict]:
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory does not exist: {root}")
    files = []
    total = 0
    for path in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.relative_to(root).parts) or path.is_symlink() or not path.is_file():
            continue
        if len(files) >= MAX_FILES:
            raise ValueError(f"Project exceeds the {MAX_FILES} file scan limit.")
        size = path.stat().st_size
        total += size
        if total > MAX_BYTES:
            raise ValueError(f"Project exceeds the {MAX_BYTES // 1_000_000} MB scan limit.")
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append({"path": path.relative_to(root).as_posix(), "content": content})
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a project directory for common software supply-chain risks.")
    parser.add_argument("path", nargs="?", default=".", help="Project directory (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON")
    args = parser.parse_args()
    try:
        files = collect_files(Path(args.path).resolve())
        report = scan_files(files)
    except (OSError, ValueError) as exc:
        print(f"supplyguard: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"SupplyGuard scan: {len(files)} files · risk {report['risk_score']}/100 · {report['status']}")
        if not report["findings"]:
            print("No findings.")
        for finding in report["findings"]:
            location = finding["file_path"] + (f":{finding['line']}" if finding["line"] else "")
            print(f"[{finding['severity'].upper():8}] {finding['rule_id']} {location}: {finding['message']}")
            print(f"           Fix: {finding['recommendation']}")
    return 1 if any(item["severity"] in {"critical", "high"} for item in report["findings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
