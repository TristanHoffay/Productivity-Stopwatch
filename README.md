Basic stopwatch tool written in Python

Requires pandas, numpy, and pyaudio (and also pygame if you want sfx audio files to play)
Uses tkinter for GUI

Run with python `python stopwatch.py`
Use `runstopwatch.sh` or modify/create your own script to run it with preferred arguments.
I use the BASH file for an executable widget in my task bar, making the timer easily accessible.

CLI arguments:
Arguments are read as 'argname=value' format. Order does not matter. Ex: `python stopwatch.py debug_level=1 log_path_csv=mylog.csv`
Args and their default values:
  debug_level: 0
      Higher value means more verbose debug logging in console. 0 for none (default), 1 for less frequent one-shot events (e.g., saving log), 2 for more frequent one-shot events (toggling timer), 3 for constant/looping events (updating elapsed time). Higher (more verbose) values will also print debug information for lower tiers.
  log_path_txt: timelog.txt
      Not used, since txt logging is no longer used. You can specify it if you want, or even re-add usage of the text logging function, but CSV logging is better and the supported alternative now.
  log_path_csv: time_log.csv
      Sets the output file written to for logging stopwatch data. 
  analysis_script: log_analysis_gui.py
      The Python script executed when pressing the "Open Log Analysis Tool" button in the GUI. Useful if you create your own or have multiple analysis scripts that you wish to specify instead of the default.

Sound Effects:
You can add your own sound effects (or remove them for a default tone generated with pyaudio). Sound effects require pygame installed.
Sound effects are played from audio files in the 'sfx' directory. You can change them to be whatever you want, but they must be mp3 files with the defined names. The names are:
  start.mp3  -  plays when starting/resuming the timer
  reset.mp3  -  plays when resetting the timer
  pause.mp3  -  plays when pausing the timer
  log.mp3    -  plays when logging the time
