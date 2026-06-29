"""
conn.py - shared printer connection for TM-T20III probes.

python-escpos Usb() is primary; raw pyusb is the fallback for byte-exact work.

USB IDs: Epson TM printers enumerate under vendor 0x04b8. The TM-T20III USB
product ID is commonly 0x0e03, but confirm with `python 00_list_usb.py` and
edit below if your unit differs (interface/Ethernet variants can differ).

Windows + Zadig: the printer must be bound to WinUSB / libusb-win32 so pyusb
can claim it. Only one driver can own the device; if Usb() raises a backend
error, check Zadig is bound to WinUSB, not the Epson APD printer driver.
"""

import sys

VENDOR_ID = 0x04B8          # Seiko Epson
PRODUCT_ID = 0x0E03         # TM-T20III (CONFIRM with 00_list_usb.py)
OUT_EP = 0x01
IN_EP = 0x82
PROFILE = "TM-T20III"


def get_escpos(profile=PROFILE):
    """Primary path: python-escpos Usb device using our custom profile."""
    from escpos.printer import Usb
    return Usb(VENDOR_ID, PRODUCT_ID, profile=profile,
               in_ep=IN_EP, out_ep=OUT_EP)


class RawUsb:
    """Fallback: raw pyusb bulk writes, no escpos interpretation."""

    def __init__(self, vendor=VENDOR_ID, product=PRODUCT_ID, out_ep=OUT_EP):
        import usb.core
        import usb.util
        self._util = usb.util
        dev = usb.core.find(idVendor=vendor, idProduct=product)
        if dev is None:
            raise RuntimeError(
                f"No USB device {vendor:#06x}:{product:#06x}. "
                "Run 00_list_usb.py and check the Zadig binding.")
        try:
            if dev.is_kernel_driver_active(0):
                dev.detach_kernel_driver(0)
        except (NotImplementedError, Exception):
            pass
        dev.set_configuration()
        self.dev = dev
        self.out_ep = out_ep

    def write(self, data: bytes):
        self.dev.write(self.out_ep, data)

    def read(self, in_ep=IN_EP, length=64, timeout=1000):
        return bytes(self.dev.read(in_ep, length, timeout))

    def close(self):
        self._util.dispose_resources(self.dev)


def open_printer(prefer_raw=False, profile=PROFILE):
    """Try requested path; fall back to raw with a clear message."""
    if prefer_raw:
        return ("raw", RawUsb())
    try:
        return ("escpos", get_escpos(profile))
    except Exception as exc:  # noqa: BLE001
        print(f"[conn] Usb() failed ({exc!r}); falling back to raw pyusb.",
              file=sys.stderr)
        return ("raw", RawUsb())


def writer_for(mode, p):
    """Return a uniform write(bytes) callable for either connection mode."""
    return (lambda b: p.write(b)) if mode == "raw" else p._raw
