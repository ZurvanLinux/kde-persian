#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Ensure scripts directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from translate_po import process_pot_file, CORE_MODEL, BULK_MODEL, BASE_DIR

TIER1_REPOS = [
    # 1. Fundamental KDE Frameworks UI & Core
    "kcoreaddons",
    "kwidgetsaddons",
    "kconfigwidgets",
    "kxmlgui",
    "kio",
    # 2. Core Desktop System Control & File Management
    "systemsettings",
    "kdialog",
    "dolphin",
    "kwin",
    "kscreen",
    "powerdevil",
    # 3. Plasma Desktop Shell & Applets
    "plasma-workspace",
    "plasma-desktop",
    "plasma-nm",
    "plasma-pa",
    # 4. Essential Desktop Productivity Apps
    "konsole",
    "kate",
    "ark",
    "spectacle",
    "okular",
    "gwenview",
]

IN_PROGRESS_REPOS = [
    "kio",
    "plasma-workspace",
    "plasma-desktop",
    "plasma-nm",
]

def main():
    parser = argparse.ArgumentParser(description="Batch-translate KDE packages by priority tier.")
    parser.add_argument("--tier", type=int, choices=[1, 2], default=1, help="1 = Core Desktop (Opus), 2 = Full Repo (Sonnet)")
    parser.add_argument("--repo", type=str, default="", help="Optionally translate only a specific repository name (e.g., dolphin, kio)")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--engine", choices=["dual", "google"], default="dual", help="Translation engine: dual or google")
    parser.add_argument("--finish-in-progress", action="store_true", help="Only complete the remaining strings in kio, plasma-workspace, plasma-desktop, plasma-nm")
    parser.add_argument("--after-in-progress-google", action="store_true", help="Finish in-progress repos first with dual engine, then translate all remaining repos with google engine")
    args = parser.parse_args()

    templates_root = BASE_DIR / "upstream" / "templates"
    if not templates_root.exists():
        print("Error: upstream/templates not found. Run ./scripts/sync_svn.sh first.")
        sys.exit(1)

    # Workflow 1: --after-in-progress-google
    if args.after_in_progress_google:
        print("==> Step 1: Completing in-progress repositories (kio, plasma-workspace, plasma-desktop, plasma-nm) with dual engine...")
        in_progress_pots = []
        for repo in IN_PROGRESS_REPOS:
            repo_dir = templates_root / repo
            if repo_dir.exists():
                in_progress_pots.extend(sorted(repo_dir.rglob("*.pot")))

        for idx, pot_path in enumerate(in_progress_pots, 1):
            rel_path = pot_path.relative_to(templates_root)
            print(f"\n[In-Progress {idx}/{len(in_progress_pots)}] Target: {rel_path}")
            try:
                process_pot_file(rel_path, model=CORE_MODEL, batch_size=args.batch_size, force=args.force, engine="dual")
            except Exception as exc:
                print(f"✗ Error on {rel_path}: {exc}")

        print("\n==> Step 2: In-progress repositories completed! Now translating remaining packages ONLY with Google Translate engine...")
        remaining_repos = [r for r in TIER1_REPOS if r not in IN_PROGRESS_REPOS]
        remaining_pots = []
        for repo in remaining_repos:
            repo_dir = templates_root / repo
            if repo_dir.exists():
                remaining_pots.extend(sorted(repo_dir.rglob("*.pot")))

        for idx, pot_path in enumerate(remaining_pots, 1):
            rel_path = pot_path.relative_to(templates_root)
            print(f"\n[Google Engine {idx}/{len(remaining_pots)}] Target: {rel_path}")
            try:
                process_pot_file(rel_path, model=CORE_MODEL, batch_size=max(args.batch_size, 35), force=args.force, engine="google")
            except Exception as exc:
                print(f"✗ Error on {rel_path}: {exc}")
        return

    # Workflow 2: --finish-in-progress
    if args.finish_in_progress:
        pot_files = []
        for repo in IN_PROGRESS_REPOS:
            repo_dir = templates_root / repo
            if repo_dir.exists():
                pot_files.extend(sorted(repo_dir.rglob("*.pot")))
        model = CORE_MODEL
    elif args.repo:
        repo_dir = templates_root / args.repo
        if not repo_dir.exists():
            print(f"Error: Repository {args.repo} not found in upstream/templates.")
            sys.exit(1)
        pot_files = sorted(repo_dir.rglob("*.pot"))
        model = CORE_MODEL if args.tier == 1 else BULK_MODEL
    elif args.tier == 1:
        pot_files = []
        for repo in TIER1_REPOS:
            repo_dir = templates_root / repo
            if repo_dir.exists():
                pot_files.extend(sorted(repo_dir.rglob("*.pot")))
        model = CORE_MODEL
    else:
        pot_files = sorted(templates_root.rglob("*.pot"))
        model = BULK_MODEL

    print(f"==> Starting translation queue ({len(pot_files)} POT files) with model={model}, engine={args.engine}")
    for idx, pot_path in enumerate(pot_files, 1):
        rel_path = pot_path.relative_to(templates_root)
        print(f"\n[{idx}/{len(pot_files)}] Target: {rel_path}")
        try:
            process_pot_file(rel_path, model=model, batch_size=args.batch_size, force=args.force, engine=args.engine)
        except Exception as exc:
            print(f"✗ Error on {rel_path}: {exc}")

if __name__ == "__main__":
    main()
