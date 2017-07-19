# keyjs

keyjs allows you to emulate a joystick using the keyboard. Tested with Python 3.

keyjs creates a named pipe to which it writes Linux joystick events after characters are sent to the controlling terminal.

## fake_joy.py

Must be run as root to emulate a joystick in `/dev`.

Run `python fake_joy.py`.

Key bindings and joystick FIFO can be changed inside.

## listen_js.py

Listens to a joystick file and outputs events found.

## Limitations

Does not send any preamble. Axis values are always at the max; intermediate values are not supported.
A button press and release requires two keystrokes.
