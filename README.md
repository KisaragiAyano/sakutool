# Saku Tool v0.3

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
| q | quit |

##### Top menu commands

| command | description |
| --- | --- |
| i | Open a video by booru id from PATH defined in 'config.ini'. (This will load the whole video as array.)  |
| I | Open a video file with filedialog. (This won't load the video as array) |
| space | play / pause ; enter (input mode) |
| j | pause and goto prev frame |
| k | pause and goto next frame |
| f | switch fps between 1x/0.5x/0.25x |
| c | switch canny between off/on/hybrid |
| m | switch komas between 2/3/1 |
| o | switch onion layers off/1/2/3 |
| g | switch grid |
| l/r | set start/end point(left/right bound). used to loop or clip. |
| s | pause, save current frame and goto next frame, hold to save sequentially.(booru video opened) ; save clipped mp4 by inputting id.(video file opened) |


### FUTURE WORK
- Simple drawing
- Another renderer for comparison
- A timeline with timesheet editing