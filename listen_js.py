import argparse
import select
import struct
import time

if __name__ == "__main__":
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--device", type=str, default="/dev/input/js0", nargs='?', help="Filename of joystick pipe to listen to")
  args = parser.parse_args()

  f = open(args.device, 'rb')

  in_press = False
  char_seq = b''

  EVENT_BYTES = 8 # Length of each joystick event in bytes.

  while 1:
    if select.select([f], [], [], 0.0)[0]:
      event = f.read(EVENT_BYTES)
      # Below format matches that found in linux/joystick.h for js_event.
      tup = struct.unpack("IhBB", event)
      print("Got event", tup)
    else:
      time.sleep(0.1)
