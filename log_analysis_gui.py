# Basic python script for making terminal input-output into a tkinter GUI application
# You can use this program to run CLI python programs

import tkinter as tk
import threading

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
    log.insert(tk.END, text)
    log.insert(tk.END,'\n')
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
    for d in range(1, int(df['Duration Count'].max()) + 1):
        df[f'Duration {d}'] = pd.to_timedelta(df[f'Duration {d}'])
        if d < int(df['Duration Count'].max()):
            df[f'Paused {d}'] = pd.to_timedelta(df[f'Paused {d}'])
    return df

def info_data_for_title():
    # Prompt for CSV file
    in_file = Prompt(f"Enter file path/name for CSV to analyze, or leave empty to use default: {csv_main_path}\nPath: ")
    if len(in_file) < 1:
        in_file = csv_main_path
    df = get_log_df(in_file)
    if df is None:
        WriteText("Could not load data.")
        return

    # Check if 'Title' column exists
    if 'Title' not in df.columns:
        WriteText("No 'Title' column found in the data.")
        return

    # Get unique titles
    unique_titles = df['Title'].dropna().unique()
    if len(unique_titles) == 0:
        WriteText("No titles found in the data.")
        return

    # List titles
    title_list = "\n".join([f"{i+1}: {title}" for i, title in enumerate(unique_titles)])
    WriteText(f"Available Titles:\n{title_list}")

    # Ask user to select a title
    while True:
        selection = Prompt("Enter the number of the title you want to analyze: ")
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(unique_titles):
                selected_title = unique_titles[idx]
                break
            else:
                WriteText("Invalid selection. Please enter a valid number.")
        except ValueError:
            WriteText("Please enter a number.")

    # Filter data for selected title
    title_df = df[df['Title'] == selected_title].copy()
    if title_df.empty:
        WriteText(f"No data found for title: {selected_title}")
        return

    # Check if 'Info' column exists
    if 'Info' not in title_df.columns:
        WriteText("No 'Info' column found for the selected title.")
        return

    # Ask for pattern
    pattern = Prompt(f"Enter a pattern for extracting the numeric value from 'Info' (e.g., '$<n>/hr' where <n> is the number). Leave empty to extract digits: ")

    def extract_numeric(info_str):
        if not info_str:
            return None
        if '<n>' in pattern:
            prefix, suffix = pattern.split('<n>')
            stripped = str(info_str).replace(prefix, '')
            stripped = stripped.replace(suffix, '')
            regex_pattern = r'(\d+\.?\d*)'
            match = re.search(regex_pattern, stripped)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        # Fallback: extract digits
        WriteText(f"Fallback: pattern not found in {info_str}, extracting first number instead.")
        digits = re.findall(r'\d+\.?\d*', str(info_str))
        if digits:
            try:
                return float(digits[0])
            except ValueError:
                pass
        return None

    # Apply extraction
    title_df['info_numeric'] = title_df['Info'].apply(extract_numeric)

    # Drop rows where extraction failed
    title_df = title_df.dropna(subset=['info_numeric', 'Elapsed Time', 'Date'])
    if title_df.empty:
        WriteText("Could not extract numeric values from 'Info' for the selected title.")
        return

    # Convert Elapsed Time to hours
    title_df['elapsed_hours'] = title_df['Elapsed Time'].apply(lambda x: x.total_seconds() / 3600)

    # Compute weighted value (e.g., info_numeric * elapsed_hours)
    title_df['weighted_value'] = title_df['info_numeric'] * title_df['elapsed_hours']

    # Compute statistics
    WriteText(f"Statistics for Title: {selected_title}")

    # Total weighted value
    total_weighted = title_df['weighted_value'].sum()
    WriteText(f"Total Weighted Value: {total_weighted:.2f}")

    # Average info_numeric
    avg_info = title_df['info_numeric'].mean()
    WriteText(f"Average Info Numeric: {avg_info:.2f}")

    # Day with highest weighted value
    if 'Date' in title_df.columns:
        date_group = title_df.groupby('Date')['weighted_value'].sum().sort_values(ascending=False)
        if not date_group.empty:
            top_date = date_group.index[0]
            top_value = date_group.iloc[0]
            WriteText(f"Date with Highest Weighted Value: {top_date} ({top_value:.2f})")

    # Average weighted value per session
    avg_weighted = title_df['weighted_value'].mean()
    WriteText(f"Average Weighted Value per Session: {avg_weighted:.2f}")

    # Number of sessions
    session_count = len(title_df)
    WriteText(f"Number of Sessions: {session_count}")

    # If there are multiple unique info_numeric, show distribution
    unique_info = title_df['info_numeric'].value_counts()
    if len(unique_info) > 1:
        WriteText("Info Numeric Distribution (Top 10):")
        WriteText(unique_info.sort_values(ascending=False).head(10))


################################################################
# Program definition here
def program():
    looping = True
    while looping:
        choice = Prompt("Select an option to continue:\n1: Convert text log to CSV data\n2: Fix/Restructure CSV log\n3: View Statistics\n4: Info statistics for Title\n5: Quit\n(Other functionalities to be added soon)\n\nOption: ")
        try:
            choice = int(choice)
        except:
            WriteText('Invalid input.')
            continue
        if choice not in range(1,5):
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
            in_file = Prompt(f"Enter file path/name for CSV to analyze, or leave empty to use default: {csv_main_path}\nPath: ")
            if len(in_file) < 1:
                in_file = csv_main_path
            df = get_log_df(in_file)
            df.dropna(inplace=True, how='all')
            if df is not None:
                WriteText("Statistics for Time Log:")
                # Total time
                total_time = df['Elapsed Time'].sum()
                WriteText(f"Total Time Logged: {total_time}")

                # Date with most time
                date_group = df.groupby('Date')['Elapsed Time'].sum().sort_values(ascending=False)
                if not date_group.empty:
                    top_date = date_group.index[0]
                    top_date_time = date_group.iloc[0]
                    WriteText(f"Date with Most Time: {top_date} ({top_date_time})")

                # Subtitle with most time (if Subtitle column exists)
                if 'Subtitle' in df.columns:
                    subtitle_group = df.groupby('Subtitle')['Elapsed Time'].sum().sort_values(ascending=False)
                    if not subtitle_group.empty:
                        top_subtitle = subtitle_group.index[0]
                        top_subtitle_time = subtitle_group.iloc[0]
                        WriteText(f"Subtitle with Most Time: {top_subtitle} ({top_subtitle_time})")

                # Title with most time (if Title column exists)
                if 'Title' in df.columns:
                    title_group = df.groupby('Title')['Elapsed Time'].sum().sort_values(ascending=False)
                    if not title_group.empty:
                        top_title = title_group.index[0]
                        top_title_time = title_group.iloc[0]
                        WriteText(f"Title with Most Time: {top_title} ({top_title_time})")

                # Average time per session
                avg_time = df['Elapsed Time'].mean()
                WriteText(f"Average Time per Session: {avg_time}")

                # Number of sessions
                session_count = len(df)
                WriteText(f"Total Number of Sessions: {session_count}")

                # Time range
                if 'Start Time' in df.columns and 'End Time' in df.columns:
                    earliest = df['Start Time'].min()
                    latest = df['End Time'].max()
                    WriteText(f"Time Range: {earliest} to {latest}")
            else:
                WriteText("Could not load data for statistics.")
        elif choice < 5:
            confirmation = Prompt("This tool calculates statistics for data with a specific 'Title' under the assumption that all data in the 'Info' row for this title has a numeric value that multiplies with elapsed time.\nFor example: all records with title 'Work' have 'Info' as '$18/hr' or '$22/hr'. This tool will then multiply each record's elapsed time by its number, in this case 18 or 22, to calculate statistical data.\n\nIf you have records with a certain 'Title' that have numeric data as 'Info' and wish to see statistics, confirm with 'y' or enter  anything else to return.")
            if confirmation[0] == 'y':
                info_data_for_title()
        elif choice <  6:
            looping = False

    on_closing()

########################################################################


# Create thread for main program as daemon to stop when main thread exits
pthread = threading.Thread(target=program, daemon=True)
pthread.start()


# Coerce the running thread into a terminatable state before closing the window
def on_closing():
    # In case the thread is waiting for input, update input
    InputText()
    window.destroy()

frame.pack()
window.protocol("WM_DELETE_WINDOW", on_closing) # Run on_closing when the window is closed
window.geometry("300x300")
window.mainloop()





