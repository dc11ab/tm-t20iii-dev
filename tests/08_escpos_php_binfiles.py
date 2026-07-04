r"""
08_escpos_php_binfiles.py - stream the escpos-php integration .bin files.

escpos-printer-db's doc/add-your-printer.md asks contributors: "For testing
out features, you can send escpos-php test files to your printer and note
the output for each file." This probe automates exactly that.

It lists mike42/escpos-php's test/integration/resources/output directory via
the GitHub API (so the file set is always current, not hardcoded), downloads
every .bin to assets/escpos-php-bin/ (cached; re-runs work offline), then
streams them to the printer one at a time -- each prefaced by a printed
banner and followed by a cut and a console pause, so every file's output can
be photographed and noted separately.

    python 08_escpos_php_binfiles.py                    # fetch + run all
    python 08_escpos_php_binfiles.py --only barcode     # substring filter
    python 08_escpos_php_binfiles.py --dir C:\bins      # use a local folder
    python 08_escpos_php_binfiles.py --no-pause         # no Enter between files
    python 08_escpos_php_binfiles.py --list             # show files, don't print

Record per-file results in docs/hardware.md ("escpos-php test files").
Heads-up: the full set prints a LOT of paper -- consider --only per session.
"""

import argparse
import json
import os
import sys
import urllib.request

from conn import RawUsb

ESC = 0x1B
GS = 0x1D

API = ("https://api.github.com/repos/mike42/escpos-php/"
       "contents/test/integration/resources/output")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, os.pardir, "assets", "escpos-php-bin")
CHUNK = 16384
UA = {"User-Agent": "tm-t20iii-dev-probe"}


def fetch_listing():
    req = urllib.request.Request(API, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        entries = json.load(r)
    return [(e["name"], e["download_url"]) for e in entries
            if e["name"].endswith(".bin")]


def ensure_cached(files):
    os.makedirs(CACHE, exist_ok=True)
    paths = []
    for name, url in files:
        path = os.path.join(CACHE, name)
        if not os.path.exists(path):
            print(f"  downloading {name} ...")
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r, \
                    open(path, "wb") as f:
                f.write(r.read())
        paths.append(path)
    return paths


def local_or_cached(args):
    if args.dir:
        return sorted(os.path.join(args.dir, n) for n in os.listdir(args.dir)
                      if n.endswith(".bin"))
    try:
        return ensure_cached(fetch_listing())
    except Exception as exc:  # noqa: BLE001
        if os.path.isdir(CACHE):
            cached = sorted(os.path.join(CACHE, n) for n in os.listdir(CACHE)
                            if n.endswith(".bin"))
            if cached:
                print(f"GitHub fetch failed ({exc}); using cached files.")
                return cached
        sys.exit(f"GitHub fetch failed ({exc}). Download the folder from\n"
                 f"  https://github.com/mike42/escpos-php/tree/master/"
                 f"test/integration/resources/output\n"
                 f"and re-run with --dir <folder>.")


def banner(p, text):
    p.write(bytes([ESC, ord("@")]))            # re-init between files
    p.write(bytes([ESC, ord("R"), 0]))
    p.write(bytes([ESC, ord("a"), 1]))
    p.write(bytes([GS, ord("!"), 0x11]))
    p.write(text.encode("ascii", "replace") + b"\n")
    p.write(bytes([GS, ord("!"), 0x00]))
    p.write(bytes([ESC, ord("a"), 0]))
    p.write(b"-" * 42 + b"\n\n")


def send_file(p, path):
    with open(path, "rb") as f:
        data = f.read()
    for i in range(0, len(data), CHUNK):
        p.write(data[i:i + CHUNK])
    return len(data)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="local folder of .bin files (offline)")
    ap.add_argument("--only", help="substring filter on file name")
    ap.add_argument("--no-pause", action="store_true",
                    help="don't wait for Enter between files")
    ap.add_argument("--list", action="store_true",
                    help="list matching files and exit (no printing)")
    args = ap.parse_args()

    paths = local_or_cached(args)
    if args.only:
        paths = [q for q in paths
                 if args.only.lower() in os.path.basename(q).lower()]
    if not paths:
        sys.exit("No .bin files matched.")

    print(f"{len(paths)} file(s):")
    for q in paths:
        print(f"  {os.path.basename(q)}  "
              f"({os.path.getsize(q)} B)" if os.path.exists(q) else q)
    if args.list:
        return

    p = RawUsb()
    for i, path in enumerate(paths, 1):
        name = os.path.basename(path)
        print(f"[{i}/{len(paths)}] {name}", flush=True)
        banner(p, name)
        sent = send_file(p, path)
        print(f"  sent {sent} bytes")
        try:
            p.write(b"\n\n\n\n")
            p.write(bytes([GS, ord("V"), 66, 0]))  # cut between files
        except Exception as exc:  # noqa: BLE001  (printer busy: warn, go on)
            print(f"  trailing feed/cut failed ({exc}); continuing")
        if not args.no_pause and i < len(paths):
            ans = input("  Enter=next file, s=stop: ").strip().lower()
            if ans == "s":
                break
    p.close()
    print("Done. Record per-file results in docs/hardware.md")
    print('("escpos-php test files" section) and photograph into artifacts/.')


if __name__ == "__main__":
    main()
