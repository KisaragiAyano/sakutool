# Saku Tool v0.2

### DEPENDENCY
- python 3.6
- opencv
- wxpython

### USAGE
Before use define your video path in config.ini first.

Support keyboard commands only.

##### General commands

| command | description |
| --- | --- |
| esc | back to top menu / exit input mode |
| backspace | back |
| space | enter (cuz' enter key event is blocked by wx) |
| q | quit |

##### Top menu commands

| command | description |
| --- | --- |
| i | Open a video by booru id from PATH defined in config.ini |
| space | play / pause |
| j | pause and goto prev frame |
| k | pause and goto next frame |
| f | switch fps 24/12/6 |
| c | switch canny |
| m | switch komas 1/2/3 |
| o | switch onion layers 0/1/2/3 |
| g | switch grid |
| s | pause, save current frame and goto next frame, hold to save sequentially |
| q | exit |

### FUTURE WORK
- Simple drawing
- Another renderer for comparison
- A timeline with timesheet editing