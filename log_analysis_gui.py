# Basic python script for making terminal input-output into a tkinter GUI application
# You can use this program to run CLI python programs

import tkinter as tk
from threading import *

window = tk.Tk()
window.title("Tkinter CLI")
window.configure(bg="#33006e")
frame = tk.Frame(window, bg="#33006e", padx=0, pady=0)

# Vars
newinput = tk.BooleanVar()
input_content = tk.StringVar()
# For reusing previous inputs
old_inputs = []
old_input_index = 0




def LastInput(event):
    global old_input_index
    global old_inputs
    if old_input_index > 0:
        old_input_index -= 1
        input_content.set(old_inputs[old_input_index])


def NextInput(event):
    global old_input_index
    global old_inputs
    if old_input_index < len(old_inputs)-1:
        old_input_index += 1
        input_content.set(old_inputs[old_input_index])
    else:
        input_content.set("")


# Function for entering input
def InputText(event=None):
    global old_input_index
    global old_inputs
    message = input_content.get()
    WriteText(message)
    input_content.set("")
    old_inputs.append(message)
    old_input_index = len(old_inputs)
    newinput.set(True)

# Function for writing text to the console
def WriteText(text):
    log.configure(state='normal')
    log.insert(tk.END, text + '\n')
    log.see("end")
    log.configure(state='disabled')

# Function for getting text
def Prompt(text):
    WriteText(text)
    window.wait_variable(newinput)
    newinput.set(False)
    return old_inputs[old_input_index-1]



# Scroll bar for log
# Label housing previous output and input
log = tk.Text(frame, height=13.5, bg="#000512", fg="#b5edf5", state='disabled', bd=0, padx=0, pady=0, highlightthickness=0)
log.pack()

# Text input and send button
inputframe = tk.Frame(frame, bg="#33006e")
userinput = tk.Entry(inputframe, textvariable=input_content, width=30)
userinput.grid(row=0,column=0)
submit_btn = tk.Button(inputframe, command=InputText, text="Enter", width=3)
submit_btn.grid(row=0,column=1)
inputframe.pack()

window.bind('<Return>', InputText)
window.bind('<Up>', LastInput)
window.bind('<Down>', NextInput)

##########################################################################
import pandas as pd
import re
import os

txt_log_path = 'timelog.txt'
csv_log_path = 'time_log_from_txt.csv'
csv_main_path = 'time_log.csv'

def get_log_df(csv_path=csv_log_path):
    if os.path.isfile(csv_path):
        df = pd.read_csv(csv_path)
        return convert_objects(df)
    else:
        WriteText(f"No file found at {csv_path}.")
        return None

def convert_textlog(text_path=txt_log_path, csv_path=csv_log_path):
    record_regex = r'(\d{4}-\d{2}-\d{2})\s*Elapsed Time: (\d+:\d{2}:\d{2}\.\d+)\s?\nStart Time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s*End Time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s?\nDurations: (\d+)\n((?:.+\n)+)\n'
    duration_regex = r'Duration \d+:\s*(\d+:\d{2}:\d{2}\.\d+)\n'
    pause_regex = r'Paused for (\d+:\d{2}:\d{2}\.\d+)\n'
    # Open text file
    try:
        text_file = open(text_path, "r")
    except:
        WriteText(f"No file found at {text_path}.")
        return

    # Parse text for data
    text = text_file.read()
    records = re.findall(record_regex, text)
    df = pd.DataFrame()
    for record in records:
        data = {}
        data['Date'] = record[0]
        WriteText(f"Parsing record for date {record[0]}")
        data['Elapsed Time'] = record[1]
        data['Start Time'] = record[2]
        data['End Time'] = record[3]
        data['Duration Count'] = record[4]
        for dur_i in range(1, int(record[4]) + 1):
            data[f'Duration {dur_i}'] = re.findall(duration_regex, record[5])[dur_i-1]
            if dur_i < int(record[4]):
                data[f'Paused {dur_i}'] = re.findall(pause_regex, record[5])[dur_i-1]
        WriteText(f"Adding record for date {record[0]}.")
        new_record = pd.DataFrame(data, index=[0])
        df = pd.concat([df, new_record])
    WriteText(f"Text log successfully parsed for data.")
    WriteText(f"Resulting data:\n{df}")
    old_df = get_log_df(csv_path)
    # Check if csv file already exists and ask how to resolve
    if old_df is not None:
        resolved = False
        while not resolved:
            resolve = Prompt(f"Caution: There is already a file at {csv_path}. How would you like to proceed? Enter a number corresponding to an option:\n1: Append\n2: Overwrite\n3: Specify new path\n4: Peak file contents\n5: Abort\n\nOption: ")
            try:
                resolve = int(resolve)
            except:
                WriteText("Please enter the number corresponding to an option.")
                continue
            if resolve not in range(1,6):
                WriteText("Please enter the number corresponding to an option.")
            elif resolve > 4:
                WriteText("Cancelling operation to convert text log to CSV.")
                return
            elif resolve > 3:
                WriteText(old_df.head())
            elif resolve > 2:
                csv_path = Prompt("Specify a new path or file name for the CSV log: ")
                old_df = get_log_df(csv_path)
                resolved = old_df is None
                WriteText(old_df)
            else:
                resolved = True
                if resolve < 2:
                    WriteText(f"Concatenating new data to old data.")
                    df = pd.concat([old_df, df])
    # Save DataFrame to csv path
    df.to_csv(csv_path, index=False)
    WriteText(f"Data logged to {csv_path}.")

# Takes in a DataFrame of a log and returns it with columns converted to numeric and datetime
def convert_objects(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Elapsed Time'] = pd.to_timedelta(df['Elapsed Time'])
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])
    for d in range(1, df['Duration Count'].max() + 1):
        df[f'Duration {d}'] = pd.to_timedelta(df[f'Duration {d}'])
        if d < df['Duration Count'].max():
            df[f'Paused {d}'] = pd.to_timedelta(df[f'Paused {d}'])
    return df




################################################################
# Program definition here
def program():
    looping = True
    while looping:
        choice = Prompt("Select an option to continue:\n1: Convert text log to CSV data\n2: Fix/Restructure CSV log\n3: Quit\n(Other functionalities to be added soon)\n\nOption: ")
        try:
            choice = int(choice)
        except:
            WriteText('Invalid input.')
            continue
        if choice not in range(1,4):
            WriteText('Enter a number corresponding to one of the listed options.')
            continue
        if choice < 2:
            in_file = Prompt(f"Enter file path/name for text log, or leave empty to use default: {txt_log_path}\nPath: ")
            out_file = Prompt(f"Enter file path/name to write the CSV log to, or leave empty to use default: {csv_log_path}\nPath: ")
            if len(in_file) < 1:
                in_file = txt_log_path
            if len(out_file) < 1:
                out_file = csv_log_path
            convert_textlog(in_file, out_file)
        elif choice < 3:
            in_file = Prompt(f"Enter file path/name for CSV to correct, or leave empty to use default: {csv_main_path}\nPath: ")
            out_file = Prompt(f"Enter file path/name to write the corrected CSV log to, or leave empty to use default: {csv_main_path}\nPath: ")
            if len(in_file) < 1:
                in_file = csv_main_path
            if len(out_file) < 1:
                out_file = csv_main_path
            df = get_log_df(in_file)
            cols = df.columns
            length = df.shape[0]
            df_out = pd.DataFrame()
            ordered_cols = ['Date', 'Title', 'Subtitle', 'Info']
            for column in ordered_cols:
                if column in cols:
                    df_out[column] = df[column]
                else:
                    df_out[column] = ''
            unordered_cols = [column for column in cols if column not in ordered_cols]
            for column in unordered_cols:
                df_out[column] = df[column]
            df_out.to_csv(out_file, index=False)
        elif choice < 4:
            looping = False

########################################################################


# Create thread for main program
pthread = Thread(target=program)
pthread.start()


frame.pack()
window.geometry("300x300")
window.mainloop()





