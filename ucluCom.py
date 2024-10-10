#Dexcom 1 Raw Data: {'_json': {'WT': 'Date(1727476816000)', 'ST': 'Date(1727476816000)', 'DT': 'Date(1727476816000+0200)', 'Value': 194, 'Trend': 'Flat'}, '_value': 194, '_trend_direction': 'Flat', '_trend': 4, '_datetime': datetime.datetime(2024, 9, 28, 0, 40, 16)}
#Dexcom 2 Raw Data: {'_json': {'WT': 'Date(1727477022000)', 'ST': 'Date(1727477022000)', 'DT': 'Date(1727477022000+0200)', 'Value': 111, 'Trend': 'Flat'}, '_value': 111, '_trend_direction': 'Flat', '_trend': 4, '_datetime': datetime.datetime(2024, 9, 28, 0, 43, 42)}

import os
import time
from pathlib import Path
from pydexcom import Dexcom

# Setup Dexcom authentication for two different accounts or devices
dexcom1 = Dexcom(username="your_email_or_phone_1", password="your_password_1", ous=True)
dexcom2 = Dexcom(username="your_email_or_phone_2", password="your_password_2", ous=True)
dexcom3 = Dexcom(username="your_email_or_phone_3", password="your_password_3", ous=True)

# Path to the file where BG info will be written
bg_file = Path.home() / "bg_info.txt"  # Using /tmp for temporary files

# Trend direction mapping from text to symbols
TREND_SYMBOLS = {
    "Flat": "→",
    "FortyFiveUp": "↗",
    "SingleUp": "↑",
    "DoubleUp": "↑↑",
    "FortyFiveDown": "↘",
    "SingleDown": "↓",
    "DoubleDown": "↓↓",
    "None": "—"
}

# Function to update the BG info file
def update_bg_info(glucose_value, trend_arrow, timestamp):
    # Determine the color based on glucose levels
    if glucose_value >= 240:
        color_code = "\033[93m"  # Yellow
    elif glucose_value < 90:
        color_code = "\033[91m"  # Red
    elif 160 <= glucose_value < 240:
        color_code = "\033[93m"  # Yellow
    else:
        color_code = "\033[92m"  # Green

    # Format the BG info to be displayed in the prompt
    trend_symbol = TREND_SYMBOLS.get(trend_arrow, "—")  # Convert trend to symbol
    bg_info = f"{color_code}{glucose_value} mg/dL {trend_symbol} at {timestamp}\033[0m"

    # Write the formatted BG info to the file
    with open(bg_file, 'w') as file:
        file.write(bg_info)

    # Also print the info to the command line
    print(f"Updated BG Info: {bg_info}")

# Main function to check glucose levels from three sources and print them separately
def check_glucose():
    while True:
        try:
            # Get the current blood glucose reading and trend from all three Dexcom accounts
            glucose_reading_1 = dexcom1.get_current_glucose_reading()
            glucose_reading_2 = dexcom2.get_current_glucose_reading()
            glucose_reading_3 = dexcom3.get_current_glucose_reading()

            # Collect valid glucose values and their respective timestamps and trend arrows
            glucose_values = []
            trend_arrows = []
            timestamps = []

            if glucose_reading_1 is not None:
                glucose_values.append(glucose_reading_1.value)
                trend_arrows.append(glucose_reading_1.trend_direction)
                timestamps.append(glucose_reading_1._datetime)
                print(f"\nDexcom 1: {glucose_reading_1.value} mg/dL {TREND_SYMBOLS.get(glucose_reading_1.trend_direction, '—')} at {glucose_reading_1._datetime}")
            else:
                print("Dexcom 1: No data available")

            if glucose_reading_2 is not None:
                glucose_values.append(glucose_reading_2.value)
                trend_arrows.append(glucose_reading_2.trend_direction)
                timestamps.append(glucose_reading_2._datetime)
                print(f"Dexcom 2: {glucose_reading_2.value} mg/dL {TREND_SYMBOLS.get(glucose_reading_2.trend_direction, '—')} at {glucose_reading_2._datetime}")
            else:
                print("Dexcom 2: No data available")

            if glucose_reading_3 is not None:
                glucose_values.append(glucose_reading_3.value)
                trend_arrows.append(glucose_reading_3.trend_direction)
                timestamps.append(glucose_reading_3._datetime)
                print(f"Dexcom 3: {glucose_reading_3.value} mg/dL {TREND_SYMBOLS.get(glucose_reading_3.trend_direction, '—')} at {glucose_reading_3._datetime}")
            else:
                print("Dexcom 3: No data available")

            # If all sources have valid data, calculate the average and update the file
            if len(glucose_values) == 3:
                average_glucose = sum(glucose_values) // 3
                trend_arrow = trend_arrows[0]  # Use the trend from the first device (you can adjust this logic)
                timestamp = timestamps[0]  # Use the timestamp from the first device
                update_bg_info(average_glucose, trend_arrow, timestamp)

            # If only one or two sources have valid data, use the available ones
            elif len(glucose_values) > 0:
                average_glucose = sum(glucose_values) // len(glucose_values)
                trend_arrow = trend_arrows[0]  # Use the trend from the first available device
                timestamp = timestamps[0]  # Use the timestamp from the first available device
                update_bg_info(average_glucose, trend_arrow, timestamp)
            else:
                print("No valid data from any source.")

            # Wait for 5 minutes (300 seconds) before checking again
            time.sleep(300)

        except Exception as e:
            print(f"Error fetching glucose data: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying if an error occurs

if __name__ == "__main__":
    check_glucose()
