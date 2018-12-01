# Saku Tool v0

### DEPENDENCY
- python 3.6
- imageio
- wxpython

### USAGE
Before use define your video path in config.ini first.

Support keyboard commands only.

general commands

| command | description |
| --- | --- |
| esc | back to top menu / exit input mode |
| backspace | back |
| space | enter (cuz' enter key event is blocked by wx) |
| q | quit |

top menu commands

| command | description |
| --- | --- |
| i | Open a video by booru id from PATH defined in config.ini |
| space | play / pause |
| j | pause and goto prev frame |
| k | pause and goto next frame |
| f | switch fps 24/12/6 |
| s | pause, save current frame and goto next frame, hold to save sequentially |

### FUTURE WORK
- Onion view with edge extraction
- Simple drawing
- Another renderer for comparison
- A timeline with timesheet editing