"""
06_profile_smoke.py - validate the TM-T20III profile via python-escpos.

Once TM-T20III resolves as a profile (see scripts/build_capabilities.py), this
exercises the high-level API the way rr-receipt will:
  * report what python-escpos thinks the profile supports,
  * print @ and | with the international set pinned to USA,
  * auto-encode Swedish text (profile codePages doing its job),
  * print a QR + barcode + a raster image (feature flags).

    python 06_profile_smoke.py
"""

from conn import get_escpos, PROFILE
from escpos.capabilities import get_profile

ESC = 0x1B


def show_caps():
    prof = get_profile(PROFILE)
    print(f"Profile: {prof.name}")
    cps = prof.codePages
    print(f"  code pages: {len(cps)}")
    for k in ("CP437", "CP850", "CP865", "CP1252", "CP858"):
        print(f"    {k}: {'yes' if k in cps.values() else 'no'}")


def main():
    show_caps()
    p = get_escpos()

    p._raw(bytes([ESC, ord("R"), 0]))   # USA: correct @ and |
    p.set(align="center")
    p.text("TM-T20III profile smoke\n\n")
    p.set(align="left")

    p.text("at/pipe: user@host.com | a|b|c\n")
    p.text("auto Swedish: Smörgåstårta åäö ÅÄÖ\n")

    for cp in ("CP1252", "CP850", "CP865"):
        try:
            p.charcode(cp)
            p.text(f"[{cp}] Smörgås åäö | @\n")
        except Exception as exc:  # noqa: BLE001
            p.text(f"[{cp}] error: {exc}\n")

    p.text("\n")
    p.qr("https://github.com/dc11ab/tm-t20iii-dev", size=6)
    p.barcode("123456789012", "EAN13", width=2, height=64, pos="below")
    p.text("\n\n\n")
    p.cut()


if __name__ == "__main__":
    main()
