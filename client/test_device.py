from evdev import InputDevice, ecodes, list_devices, categorize
import sys
from constants import Constants

def dump():
    """
    :dev_name: String
    :return: InputDevice
        None in failure
    """
    dev = None
    devices = map(InputDevice, list_devices())

    for device in devices:
        print(device.name)

def find_device(name):
    """
    """

    dev = None
    devices = map(InputDevice, list_devices())

    for device in devices:
        if name.lower() in device.name.lower():
            print('found {}'.format(name))
            return InputDevice(device.fn)
    return dev

def task_loop(dev):
    """reads barcode and updates sql database
    :dev: InputDevice
    """
    barcode = ""
    scancodes = Constants.scancodes()
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            # Catch only keydown, and not Enter
            if data.keystate == 1 and data.scancode != 42:
                if data.scancode == 28:
                    barcode = barcode.replace("=", "-")
                    print(barcode)
                    barcode = ""
                else:
                    barcode += scancodes[data.scancode]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        dump()
        sys.exit(0)
    elif len(sys.argv) == 2:
        dev = find_device(sys.argv[1])
        if dev is None:
            print("failed to find {}".format(sys.argv[1]))
            sys.exit(1)
        task_loop(dev)
    else:
        print('invalid usage')
        sys.exit(1)
