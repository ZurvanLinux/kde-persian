#!/usr/bin/env python3
import argparse
import json
import re
import time
import polib
import requests
from pathlib import Path
from datetime import datetime

# Contributor Identity (Upstream KDE Header Standard)
TRANSLATOR_NAME = "Mohammad Shafiee Sarvestani"
TRANSLATOR_EMAIL = "muhammad.shafiee@gmail.com"
TRANSLATOR_CREDIT = f"{TRANSLATOR_NAME} <{TRANSLATOR_EMAIL}>"

# Local Antigravity Tools Gateway Configuration
GATEWAY_BASE = "http://127.0.0.1:8045/v1"
API_KEY = "sk-4a8eb48773bd4f4482fd11a1a39526a2"

# Verified Active Models on Port 8045
CORE_MODEL = "claude-opus-4-6"
BULK_MODEL = "claude-sonnet-4-6"
QA_MODEL = "gemini-3.8-flash-high"

BASE_DIR = Path("/Users/mohammad/Documents/GitHub/kde-persian")
GLOSSARY_PATH = BASE_DIR / "glossary" / "glossary.json"

# Matches Qt/KDE placeholders (%1, %L1, %n), C-printf (%s, %d, %1$s), env vars ($HOME), and XML/KUIT tags
PlaceholderRegex = re.compile(r"(%\d+\$[a-zA-Z]|%L?\d+|%[a-zA-Z]|\$\{?[A-Za-z0-9_]+\}?|<[^>]+>)")
DesktopPrefixRegex = re.compile(r"^([A-Za-z0-9_-]+=)(.*)$", flags=re.DOTALL)

SYSTEM_PROMPT = """You are the Lead Persian (fa_IR) Localization Architect for KDE Plasma 6.
You are translating KDE user interface strings from English into fluent, modern, standard Persian from scratch.

CRITICAL KDE & PERSIAN LOCALIZATION RULES:
1. TONE & FLUENCY: Use formal, concise, natural software Persian (رسمی، روان و طبیعی). Never produce literal word-for-word calques (ترجمه تحت‌اللفظی).
2. ORTHOGRAPHY (نیم‌فاصله و ی/ک):
   - Strictly enforce Zero-Width Non-Joiner (U+200C / نیم‌فاصله) in verb prefixes (می‌شود، نمی‌تواند), plural suffixes (پرونده‌ها، پنجره‌ها), comparative/superlative suffixes (بهترین، بزرگ‌تر), and compound words.
   - Always use standard Persian Yeh (ی - U+06CC) and Keh (ک - U+06A9). NEVER use Arabic Yeh (ي) or Kaf (ك).
3. KDE / QT MARKUP & PLACEHOLDERS:
   - Preserve ALL placeholders verbatim: %1, %2, %L1, %n, %s, %d, $HOME, etc.
   - Do NOT invent %1 in a singular string if the English singular string (`msgid`) does not contain %1.
   - Preserve ALL KUIT / HTML / XML tags intact: <interface>, <filename>, <emphasis>, <b>, <i>, <nl/>, <para>.
4. DESKTOP & METADATA STRINGS:
   - If an English string starts with a key prefix like `Name=`, `GenericName=`, `Comment=`, or `Keywords=`, keep the exact ASCII prefix (`Name=`, etc.) untouched and translate only the value after `=`.
   - For `Keywords=` or `msgctxt "Keywords"`, separate translated keywords with ASCII semicolons `;` ending with a trailing `;`.
5. ACCELERATOR KEYS (&):
   - KDE uses '&' in English to mark keyboard accelerators (e.g., "&Open", "Save &As").
   - Strip single accelerator '&' characters in Persian translations so cursive joining is never broken. Preserve literal double ampersands ('&&') if present.
6. SPECIAL KDE CREDITS:
   - If `msgid` is "Your names" (with `msgctxt "NAME OF TRANSLATORS"`), translate strictly as: "محمد شفیعی سروستانی"
   - If `msgid` is "Your emails" (with `msgctxt "EMAIL OF TRANSLATORS"`), translate strictly as: "muhammad.shafiee@gmail.com"
7. PLURAL FORMS:
   - KDE Persian uses `nplurals=2; plural=(n != 1);`.
   - When `msgid_plural` is non-empty, return an array of 2 strings: `[singular_form, plural_form]`, matching the exact placeholders of `msgid` in `singular_form` and `msgid_plural` in `plural_form`.
8. OUTPUT FORMAT:
   - Return ONLY a valid JSON object mapping each item ID ("0", "1", ...) to its translated string (or 2-element list for plurals). Do not wrap in markdown code fences."""


def normalize_persian_orthography(text: str, src_msgid: str = "") -> str:
    """Enforces Persian Yeh/Keh, preserves desktop prefixes, and strips stray single accelerator ampersands."""
    text = text.replace("\u064a", "\u06cc").replace("\u0649", "\u06cc")  # Arabic Yeh -> Persian Yeh
    text = text.replace("\u0643", "\u06a9")  # Arabic Kaf -> Persian Keh
    # Remove single '&' not part of HTML entities or '&&'
    text = re.sub(r"(?<!&)&(?!&|[a-zA-Z0-9#]+;)", "", text)

    # Ensure Desktop prefix (e.g. Name=, Comment=) is preserved if present in source msgid
    m_src = DesktopPrefixRegex.match(src_msgid)
    if m_src:
        prefix = m_src.group(1)
        if not text.startswith(prefix):
            text = re.sub(r"^[A-Za-z0-9_-]+=", "", text).lstrip()
            text = f"{prefix}{text}"
    return text


def extract_legacy_header_comments(legacy_po_path: Path, pot_stem: str) -> str:
    """Preserves upstream KDE copyright and contributor history from SVN fa-legacy."""
    current_year = datetime.now().year
    new_credit = f"# SPDX-FileCopyrightText: {current_year} {TRANSLATOR_NAME} <{TRANSLATOR_EMAIL}>"
    legacy_style_credit = f"# {TRANSLATOR_NAME} <{TRANSLATOR_EMAIL}>, {current_year}."

    if not legacy_po_path.exists():
        return (
            f"# Copyright (C) {current_year} This file is copyright:\n"
            f"# This file is distributed under the same license as the {pot_stem} package.\n"
            f"{new_credit}\n"
        )

    lines = legacy_po_path.read_text(encoding="utf-8", errors="replace").splitlines()
    header_comments = []
    for line in lines:
        if line.startswith("#"):
            if not line.startswith("#,"):  # Ignore "#, fuzzy" on header
                header_comments.append(line)
        elif line.strip() == "":
            continue
        else:
            break

    if not any(TRANSLATOR_EMAIL in l for l in header_comments):
        header_comments.append(legacy_style_credit)

    return "\n".join(header_comments)


def call_anthropic_messages(model: str, system_prompt: str, user_content: str) -> str:
    url = f"{GATEWAY_BASE}/messages"
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 8192,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}],
    }
    for attempt in range(4):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            resp.raise_for_status()
            data = resp.json()
            for block in data.get("content", []):
                if block.get("type") == "text":
                    return block.get("text", "")
        except Exception as exc:
            if attempt == 3:
                raise
            wait_sec = 2 ** (attempt + 1)
            print(f"  [!] Gateway retry {attempt + 1}/3 in {wait_sec}s: {exc}")
            time.sleep(wait_sec)
    raise RuntimeError("Empty response from gateway")


def repair_with_flash_qa(src_text: str, candidate_fa: str) -> str:
    """Stage 3 QA: Repairs missing %1/%2 placeholders or broken XML tags via gemini-3.8-flash-high."""
    src_tokens = sorted(PlaceholderRegex.findall(src_text))
    dst_tokens = sorted(PlaceholderRegex.findall(candidate_fa))
    if src_tokens == dst_tokens:
        return candidate_fa

    prompt = (
        "Fix the Persian KDE translation below so that it preserves every placeholder and XML/HTML tag "
        f"from the English source string verbatim ({src_tokens}). Do NOT add extra placeholders. "
        "Return ONLY the corrected Persian string.\n\n"
        f"English: {src_text}\n"
        f"Draft Persian: {candidate_fa}"
    )
    try:
        resp = requests.post(
            f"{GATEWAY_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": QA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
            },
            timeout=60,
        )
        resp.raise_for_status()
        fixed = resp.json()["choices"][0]["message"]["content"].strip()
        fixed = re.sub(r"^```(?:[a-zA-Z0-9_-]+)?\s*|\s*```$", "", fixed, flags=re.MULTILINE).strip()
        return normalize_persian_orthography(fixed, src_text)
    except Exception:
        return candidate_fa


def translate_batch(batch_items: list, glossary: dict, model: str) -> dict:
    payload_items = []
    for idx, entry in enumerate(batch_items):
        payload_items.append({
            "id": str(idx),
            "msgctxt": entry.msgctxt or "",
            "msgid": entry.msgid,
            "msgid_plural": entry.msgid_plural or "",
            "comment": entry.comment or "",
        })

    prompt = (
        f"Approved Terminology Glossary (follow strictly):\n"
        f"{json.dumps(glossary, ensure_ascii=False, indent=2)}\n\n"
        f"Translate these KDE gettext entries into Persian.\n"
        f"- Singular entry -> {{\"id\": \"persian_string\"}}\n"
        f"- Plural entry (msgid_plural non-empty) -> {{\"id\": [\"singular_fa\", \"plural_fa\"]}}\n\n"
        f"Entries:\n{json.dumps(payload_items, ensure_ascii=False, indent=2)}"
    )

    raw_response = call_anthropic_messages(model, SYSTEM_PROMPT, prompt)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_response.strip(), flags=re.MULTILINE)
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def save_po_with_legacy_header(po: polib.POFile, out_po_file: Path, header_comments: str):
    po.save(str(out_po_file))
    content = out_po_file.read_text(encoding="utf-8")
    content_body = re.sub(r"^(#.*\n)+", "", content)
    out_po_file.write_text(header_comments + "\n" + content_body, encoding="utf-8")


def process_pot_file(rel_pot_path: Path, model: str, batch_size: int = 25, force: bool = False):
    pot_file = BASE_DIR / "upstream" / "templates" / rel_pot_path
    if not pot_file.exists():
        raise FileNotFoundError(f"Template not found: {pot_file}")

    legacy_po_file = (BASE_DIR / "upstream" / "fa-legacy" / rel_pot_path).with_suffix(".po")
    out_po_file = (BASE_DIR / "work" / "fa" / rel_pot_path).with_suffix(".po")
    out_po_file.parent.mkdir(parents=True, exist_ok=True)

    legacy_project_id = pot_file.stem
    if legacy_po_file.exists():
        try:
            legacy_po = polib.pofile(str(legacy_po_file))
            legacy_project_id = legacy_po.metadata.get("Project-Id-Version", pot_file.stem)
        except Exception:
            pass

    if out_po_file.exists() and not force:
        po = polib.pofile(str(out_po_file), wrapwidth=78)
    else:
        po = polib.pofile(str(pot_file), wrapwidth=78)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M+0330")
    po.metadata = {
        "Project-Id-Version": legacy_project_id,
        "Report-Msgid-Bugs-To": "https://bugs.kde.org",
        "POT-Creation-Date": po.metadata.get("POT-Creation-Date", now_str),
        "PO-Revision-Date": now_str,
        "Last-Translator": TRANSLATOR_CREDIT,
        "Language-Team": "Persian <kde-i18n-fa@kde.org>",
        "Language": "fa",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Plural-Forms": "nplurals=2; plural=(n != 1);",
        "X-Generator": f"kde-persian-pipeline ({model})",
    }

    glossary = {}
    if GLOSSARY_PATH.exists():
        glossary = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))

    header_comments = extract_legacy_header_comments(legacy_po_file, pot_file.stem)

    pending_entries = []
    for e in po:
        if e.obsolete or e.msgid == "":
            continue
        if not force and e.translated():
            continue
        pending_entries.append(e)

    total_pending = len(pending_entries)
    if total_pending == 0:
        print(f"✓ Skipping {rel_pot_path} (already 100% translated in work/fa/)")
        return

    print(f"==> Translating {rel_pot_path} ({total_pending} pending strings) using {model}...")

    for i in range(0, total_pending, batch_size):
        batch = pending_entries[i : i + batch_size]
        translations = translate_batch(batch, glossary, model)
        for idx, entry in enumerate(batch):
            if entry.msgctxt == "NAME OF TRANSLATORS" and entry.msgid == "Your names":
                entry.msgstr = "محمد شفیعی سروستانی"
                if "fuzzy" in entry.flags:
                    entry.flags.remove("fuzzy")
                continue
            if entry.msgctxt == "EMAIL OF TRANSLATORS" and entry.msgid == "Your emails":
                entry.msgstr = TRANSLATOR_EMAIL
                if "fuzzy" in entry.flags:
                    entry.flags.remove("fuzzy")
                continue

            result = translations.get(str(idx))
            if result is None:
                continue
            if entry.msgid_plural and isinstance(result, list):
                f0 = repair_with_flash_qa(entry.msgid, normalize_persian_orthography(result[0], entry.msgid))
                f1_raw = result[1] if len(result) > 1 else result[0]
                f1 = repair_with_flash_qa(entry.msgid_plural, normalize_persian_orthography(f1_raw, entry.msgid_plural))
                entry.msgstr_plural = {0: f0, 1: f1}
            elif isinstance(result, str):
                clean_str = normalize_persian_orthography(result, entry.msgid)
                entry.msgstr = repair_with_flash_qa(entry.msgid, clean_str)

            if "fuzzy" in entry.flags:
                entry.flags.remove("fuzzy")

        save_po_with_legacy_header(po, out_po_file, header_comments)
        print(f"  [{min(i + batch_size, total_pending)}/{total_pending}] checkpoint saved")

    print(f"✓ Completed & preserved upstream history: {out_po_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate KDE POT files into Persian from scratch.")
    parser.add_argument("pot_path", help="Relative path inside upstream/templates (e.g., dolphin/dolphin.pot)")
    parser.add_argument("--bulk", action="store_true", help="Use claude-sonnet-4-6 instead of claude-opus-4-6")
    parser.add_argument("--batch-size", type=int, default=25, help="Strings per API request")
    parser.add_argument("--force", action="store_true", help="Re-translate even if already translated in work/fa/")
    args = parser.parse_args()

    chosen_model = BULK_MODEL if args.bulk else CORE_MODEL
    process_pot_file(Path(args.pot_path), chosen_model, args.batch_size, args.force)
