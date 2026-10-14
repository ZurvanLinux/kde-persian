#!/usr/bin/env python3
import subprocess
import sys
import polib
from pathlib import Path

BASE_DIR = Path("/Users/mohammad/Documents/GitHub/kde-persian")
WORK_FA = BASE_DIR / "work" / "fa"

def validate_file(po_path: Path) -> list[str]:
    errors = []
    res = subprocess.run(
        ["msgfmt", "--check", "--statistics", str(po_path), "-o", "/dev/null"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        errors.append(f"msgfmt error: {res.stderr.strip()}")

    po = polib.pofile(str(po_path))
    for entry in po:
        texts = [entry.msgstr] if not entry.msgid_plural else list(entry.msgstr_plural.values())
        for t in texts:
            if "\u064a" in t or "\u0643" in t:
                errors.append(f"Arabic Yeh/Kaf found in msgid: {entry.msgid[:40]!r}")
    return errors

def main():
    po_files = sorted(WORK_FA.rglob("*.po"))
    if not po_files:
        print("No .po files found in work/fa/.")
        return

    failed = 0
    for po_path in po_files:
        rel = po_path.relative_to(WORK_FA)
        errs = validate_file(po_path)
        if errs:
            failed += 1
            print(f"✗ FAILED: {rel}")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"✓ PASSED: {rel}")

    if failed:
        sys.exit(1)
    print(f"\nAll {len(po_files)} files passed strict KDE & Persian validation.")

if __name__ == "__main__":
    main()
