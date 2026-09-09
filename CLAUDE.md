# CLAUDE.md — tm-t20iii-dev (repo law)

House rules in `../CLAUDE_WORKFLOW.md` apply. **On conflict, this file wins.**

## What this project is (best current understanding — owner to confirm)

R&D repo for the **Epson TM-T20III** thermal printer: profiles, character/
codepage experiments, test scripts and artifacts. The printer itself is the
production device for rr-receipt (VU6D race receipts), so findings here feed
that repo's printer issues.

- Layout observed: `profile/`, `scripts/`, `tests/` (pytest), `artifacts/`,
  `assets/`, `.yamllint`, `_issue_codepage_expansion.md`.

## Hardware truths (established in rr-receipt, apply here)

- The `@`/`|` corruption of 2026-07 was **NOT a code page issue**: the printer's
  saved `ESC R` international charset was Sweden, remapping low-ASCII. Fixed by
  pinning `ESC R 0` (USA) at job init. Any charset experiment must account for
  the printer's SAVED state, not just what the job sends.
- python-escpos 3.1 with `profile=None` is the known-working configuration;
  `profile="TM-T20II"` is the closest named profile and carries a known
  string-mismatch (our device is the T20**III**).
- Windows 11 needs WinUSB via Zadig for USB access; Linux needs the udev rule
  (VID 0x04B8, PID 0x0E28) — see rr-receipt's #12 replay notes.
- Codepage work coordinates with **rr-receipt #55** (deterministic `ESC t`
  emission, `PrinterConfig` home) and **#20** (configurator UI). Decide shared
  questions once, in whichever repo lands first, and cross-reference.

## Safety

- Anything that PRINTS costs paper and cannot be undone — batch experiments get
  a dry-run/preview mode before hardware runs.
- Never leave the device claimed: release USB handles in `finally` (the #47
  lesson from rr-receipt).

## TODO(owner)

- Confirm the repo's actual purpose statement and Python/venv setup
  (`requirements.txt` observed — pin the install command).
- State whether `_issue_codepage_expansion.md` is live work or archive.
