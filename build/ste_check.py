#!/usr/bin/env python3
"""Check the English text of the Markdown files against ASD-STE100 rules.

    python3 build/ste_check.py                 # docs/, README.md, CONTRIBUTING.md
    python3 build/ste_check.py docs/essen.md   # single file
    python3 build/ste_check.py --strict        # exit code 1 if there are findings

The check is a help for the writer. It cannot replace a review with the
ASD-STE100 dictionary. It finds

  * procedural sentences with more than 20 words, descriptive sentences with
    more than 25 words, paragraphs with more than 6 sentences,
  * words that are not approved (list in build/ste_terms.yml),
  * -ing forms that are not technical names,
  * possible passive voice,
  * semicolons and dashes (house style).

German text (forms) is ignored. Ignore a block with
<!-- ste-ignore-start --> ... <!-- ste-ignore-end -->.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TERMS = yaml.safe_load((ROOT / "build" / "ste_terms.yml").read_text(encoding="utf-8"))

UNAPPROVED = {k.lower(): v for k, v in TERMS["unapproved"].items()}
TECHNICAL = {w.lower() for w in TERMS.get("technical_names", [])}
ING_OK = {w.lower() for w in TERMS.get("ing_allowed", [])}

PROCEDURAL_MAX, DESCRIPTIVE_MAX, PARAGRAPH_MAX = 20, 25, 6

IMPERATIVES = {
    "activate", "add", "attach", "cancel", "change", "complete", "connect", "continue",
    "do", "download", "examine", "fill", "follow", "get", "install", "keep", "log",
    "look", "make", "mount", "move", "open", "put", "read", "refer", "register",
    "remove", "run", "select", "send", "set", "speak", "start", "stop", "tell",
    "upload", "use", "wait", "write", "commit", "push", "pay", "claim",
}
GERMAN = {"der", "die", "das", "und", "ist", "sie", "mit", "für", "nicht", "ein",
          "eine", "den", "dem", "zur", "von", "bei", "auf", "im", "oder", "wird",
          "werden", "ihr", "ihre", "bitte", "sich", "an", "zu", "des"}
ABBREV = ["e.g.", "i.e.", "Dr.", "Prof.", "Nr.", "Dez.", "Str.", "No.", "z.B.", "ca.",
          "vs.", "med.", "ggf."]
PARTICIPLES_ADJ = {"approved", "registered", "completed", "expired", "permitted",
                   "encrypted", "mounted", "linked", "scheduled", "necessary",
                   "selected", "listed", "pinned", "signed", "self-signed", "paid"}
PASSIVE = re.compile(r"\b(is|are|was|were|be|been)\s+(?:not\s+)?(\w+ed|made|done|given|"
                     r"sent|shown|written|kept|put|taken|seen|known|found|built)\b", re.I)


def clean_inline(text):
    text = re.sub(r"`[^`]*`", "X", text)                        # inline code
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)            # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)        # links -> text
    text = re.sub(r"\{[^}]*\}", "", text)                       # attr lists
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)                         # html tags
    text = re.sub(r"https?://[^\s)]*[^\s).,;]", "URL", text)
    text = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "EMAIL", text)
    text = re.sub(r"[*_]{1,2}", "", text)                       # emphasis
    return text.strip()


def sentences(text):
    protected = text
    for i, ab in enumerate(ABBREV):
        protected = protected.replace(ab, f"\u0000{i}\u0000")
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", protected)
    out = []
    for p in parts:
        for i, ab in enumerate(ABBREV):
            p = p.replace(f"\u0000{i}\u0000", ab)
        if p.strip():
            out.append(p.strip())
    return out


def words(sentence):
    return re.findall(r"[A-Za-zÄÖÜäöüß0-9][\w'’./@+-]*", sentence)


def is_german(text):
    toks = [w.lower() for w in re.findall(r"[A-Za-zÄÖÜäöüß]+", text)]
    return sum(t in GERMAN for t in toks) >= 2 or any(c in text for c in "äöüß")


def is_procedural(sentence):
    toks = [w.lower() for w in words(sentence)]
    if not toks:
        return False
    if toks[0] in IMPERATIVES:
        return True
    if toks[0] in ("if", "when", "after", "before", "to", "for") and "," in sentence:
        after = sentence.split(",", 1)[1].strip().split(" ")
        return bool(after) and after[0].lower().strip(".") in IMPERATIVES
    return False


def units(path):
    """Return (line number, kind, text). kind is 'para', 'step', 'item' or 'cell'."""
    lines = path.read_text(encoding="utf-8").split("\n")
    i, n = 0, len(lines)
    if lines and lines[0].strip() == "---":                     # front matter
        i = 1
        while i < n and lines[i].strip() != "---":
            i += 1
        i += 1
    ignore = in_code = in_comment = False
    para, para_start = [], 0

    def flush():
        nonlocal para
        if para:
            yield_list.append((para_start, "para", " ".join(para)))
            para = []

    yield_list = []
    while i < n:
        raw = lines[i]
        line = raw.strip()
        lineno = i + 1
        i += 1
        if "ste-ignore-start" in line:
            ignore = True
        if "ste-ignore-end" in line:
            ignore = False
            continue
        if ignore:
            continue
        if line.startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if in_comment or line.startswith("<!--"):
            in_comment = "-->" not in line
            continue
        if not line:
            flush()
            continue
        if line.startswith("#"):
            flush()
            continue
        if line.startswith("|"):
            flush()
            if re.match(r"^\|[\s:|-]+\|?$", line):
                continue
            prev = lines[i - 2].strip() if i >= 2 else ""
            nxt = lines[i].strip() if i < n else ""
            if re.match(r"^\|[\s:|-]+\|?$", nxt):              # header row
                continue
            for cell in line.strip("|").split("|"):
                cell = clean_inline(cell)
                if cell:
                    yield_list.append((lineno, "cell", cell))
            continue
        m = re.match(r"^([-*]|\d+\.)\s+(.*)$", line)
        if m:
            flush()
            kind = "step" if m.group(1)[0].isdigit() else "item"
            yield_list.append((lineno, kind, clean_inline(m.group(2))))
            continue
        if line.startswith(">"):
            line = line.lstrip("> ").strip()
        if not para:
            para_start = lineno
        para.append(clean_inline(line))
    flush()
    return yield_list


def check_file(path):
    findings = []
    for lineno, kind, text in units(path):
        if not text or is_german(text):
            continue
        sents = sentences(text)
        if kind == "para" and len(sents) > PARAGRAPH_MAX:
            findings.append((lineno, "paragraph", f"{len(sents)} sentences (max {PARAGRAPH_MAX})"))
        for s in sents:
            n = len(words(s))
            procedural = kind == "step" or is_procedural(s)
            limit = PROCEDURAL_MAX if procedural else DESCRIPTIVE_MAX
            if n > limit:
                findings.append((lineno, "length", f"{n} words (max {limit}): {s[:70]}..."))
            low = s.lower()
            for tech in TECHNICAL:
                low = low.replace(tech, " ")
            for term, alt in UNAPPROVED.items():
                if term in TECHNICAL:
                    continue
                pat = r"(?<![\w-])" + re.escape(term) + r"(?![\w-])"
                if re.search(pat, low):
                    findings.append((lineno, "word", f'"{term}" is not approved, use {alt}'))
            for w in words(s):
                wl = w.lower().strip(".,")
                if wl.endswith("ing") and len(wl) > 4 and wl not in ING_OK and w[0].islower():
                    findings.append((lineno, "-ing", f'"{w}"'))
            for m in PASSIVE.finditer(s):
                if m.group(2).lower() not in PARTICIPLES_ADJ:
                    findings.append((lineno, "passive", f'"{m.group(0)}"'))
            if ";" in s:
                findings.append((lineno, "style", "semicolon"))
            if "—" in s or "–" in s:
                findings.append((lineno, "style", "dash"))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--strict", action="store_true", help="exit code 1 if there are findings")
    args = ap.parse_args()
    files = args.files or sorted((ROOT / "docs").rglob("*.md")) + [
        ROOT / "README.md", ROOT / "CONTRIBUTING.md"]
    files = [f for f in files if "downloads" not in f.parts]
    total = 0
    for f in files:
        for lineno, rule, msg in check_file(f):
            total += 1
            rel = f.resolve().relative_to(ROOT) if ROOT in f.resolve().parents else f
            print(f"{rel}:{lineno}: [{rule}] {msg}")
    print(f"ASD-STE100 check: {total} finding(s) in {len(files)} file(s)")
    if args.strict and total:
        sys.exit(1)


if __name__ == "__main__":
    main()
