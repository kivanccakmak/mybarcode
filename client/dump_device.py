from evdev import InputDevice, ecodes, list_devices, categorize

def main():
    """
    :dev_name: String
    :return: InputDevice
        None in failure
    """
    dev = None
    devices = map(InputDevice, list_devices())

    for device in devices:
        print(device.name)

if __name__ == "__main__":
    main()
