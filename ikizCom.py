import os
import time
from pydexcom import Dexcom

# Setup Dexcom authentication for two different accounts or devices
dexcom1 = Dexcom(username="your_email_or_phone_1", password="your_password_1", ous=True)
dexcom2 = Dexcom(username="your_email_or_phone_2", password="your_password_2", ous=True)

# Path to the file where BG info will be written
bg_file = "/tmp/bg_info.txt"  # Using /tmp for temporary files

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
    bg_info = f"{color_code}{glucose_value} mg/dL {trend_arrow} at {timestamp}\033[0m"

    # Write the formatted BG info to the file
    with open(bg_file, 'w') as file:
        file.write(bg_info)

    # Also print the info to the command line
    print(f"Updated BG Info: {bg_info}")

# Main function to check glucose levels from two sources and print them separately
def check_glucose():
    while True:
        try:
            # Get the current blood glucose reading and trend from both Dexcom accounts
            glucose_reading_1 = dexcom1.get_current_glucose_reading()
            glucose_reading_2 = dexcom2.get_current_glucose_reading()

            # Print the glucose values from both sources, if available
            if glucose_reading_1 is not None:
                glucose_value_1 = glucose_reading_1.value
                trend_arrow_1 = glucose_reading_1.trend_direction  # 'Flat' or '↑' etc.
                timestamp_1 = glucose_reading_1._datetime  # Glukoz ölçüm zamanı
                print(f"Dexcom 1: {glucose_value_1} mg/dL {trend_arrow_1} at {timestamp_1}")
            else:
                print("Dexcom 1: No data available")

            if glucose_reading_2 is not None:
                glucose_value_2 = glucose_reading_2.value
                trend_arrow_2 = glucose_reading_2.trend_direction  # 'Flat' or '↑' etc.
                timestamp_2 = glucose_reading_2._datetime  # Glukoz ölçüm zamanı
                print(f"Dexcom 2: {glucose_value_2} mg/dL {trend_arrow_2} at {timestamp_2}")
            else:
                print("Dexcom 2: No data available")

            # If both sources have valid data, calculate the average and update the file
            if glucose_reading_1 is not None and glucose_reading_2 is not None:
                average_glucose = (glucose_value_1 + glucose_value_2) // 2
                trend_arrow = trend_arrow_1  # You can choose which trend arrow to use or calculate an average
                timestamp = timestamp_1  # Use the timestamp from the first device (or merge them as needed)
                update_bg_info(average_glucose, trend_arrow, timestamp)

            # If only one source has valid data, use that one
            elif glucose_reading_1 is not None:
                update_bg_info(glucose_value_1, trend_arrow_1, timestamp_1)

            elif glucose_reading_2 is not None:
                update_bg_info(glucose_value_2, trend_arrow_2, timestamp_2)

            else:
                print("No valid data from either source.")

            # Wait for 5 minutes (300 seconds) before checking again
            time.sleep(300)

        except Exception as e:
            print(f"Error fetching glucose data: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying if an error occurs

if __name__ == "__main__":
    check_glucose()
