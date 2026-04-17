#!/usr/bin/env python3
"""
hammerin_gate.py — Validator esterno deterministico per Hammerin'Claude v4.

Esegue i 3 check del Gate d'Ispezione dopo ogni strato, senza fare
affidamento sulla disciplina di Opus:

  1. ALLOWLIST — i file modificati rientrano in files_allowlist del blocco attivo
  2. CONTRATTO — ogni identificatore tecnico del campo `contratto` appare nel diff
  3. RIGHE     — righe aggiunte <= token_cap_output * 0.5 (solo warning)

Invocazione tipica (dalla skill, dopo lo strato):

    python3 /root/.claude/skills/hammerin-claude/hooks/hammerin_gate.py \
        --cwd /home/webportal/www/progetto-x

Exit code:
    0 = pass (o nessun workorder / active_agent assente → allow)
    1 = fail di un check bloccante (allowlist o contratto)
    2 = errore di configurazione (workorder malformato, cwd non valida)
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

STATE_DIR = Path("/home/webportal/.hammerin-state")
TOKEN_TO_LINES_RATIO = 0.5  # ~2 token per riga di codice

# Regex per estrarre identificatori "tecnici" dal contratto.
# Evita falsi positivi su parole italiane comuni (Tabella, Log, Risposta…)
# catturando solo nomi che hanno forma di identificatore di codice.
CONTRACT_TOKEN_PATTERNS = [
    re.compile(r"/[A-Za-z_][\w/{}-]*"),                     # path API: /api/assets/{id}/log
    re.compile(r"\b[a-z_][a-z0-9_]*_[a-z0-9_]+\b"),         # snake_case (>=1 underscore)
    re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]+)+\b"),  # CamelCase multi-gruppo
    re.compile(r"\b[a-z][a-z0-9]+(?:[A-Z][A-Za-z0-9]+)+\b"),  # camelCase multi-gruppo
]

# Identificatori tecnici comunissimi ma non "nomi di codice": evitiamo di
# pretenderli nel diff perché generano rumore.
TOKEN_STOPLIST = {
    "http_status",
    "status_code",
    "content_type",
}


def err(msg: str) -> None:
    print(msg, file=sys.stderr)


def run(cmd: list[str], cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"comando fallito: {' '.join(cmd)}\n{r.stderr}")
    return r.stdout


def discover_workorder(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"workorder non trovato: {p}")
        return p
    candidates = sorted(STATE_DIR.glob("*-workorder.json"))
    if not candidates:
        raise FileNotFoundError(f"nessun *-workorder.json in {STATE_DIR}")
    if len(candidates) > 1:
        err(f"[WARN] trovati {len(candidates)} workorder, uso il primo: {candidates[0].name}")
    return candidates[0]


def load_workorder(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise RuntimeError(f"workorder JSON malformato: {e}")


def collect_diff(cwd: Path, base_ref: str) -> tuple[list[str], str]:
    """Ritorna (file_list, diff_text) rispetto a base_ref + untracked."""
    try:
        tracked_names = run(["git", "diff", "--name-only", base_ref], cwd).splitlines()
        tracked_diff = run(["git", "diff", base_ref], cwd)
        untracked = run(["git", "ls-files", "--others", "--exclude-standard"], cwd).splitlines()
    except RuntimeError as e:
        raise RuntimeError(f"git diff fallito in {cwd}: {e}")

    files = [f for f in tracked_names if f] + [f for f in untracked if f]

    untracked_content = ""
    for u in untracked:
        if not u:
            continue
        full = cwd / u
        if full.is_file():
            try:
                body = full.read_text(errors="replace")
                untracked_content += f"\n+++ b/{u}\n" + "".join(f"+{line}\n" for line in body.splitlines())
            except OSError:
                pass

    return files, tracked_diff + untracked_content


def glob_any(path: str, patterns: Iterable[str]) -> str | None:
    for p in patterns:
        if fnmatch.fnmatch(path, p):
            return p
    return None


def check_allowlist(files: list[str], allowlist: list[str], denylist: list[str]) -> list[str]:
    failures: list[str] = []
    for f in files:
        allow_match = glob_any(f, allowlist)
        if not allow_match:
            failures.append(f"file fuori allowlist: {f}")
            continue
        # denylist con lo stesso trattamento del hook bash: "*" ignorato se c'è allow match
        deny_match = glob_any(f, [d for d in denylist if d != "*"])
        if deny_match:
            failures.append(f"file in denylist ({deny_match}): {f}")
    return failures


def extract_contract_tokens(contratto: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pat in CONTRACT_TOKEN_PATTERNS:
        for m in pat.findall(contratto):
            if m in seen or m in TOKEN_STOPLIST:
                continue
            # filtra path troppo corti (es: "/a")
            if m.startswith("/") and len(m) < 4:
                continue
            seen.add(m)
            found.append(m)
    return found


def check_contract(contratto: str, diff_text: str) -> tuple[list[str], list[str]]:
    tokens = extract_contract_tokens(contratto)
    missing = [t for t in tokens if t not in diff_text]
    return tokens, missing


def count_added_lines(diff_text: str) -> int:
    # righe che iniziano con '+' ma non '+++' (header file)
    n = 0
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Hammerin'Claude — gate validator")
    ap.add_argument("--workorder", help="path esplicito al workorder JSON")
    ap.add_argument("--cwd", default=os.getcwd(), help="repo git del progetto")
    ap.add_argument("--base-ref", default="HEAD", help="base git per diff (default HEAD)")
    ap.add_argument("--agent", help="override del campo active_agent")
    ap.add_argument("--skip", default="", help="csv di check da saltare: allowlist,contract,lines")
    args = ap.parse_args()

    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    cwd = Path(args.cwd).resolve()
    if not (cwd / ".git").exists():
        err(f"[gate] cwd non è un repo git: {cwd}")
        return 2

    try:
        wo_path = discover_workorder(args.workorder)
    except FileNotFoundError as e:
        err(f"[gate] {e} — allow (nessun gate da applicare)")
        return 0

    try:
        wo = load_workorder(wo_path)
    except RuntimeError as e:
        err(f"[gate] {e}")
        return 2

    agent = args.agent or wo.get("active_agent", "").strip()
    if not agent:
        err(f"[gate] active_agent vuoto in {wo_path.name} — allow")
        return 0

    blocco = wo.get("blocchi", {}).get(agent)
    if not blocco:
        err(f"[gate] blocco '{agent}' non trovato nel workorder")
        return 2

    allowlist = blocco.get("files_allowlist", [])
    denylist = blocco.get("files_denylist", [])
    contratto = blocco.get("contratto", "")
    cap_out = int(blocco.get("token_cap_output", 0))
    cap_lines = int(cap_out * TOKEN_TO_LINES_RATIO)

    try:
        files, diff_text = collect_diff(cwd, args.base_ref)
    except RuntimeError as e:
        err(f"[gate] {e}")
        return 2

    print(f"━━━ GATE agent='{agent}' files={len(files)} workorder={wo_path.name} ━━━")

    blocking_fail = False

    # Check 1 — allowlist
    if "allowlist" in skip:
        print("[SKIP] check 1 allowlist")
    else:
        fails = check_allowlist(files, allowlist, denylist)
        if fails:
            err("[FAIL] Check 1 allowlist:")
            for f in fails:
                err(f"  - {f}")
            err(f"  allowlist consentita: {allowlist}")
            blocking_fail = True
        else:
            print(f"[OK] Check 1 allowlist — {len(files)} file in allowlist")

    # Check 2 — contratto
    if "contract" in skip:
        print("[SKIP] check 2 contratto")
    elif not contratto:
        print("[WARN] contratto vuoto — skip check 2")
    else:
        tokens, missing = check_contract(contratto, diff_text)
        if not tokens:
            print("[WARN] nessun identificatore tecnico estratto dal contratto — skip check 2")
        elif missing:
            err(f"[FAIL] Check 2 contratto — {len(missing)}/{len(tokens)} identificatori mancanti nel diff:")
            for t in missing:
                err(f"  - {t}")
            blocking_fail = True
        else:
            print(f"[OK] Check 2 contratto — tutti i {len(tokens)} identificatori presenti")

    # Check 3 — righe (warning, non blocca)
    if "lines" in skip:
        print("[SKIP] check 3 righe")
    elif cap_lines <= 0:
        print("[WARN] token_cap_output non impostato — skip check 3")
    else:
        added = count_added_lines(diff_text)
        if added > cap_lines:
            err(f"[WARN] Check 3 righe — +{added} aggiunte > cap {cap_lines} (token_cap={cap_out})")
        else:
            print(f"[OK] Check 3 righe — +{added} / cap {cap_lines}")

    return 1 if blocking_fail else 0


if __name__ == "__main__":
    sys.exit(main())
