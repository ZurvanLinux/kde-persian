#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path("/Users/mohammad/Documents/GitHub/kde-persian")
WORK_FA = BASE_DIR / "work" / "fa"
SVN_FA = BASE_DIR / "upstream" / "fa-legacy"

def main():
    po_files = sorted(WORK_FA.rglob("*.po"))
    for src in po_files:
        rel = src.relative_to(WORK_FA)
        dst = SVN_FA / rel
        is_new = not dst.exists()

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        if is_new:
            subprocess.run(["svn", "add", "--parents", str(rel)], cwd=SVN_FA, check=False)

        print(f"==> Exported to SVN tree: {rel}")

    print("\nRun `cd upstream/fa-legacy && svn status && svn diff` to inspect changes before upstream submission.")

if __name__ == "__main__":
    main()
