#!/usr/bin/env python3
"""
build_capabilities.py - make TM-T20III resolvable inside python-escpos.

python-escpos ships a generated capabilities.json built from the
escpos-printer-db YAML sources. To use our profile we regenerate that JSON (or
point the library at a custom file). No actual compilation happens.

ROUTE A (upstream parity): regenerate from a checkout of escpos-printer-db that
includes our TM-T20III.yml.
  1. git clone https://github.com/receipt-print-hq/escpos-printer-db
  2. copy profile/TM-T20III.yml into escpos-printer-db/data/profile/
  3. run the DB's own build to emit capabilities.json
  4. python build_capabilities.py --install <path/to/capabilities.json>

ROUTE B (no global change): set the env var python-escpos reads for an external
capabilities file:
  set ESCPOS_CAPABILITIES_FILE=C:\\path\\to\\capabilities.json   (Windows)
  Then Usb(..., profile="TM-T20III") resolves from your file.

This script does the Route A file plumbing and prints the Route B hint. It does
NOT convert YAML->JSON (that is escpos-printer-db's job, with its own schema
validation -- which is exactly what catches any wrong [VERIFY] codec names).
"""

import argparse
import os
import shutil
import sys


def find_installed_capabilities():
    try:
        import escpos
    except ImportError:
        sys.exit("python-escpos not importable in this environment.")
    candidate = os.path.join(os.path.dirname(escpos.__file__),
                             "capabilities.json")
    return candidate if os.path.exists(candidate) else None


def install(new_json):
    target = find_installed_capabilities()
    if not target:
        sys.exit("Could not locate installed capabilities.json.")
    backup = target + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(target, backup)
        print(f"Backed up original -> {backup}")
    shutil.copy2(new_json, target)
    print(f"Installed {new_json} -> {target}")
    print("Verify: python -c \"from escpos.capabilities import get_profile; "
          "print(get_profile('TM-T20III').name)\"")


def restore():
    target = find_installed_capabilities()
    backup = (target or "") + ".orig"
    if target and os.path.exists(backup):
        shutil.copy2(backup, target)
        print(f"Restored original from {backup}")
    else:
        print("No backup found; nothing to restore.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--install", metavar="capabilities.json")
    g.add_argument("--restore", action="store_true")
    g.add_argument("--where", action="store_true")
    args = ap.parse_args()
    if args.where:
        print(find_installed_capabilities() or "not found")
    elif args.install:
        install(args.install)
        print("\nRoute B alternative: set ESCPOS_CAPABILITIES_FILE instead.")
    elif args.restore:
        restore()


if __name__ == "__main__":
    main()
