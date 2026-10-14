#!/usr/bin/env python3
import json
import re
import polib
import requests
from pathlib import Path

BASE_DIR = Path("/Users/mohammad/Documents/GitHub/kde-persian")
GLOSSARY_PATH = BASE_DIR / "glossary" / "glossary.json"
GATEWAY_BASE = "http://127.0.0.1:8045/v1"
API_KEY = "sk-4a8eb48773bd4f4482fd11a1a39526a2"
MODEL = "gemini-3.1-pro-high"

CORE_PACKAGES = [
    "plasma-workspace/plasmashell.pot",
    "dolphin/dolphin.pot",
    "systemsettings/systemsettings.pot",
    "kio/kio6.pot",
    "kwin/kwin.pot",
]

def extract_short_terms() -> list[str]:
    terms = set()
    for rel_path in CORE_PACKAGES:
        pot_path = BASE_DIR / "upstream" / "templates" / rel_path
        if not pot_path.exists():
            continue
        po = polib.pofile(str(pot_path))
        for entry in po:
            clean = entry.msgid.replace("&", "").strip()
            if 1 <= len(clean.split()) <= 3 and clean.isascii() and not any(c in clean for c in "%<>/:="):
                terms.add(clean)
    return sorted(terms)[:500]

def main():
    existing = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8")) if GLOSSARY_PATH.exists() else {}
    candidates = [t for t in extract_short_terms() if t not in existing]
    if not candidates:
        print("No new candidate terms found (ensure ./scripts/sync_svn.sh was run first).")
        return

    prompt = (
        "You are the Lead Persian Localization Architect for KDE Plasma 6.\n"
        "Review these recurring UI terms from KDE core packages and select the most important UI nouns and verbs.\n"
        "Provide standard, fluent modern Persian (fa_IR) equivalents using proper نیم‌فاصله (U+200C) and standard ی/ک.\n"
        "Return ONLY a flat JSON object mapping English terms to Persian equivalents.\n\n"
        f"Existing Glossary:\n{json.dumps(existing, ensure_ascii=False, indent=2)}\n\n"
        f"Candidate Terms:\n{json.dumps(candidates, ensure_ascii=False)}"
    )

    resp = requests.post(
        f"{GATEWAY_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        },
        timeout=180,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)
    new_terms = json.loads(cleaned)

    existing.update(new_terms)
    GLOSSARY_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(f"✓ Updated glossary with {len(new_terms)} new terms. Total terms: {len(existing)}")

if __name__ == "__main__":
    main()
