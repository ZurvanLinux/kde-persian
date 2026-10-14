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
MODELS = ["gemini-3.8-flash-high", "claude-sonnet-4-6"]

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

def parse_json_response(raw: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL)
    if m:
        return json.loads(m.group(1))
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(cleaned)

def request_glossary(prompt: str) -> dict:
    for model in MODELS:
        try:
            print(f"==> Requesting glossary terms via {model}...")
            if model.startswith("claude"):
                resp = requests.post(
                    f"{GATEWAY_BASE}/messages",
                    headers={
                        "x-api-key": API_KEY,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": 4096,
                        "system": "You are the Lead Persian Localization Architect for KDE Plasma 6. Respond only with JSON.",
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=180,
                )
                resp.raise_for_status()
                data = resp.json()
                raw = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            else:
                resp = requests.post(
                    f"{GATEWAY_BASE}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                    timeout=180,
                )
                resp.raise_for_status()
                raw = resp.json()["choices"][0]["message"]["content"]

            return parse_json_response(raw)
        except Exception as exc:
            print(f"  [!] Failed with {model}: {exc}. Trying fallback...")
            continue
    raise RuntimeError("All models failed to generate glossary.")

def main():
    existing = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8")) if GLOSSARY_PATH.exists() else {}
    candidates = [t for t in extract_short_terms() if t not in existing]
    if not candidates:
        print("No new candidate terms found (ensure ./scripts/sync_svn.sh was run first).")
        return

    print(f"Found {len(candidates)} candidate UI terms across core KDE packages.")
    prompt = (
        "You are the Lead Persian Localization Architect for KDE Plasma 6.\n"
        "Review these recurring UI terms from KDE core packages and select the most important UI nouns and verbs.\n"
        "Provide standard, fluent modern Persian (fa_IR) equivalents using proper نیم‌فاصله (U+200C) and standard ی/ک.\n"
        "Return ONLY a flat JSON object mapping English terms to Persian equivalents.\n\n"
        f"Existing Glossary:\n{json.dumps(existing, ensure_ascii=False, indent=2)}\n\n"
        f"Candidate Terms (choose up to 100 most relevant):\n{json.dumps(candidates[:150], ensure_ascii=False)}"
    )

    new_terms = request_glossary(prompt)
    existing.update(new_terms)
    GLOSSARY_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(f"✓ Updated glossary with {len(new_terms)} new terms. Total terms: {len(existing)}")

if __name__ == "__main__":
    main()
