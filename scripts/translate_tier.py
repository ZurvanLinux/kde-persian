#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Ensure scripts directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translate_po import process_pot_file, CORE_MODEL, BULK_MODEL, BASE_DIR

TIER1_REPOS = [
    "plasma-workspace",
    "plasma-desktop",
    "kwin",
    "systemsettings",
    "dolphin",
    "kio",
    "kxmlgui",
    "kconfigwidgets",
    "kcoreaddons",
    "kwidgetsaddons",
    "konsole",
    "kate",
    "ark",
    "spectacle",
    "okular",
    "gwenview",
    "plasma-nm",
    "plasma-pa",
    "powerdevil",
    "kscreen",
]

def main():
    parser = argparse.ArgumentParser(description="Batch-translate KDE packages by priority tier.")
    parser.add_argument("--tier", type=int, choices=[1, 2], default=1, help="1 = Core Desktop (Opus), 2 = Full Repo (Sonnet)")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    templates_root = BASE_DIR / "upstream" / "templates"
    if not templates_root.exists():
        print("Error: upstream/templates not found. Run ./scripts/sync_svn.sh first.")
        sys.exit(1)

    if args.tier == 1:
        pot_files = []
        for repo in TIER1_REPOS:
            repo_dir = templates_root / repo
            if repo_dir.exists():
                pot_files.extend(sorted(repo_dir.rglob("*.pot")))
        model = CORE_MODEL
    else:
        pot_files = sorted(templates_root.rglob("*.pot"))
        model = BULK_MODEL

    print(f"==> Starting Tier {args.tier} batch translation ({len(pot_files)} POT files) with {model}")
    for idx, pot_path in enumerate(pot_files, 1):
        rel_path = pot_path.relative_to(templates_root)
        print(f"\n[{idx}/{len(pot_files)}] Target: {rel_path}")
        try:
            process_pot_file(rel_path, model=model, batch_size=args.batch_size, force=args.force)
        except Exception as exc:
            print(f"✗ Error on {rel_path}: {exc}")

if __name__ == "__main__":
    main()
