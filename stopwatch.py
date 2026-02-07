# stopwatch.py
import tkinter as tk
import datetime
import os
import sys
import pandas as pd
import numpy as np
import pyaudio

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True)

def play_beep(sfx=None, frequency=1000, duration=0.05, volume=0.2):
    global stream
    # Check if there's an MP3 file for this frequency in the sfx directory
    if sfx:
        sfx_file = f"sfx/{sfx}.mp3"
        if os.path.exists(sfx_file):
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(sfx_file)
                pygame.mixer.music.play()
                return
            except Exception as e:
                print(f"Error playing sound effect: {e}")
                # Fall back to beep if there's an error

    # Generate samples
    t = np.linspace(0, duration, int(48000 * duration), False)
    wave = (np.sin(2 * np.pi * frequency * t) * volume).astype(np.float32)

    stream.write(wave.tobytes())
# Notes for improvement:
#
# Duration is calculated every update, adding all start-stop durations.
# This could be changed to only calculate running time and store already complete
# durations so they aren't recalculated constantly.
#
# - Add some sort of way to manipulate timestamps while stopwatch is running, or
# implement some extra logged information for proper manipulation and
# recalculation afterwards. This should address the problem of forgetting to
# pause or resume the timer, maybe by letting the user type in a time to add or
# subtract from the total and including this amount(s) as a separate variable

# Window and frame creation
window = tk.Tk()
window.title("Stopwatch")
if os.path.exists('icon.png'):
    icon = tk.PhotoImage(file ='icon.png')
    window.iconphoto(False, icon)

# Get command-line arguments
# Currently only one is debug level
# No checking or parsing done currently, just basic debug use
# Parse command-line arguments with default values
args = {"debug_level": 0, "log_path_txt": 'timelog.txt', "log_path_csv": 'time_log.csv', "analysis_script": 'log_analysis_gui.py'}  # Default debug level is 0
for arg in sys.argv[1:]:
    if arg.find('=') != -1:
        arg_name, arg_value = arg.split('=')
        try:
            arg_value = type(args[arg_name])(arg_value)
            args[arg_name] = arg_value
        except:
            print(f"Error: Argument {arg_name} value of {arg_value} is not of type {type(args[arg_name])}. Keeping default value of {args[arg_name]}.")
    else:
        print(f"Error: Argument {arg} is not in the format 'arg=value'. Ignoring argument.")
from tkinter import font
default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=8)  # make text smaller
window.option_add("*Font", default_font)
window.option_add("*Button.padX", 4)
window.option_add("*Button.padY", 2)
# Level of debug info printed during runtime. Higher levels also print lower levels
# 0 = no debug info
# 1 = basic info
# 2 = discrete info (responses to buttons, single events, etc)
# 3 = continuous info (constant info from repeated events like timer updating)
# 4 = exterminator mode (currently unused)
DEBUG_LEVEL = args["debug_level"]
log_path_txt = args["log_path_txt"]
log_path_csv = args["log_path_csv"]
analysis_script = args["analysis_script"]


timerPauses = []
timeractive = False
timertext = tk.StringVar(window, "00h00m00.0s")
timestart_text = tk.StringVar(window, "Click [Start/Stop] to start timer.")
flagtime = None
timeflag_text = tk.StringVar(window, "Click [Toggle Flag] to set\na temporary timestamp")


# Recursively change background color of widget and its children
def ChangeBGColor(widget, color):
    if not isinstance(widget, tk.Button):
        try:
            widget.configure(bg=color)
        except:
            pass
    for child in widget.winfo_children():
        ChangeBGColor(child, color)
# Set timeractive = false and timerpauses to empty
def ResetTimer():
    global DEBUG_LEVEL
    global window
    if DEBUG_LEVEL >= 2:
        print("Resetting Timer")
    global timeractive
    global timerPauses
    if timeractive:
        ToggleTimer()
    global flagtime
    if flagtime is not None:
        ToggleFlag()
    timerPauses = []
    timestart_text.set("Click [Start/Stop] to start timer.")
    ChangeBGColor(window, "#bad1ff")
    UpdateTimer()
    play_beep(sfx='reset', frequency=200)

# Update a backup file for the log when writing. 'filepath' is for non-backup
def UpdateBackup(filepath):
    if not os.path.isfile(filepath):
        print(f"Skipping backup - no file at {filepath} to backup.")
        return
    import shutil
    path_split = filepath.rsplit('.', 1)
    new_path = path_split[0] + '_backup.' + path_split[1]
    if DEBUG_LEVEL >= 1:
        print(f"Backing up {filepath} to {new_path}.")
    shutil.copyfile(filepath, new_path)


# Write time to text file. No longer used since CSV implementation.
def LogTime():
    global timeractive
    global timerPauses
    if len(timerPauses) < 1:
        return
    if timeractive:
        ToggleTimer()
    UpdateBackup(log_path_txt)
    save_file = open(log_path_txt, "a")
    totaltime = GetElapsedTime()
    # Write date, start and end time, and total duration.
    output = f"\n{str(datetime.datetime.now().date())}\t\tElapsed Time: {str(totaltime)}\nStart Time: {str(timerPauses[0])}\t\tEnd Time: {str(timerPauses[-1])}\n"
    durcount = len(timerPauses) // 2
    output += f"Durations: {durcount}\n"
    for d in range(durcount):
        duration = timerPauses[(d*2)+1] - timerPauses[d*2]
        output += f"Duration {d+1}:\t\t{str(duration)}\n"
        if d < durcount-1:
            pausedur = timerPauses[(d+1)*2] - timerPauses[(d*2)+1]
            output += f"Paused for {str(pausedur)}\n"
    output += "\n"
    save_file.write(output)
    if DEBUG_LEVEL >= 1:
        print(f"Time written to {log_path_txt}")
    # Change to green to indicate success
    ChangeBGColor(window, "#d2ffde")
    play_beep(sfx='log', frequency=1000)

# New function for logging the time to a csv instead of a text file.
def LogTimeCSV():
    global timeractive
    global timerPauses
    if len(timerPauses) < 1:
        return
    if timeractive:
        ToggleTimer()
    df = GetCSVData()
    if DEBUG_LEVEL > 1:
        print(f"Time log with {df.shape[0]} rows read into DataFrame.\n")
    totaltime = GetElapsedTime()
    output = {'Date': datetime.datetime.now().date(),'Title': name_text.get(), 'Subtitle': subtitle_text.get(), 'Info': info_text.get(), 'Elapsed Time': totaltime, 'Start Time': timerPauses[0], 'End Time': timerPauses[-1]}
    durcount = len(timerPauses) // 2
    output['Duration Count'] =  durcount
    for d in range(durcount):
        duration = timerPauses[(d*2)+1] - timerPauses[d*2]
        output[f"Duration {d+1}"] = duration
        if d < durcount-1:
            pausedur = timerPauses[(d+1)*2] - timerPauses[(d*2)+1]
            output[f"Paused {d+1}"]= pausedur
    new_data = pd.DataFrame(output, index=[0])
    if DEBUG_LEVEL > 1:
        print(f"New row for time record created:\n{new_data}\nAdding to log...")
    df = pd.concat([df, new_data])
    df.to_csv(log_path_csv, index=False)
    if DEBUG_LEVEL >= 1:
        print(f"Time written to {log_path_csv}")
    # Change to green to indicate success
    ChangeBGColor(window, "#d2ffde")
    play_beep(sfx='log', frequency=1200)

def GetCSVData():
    df = None
    # Check if CSV log already exists, and load it. If not, start with empty DF
    if os.path.isfile(log_path_csv):
        UpdateBackup(log_path_csv)
        df = pd.read_csv(log_path_csv)
    else:
        if DEBUG_LEVEL > 1:
            print(f"No file found at {log_path_csv}. Creating empty DataFrame.")
        df = pd.DataFrame()
    return df

def ToggleTimer():
    global DEBUG_LEVEL
    global timeractive
    global timerPauses
    global timestart_text
    global window
    timerPauses.append(datetime.datetime.now())
    timestart_text.set("Started at " + timerPauses[0].strftime("%Y-%m-%d %H:%M:%S"))
    if DEBUG_LEVEL >= 2:
        print(f"Timer {'stopped' if timeractive else 'started'} At: ", timerPauses[-1])
    timeractive = not timeractive
    # Add media toggle when timer state changes
    toggle_media_playback()
    ChangeBGColor(window, "#ffd1d8" if timeractive else "#e1fbff")
    if timeractive:
        play_beep(sfx='start', frequency=600)
        UpdateTimer()
    else:
        play_beep(sfx='pause', frequency=300)

# Uses global list of timer toggles and returns sum of durations (plus runtime if active)
def GetElapsedTime():
    global DEBUG_LEVEL
    global timerPauses
    global timeractive
    # time_0 removed in favor of using only timerPauses as start-stop pairs.
    # Sum durations between pairs in timerPauses. If odd size (timer active), use
    # current time for final duration.
    if DEBUG_LEVEL >= 3:
        print("Calculating elapsed time")
    timesum = datetime.timedelta(0)
    for i in range(len(timerPauses)//2): # For every start-stop pair
        # Calculate duration (difference between stop - start)
        duration = timerPauses[(i*2)+1] - timerPauses[i*2]
        if DEBUG_LEVEL >= 3:
            print("Duration ", i, ": ", duration)
        timesum += duration
    # Add final running duration if timer active (and odd sized timerPauses)
    if timeractive or (len(timerPauses) % 2 == 1):# both should be true or false, but JiC
        duration = datetime.datetime.now() - timerPauses[-1]
        if DEBUG_LEVEL >= 3:
            print("Running duration: ", duration)
        timesum += duration
    # Return total duration
    if DEBUG_LEVEL >= 3:
        print("Calculated elapsed time is: ", timesum)
    return timesum


def UpdateTimer():
    global DEBUG_LEVEL
    if DEBUG_LEVEL >= 3:
        print("Updating Timer")
    global timeractive
    global timertext
    global timeflag_text
    global flagtime

    time = GetElapsedTime()
    s = time.total_seconds()
    timertext.set('{:02}h{:02}m{:04.1F}s'.format(int(s // 3600), int(s % 3600 // 60), s % 60))
    # If time flag set, calc and update time
    if flagtime is not None:
        e = (time - flagtime).total_seconds()
        f = flagtime.total_seconds()
        timeflag_text.set(f"Flag Time: " + '{:02}h{:02}m{:04.1F}s'.format(int(f // 3600), int(f % 3600 // 60), f % 60) + "\nDuration: " + '{:02}h{:02}m{:04.1F}s'.format(int(e // 3600), int(e % 3600 // 60), e % 60))
    if timeractive:
        window.after(100, UpdateTimer)

def OpenLog():
    import subprocess, os, platform
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', log_path_csv))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(log_path_csv)
    else:                                   # linux variants
        subprocess.call(('xdg-open', log_path_csv))

def OpenAnalysis():
    import subprocess
    subprocess.run(['python3', analysis_script])

def ToggleFlag():
    global flagtime
    global timeflag_text
    UpdateTimer()
    if flagtime is None and len(timerPauses) > 0:
        flagtime = GetElapsedTime()
    else:
        flagtime = None
        timeflag_text.set("No Time Flag Set\nClick [Toggle Flag] to set.")
    UpdateTimer()


def toggle_media_playback():
    if not media_control_enabled.get():
        return
    try:
        # Use pynput to simulate media key press
        from pynput.keyboard import Key, Controller
        keyboard = Controller()
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)

    except Exception as e:
        if DEBUG_LEVEL >= 1:
            print(f"Media toggle failed: {e}")
confirm_open = False
def OnClose():
    global confirm_open, timerPauses, stream, p
    stream.stop_stream()
    stream.close()
    p.terminate()
    if not confirm_open:
        # Ask for confirmation with options to log time or not
        if len(timerPauses) > 0:
            from tkinter import messagebox
            confirm_open = True
            response = messagebox.askyesnocancel("Confirm Exit", 
                                            "Do you want to save your time log before exiting?",
                                            icon='warning')
            confirm_open = False
            if response is None:  # Cancel was clicked
                return
            elif response:  # Yes was clicked
                LogTimeCSV()
        window.destroy()

# Set the window's close protocol to use OnClose
window.protocol("WM_DELETE_WINDOW", OnClose)

# Timer
timerframe = tk.Frame(window)
timerlbl = tk.Label(timerframe, textvariable=timertext, font=('Courier 20'), padx=5, pady=5)
timerlbl.pack()
timerframe.pack()

# User interface
ux = tk.Frame(window)
name_text = tk.StringVar(window, "Untitled Stopwatch")
subtitle_text = tk.StringVar(window, "Unconfigured")
info_text = tk.StringVar(window, "No Info")
# Add media control checkbox
media_control_enabled = tk.BooleanVar(window, False)
media_checkbox = tk.Checkbutton(ux, text="Pause toggles media", 
                              variable=media_control_enabled)
media_checkbox.pack()

from tkinter import ttk
name_select = ttk.Combobox(ux, textvariable = name_text)
names = GetCSVData().get('Title', pd.Series()).unique().tolist()
name_select['values'] = names
name_select.pack()
sub_select = ttk.Combobox(ux, textvariable = subtitle_text)
subs = GetCSVData().get('Subtitle', pd.Series()).unique().tolist()
sub_select['values'] = subs
sub_select.pack()

info_input = tk.Entry(ux, textvariable = info_text)
info_input.pack()

# Flag label and button
flaglbl = tk.Label(ux, textvariable=timeflag_text)
flaglbl.pack()
startlbl = tk.Label(ux, textvariable=timestart_text)
startlbl.pack()
flagButton = tk.Button(ux, command=ToggleFlag, text="Toggle Flag")
flagButton.pack()

# Button frame
btnframe = tk.Frame(ux)
timeButton = tk.Button(btnframe, command=ToggleTimer, text="Start/Stop", bg="#aeffa3", activebackground="#bdffea")
timeButton.grid(row=0, column=0, sticky="nesw")
resetButton = tk.Button(btnframe, command=ResetTimer, text="Reset", bg="#fc7777", activebackground="#fa9d9d")
resetButton.grid(row=0, column=1, sticky="nesw")
logButton = tk.Button(btnframe, command=LogTimeCSV, text="Log Time")
logButton.grid(row=1, column=0, sticky="nesw")
openLogButton = tk.Button(btnframe, command=OpenLog, text="Open Log")
openLogButton.grid(row=1, column=1, sticky="nesw")
btnframe.pack()

# Analysis button
analysisButton = tk.Button(ux, command=OpenAnalysis, text="Open Log Analysis Tool", bg="#c296ff")
analysisButton.pack()
ux.pack()

ChangeBGColor(window, "#bad1ff")
window.mainloop()
