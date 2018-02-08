import argparse
import os
import signal
import stat
import struct
import sys
import termios
import time
import traceback
import tty

def cleanup(term_fd, old_settings, joy_file):
  termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  os.remove(joy_file)
  sys.exit(0)

def get_msg(value, msg_type, axis):
  ts = int(time.time() * 1000) & (2 ** 32 - 1)
  # Below format matches that found in linux/joystick.h for js_event.
  return struct.pack("IhBB", ts, value, msg_type, axis)

# Map from char to type, button/axis, [scale factor]
button_map = {
  'y' : (1, 3),
  'b' : (1, 2),
  'a' : (1, 1),
  'x' : (1, 0),

  'f' : (1, 4),
  'g' : (1, 5),
  'h' : (1, 6),
  'j' : (1, 7),

  'z' : (2, 0, 1),
  's' : (2, 0, -1),
  'c' : (2, 1, 1),
  'v' : (2, 1, -1),
  'u' : (2, 2, 1),
  'i' : (2, 2, -1),
  'o' : (2, 3, 1),
  'p' : (2, 3, -1),

  'w' : (2, 4, 1),
  'e' : (2, 4, -1),
  'l' : (2, 5, 1),
  'k' : (2, 5, -1)
}

button_state = dict(zip(button_map.keys(), [False] * len(button_map.keys())))

MAX_AXIS_VALUE = 2 ** 15 - 1

def read_loop(out_file):
  while 1:
    ch = sys.stdin.read(1)
    if ch == 'q':
      break

    if ch in button_map:
      tup = button_map[ch]

      if button_state[ch]:
        button_state[ch] = False
        value = 0
      else:
        button_state[ch] = True
        if tup[0] == 2:
          value = MAX_AXIS_VALUE * tup[2]
        else:
          value = 1

      msg = get_msg(value, tup[0], tup[1])
      os.write(out_file, msg)
      print("Sent value %d of type %d on %s %d.\r" % (value, tup[0], ["button", "axis"][tup[0] - 1], tup[1]))
    else:
      print("Invalid key.\r")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--device", type=str, default="/dev/input/js0", nargs='?', help="Filename where joystick pipe is opened")
  args = parser.parse_args()

  os.mkfifo(args.device, 0o664 | stat.S_IFIFO)

  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)

  signals = [signal.SIGINT, signal.SIGTERM]
  for sig in signals:
    signal.signal(sig,
           lambda x, y, fd=fd, old_settings=old_settings, joy_file=args.device: cleanup(fd, old_settings, joy_file))

  out_file = os.open(args.device, os.O_WRONLY)
  tty.setraw(fd)

  try:
    read_loop(out_file)
  except Exception as e:
    traceback.print_exc()

  cleanup(fd, old_settings, args.device)
