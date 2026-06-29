"""
00_list_usb.py - confirm the TM-T20III's USB identity and endpoints. Run first.

    python 00_list_usb.py

Prints every Epson (0x04b8) USB device via the libusb backend so you can
correct conn.py if your unit enumerates differently. If nothing prints while
the printer is on and cabled, Zadig hasn't bound it to WinUSB/libusb yet (or
the Epson APD driver still owns it).
"""

import usb.core
import usb.util

EPSON = 0x04B8


def main():
    devices = list(usb.core.find(find_all=True, idVendor=EPSON))
    if not devices:
        print("No Epson (0x04b8) USB devices found via libusb.")
        print("Check: printer on, cable seated, Zadig bound to WinUSB/"
              "libusb-win32 (not Epson APD).")
        return
    for dev in devices:
        print(f"Device {dev.idVendor:#06x}:{dev.idProduct:#06x}")
        try:
            print(f"  Manufacturer: {usb.util.get_string(dev, dev.iManufacturer)}")
            print(f"  Product:      {usb.util.get_string(dev, dev.iProduct)}")
        except Exception as exc:  # noqa: BLE001
            print(f"  (string descriptors unreadable: {exc})")
        for cfg in dev:
            for intf in cfg:
                print(f"  Interface {intf.bInterfaceNumber} "
                      f"(class {intf.bInterfaceClass})")
                for ep in intf:
                    d = ("IN" if usb.util.endpoint_direction(ep.bEndpointAddress)
                         == usb.util.ENDPOINT_IN else "OUT")
                    print(f"    Endpoint {ep.bEndpointAddress:#04x} {d} "
                          f"type={usb.util.endpoint_type(ep.bmAttributes)}")
        print()


if __name__ == "__main__":
    main()
