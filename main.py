import network
import urequests
import ujson
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time

# Initialize the OLED display
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)
DEBOUNCE_DELAY_MS = 200

up_button = Pin(16, Pin.IN, Pin.PULL_UP)  # switch to match below			rx-black
down_button = Pin(17, Pin.IN, Pin.PULL_UP)  # switch to match above												tx - white
select_button = Pin(18, Pin.IN, Pin.PULL_UP)  # button to select match & get information ahade					blue
back_button = Pin(15, Pin.IN, Pin.PULL_UP)  # Added a "back" button												purple

# Define the API URL for the GET request
url = ("https://api.cricapi.com/v1/currentMatches?apikey=___ ADD YOUR API HERE___&offset=0")


def clear_oled():
    oled.fill(0)
    oled.show()


ssid = "____ YOUR ____ SSID[WIFI NAME]_____"
password = "____YOUR PASSWORD____"
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    select_button_state = select_button.value()
    clear_oled()
    oled.text(f"press select to conn.:", 0, 24)
    oled.show()
    if select_button_state == 0:
        clear_oled()
        oled.text(f"Connecting to :", 0, 16)
        oled.text(f"wifi", 0, 32)
        oled.show()
        time.sleep(1)
        print("not connected")
        time.sleep(1)
        station.connect(ssid, password)


else:
    print("connected")
    clear_oled()
    oled.text(f"Connected to :", 0, 24)
    oled.text(f"WIFI", 0, 32)
    oled.show()
    time.sleep(1)


scroll_position = 0  # Track the scroll position
matches = []  # Store the match data


clear_oled()
print("greet")
oled.text(f"Created by Viren Modiyani", 0, 0)
oled.text(f"         modiyani", 0, 8)
oled.text(f"LINE 3", 0, 24)
oled.text(f"LINE 4", 0, 32)
oled.text(f"LINE 5", 0, 48)
oled.text(f"LINE 6", 0, 56)
oled.show()
time.sleep(2)
clear_oled()


while True:
    if station.isconnected():
        response = urequests.get(url)
        if response.status_code == 200:
            data = ujson.loads(response.text)
            matches = data["data"]
            print("got data")

    clear_oled()
    oled.text("Select match:", 0, 0)
    oled.show()
    break

    # Display a list of matches based on the current scroll position
# ...
def back_to_main_menu():
    clear_oled()
    for i in range(scroll_position, min(scroll_position + 3, len(matches))):
        match_info = matches[i]
        short_names = [team["shortname"] for team in match_info["teamInfo"]]
        match_display = " vs ".join(short_names)
        oled.text(f"{i + 1}. {match_display}", 0, 16 * (i - scroll_position) + 16)
        print(f"{i + 1}. {match_display}")
        oled.text("Select match:", 0, 0)
        oled.show()


def main_menu():
    clear_oled()
    for i in range(scroll_position, min(scroll_position + 3, len(matches))):
        match_info = matches[i]
        short_names = [team["shortname"] for team in match_info["teamInfo"]]
        match_display = " vs ".join(short_names)
        oled.text(f"{i + 1}. {match_display}", 0, 16 * (i - scroll_position) + 16)
        print(f"{i + 1}. {match_display}")
        oled.text("Select match:", 0, 0)
        oled.show()


def display_match_information(selected_match):
    # while True:
    #         back_button_state = back_button.value()
    #         if(back_button_state==0):
    #             #back_to_main_menu()
    #             break
    # Display match information on the OLED
    # else:
    my_line = 0
    clear_oled()
    match_teams = selected_match["teamInfo"]
    short_names = [team["shortname"] for team in match_teams]
    match_display = " vs ".join(short_names)

    # Split the match_display into lines with a maximum of 16 characters
    lines = [match_display[i : i + 16] for i in range(0, len(match_display), 16)]

    # Display the first 8 lines
    for i in range(min(len(lines), 8)):
        oled.text(lines[i], 0, i * 8)
        my_line = my_line + 1
        print(lines[i], 0, i * 8)

    # Extract and display runs and wickets information
    current_line = 8

    team1_score = ""
    team2_score = ""
    inn1 = 0
    # Iterate through the scores and split them into two strings
    for score in selected_match["score"]:
        if inn1 == 0:
            inn2 = score["inning"]
            inn1 = 1

        inning = score["inning"]
        runs = score["r"]
        wickets = score["w"]
        over = score["o"]
        info_line = f"{inning}: {runs}/{wickets} in {over}\n"

        if inn2 in inning:
            team1_score += info_line
        else:
            team2_score += info_line

    # Print or use team1_score and team2_score as needed
    print("Team 1 Score:")
    # print(team1_score,0, my_line*8)
    # Input string
    input_string = team1_score
    # Initialize line number
    line_number = 1
    # Process the input string
    while input_string:
        # Extract up to 16 characters from the input string
        current_line = input_string[:16]

        # Check if there are more than 16 characters left
        if len(input_string) > 16:
            # Find the first space from the end within the first 16 characters
            last_space_index = current_line.rfind(" ")

            if last_space_index != -1:
                # Include the space character in the current line
                current_line = current_line[: last_space_index + 1]

            # Remove the processed characters from the input string
            input_string = input_string[len(current_line) :]
        else:
            # The input string is shorter than 16 characters
            input_string = ""

        # Output the current line with line number
        print(f"Line {line_number}: {current_line}")
        oled.text(current_line, 0, my_line * 8)
        my_line = my_line + 1

        # Increment the line number
        line_number += 1

    # oled.text(team1_score, 0,my_line*8)
    # my_line=my_line+1

    print("Team 2 Score:")
    print(team2_score, 0, my_line * 8)
    input_string = team2_score
    # Initialize line number
    line_number = 1
    # Process the input string
    while input_string:
        # Extract up to 16 characters from the input string
        current_line = input_string[:16]

        # Check if there are more than 16 characters left
        if len(input_string) > 16:
            # Find the first space from the end within the first 16 characters
            last_space_index = current_line.rfind(" ")

            if last_space_index != -1:
                # Include the space character in the current line
                current_line = current_line[: last_space_index + 1]

            # Remove the processed characters from the input string
            input_string = input_string[len(current_line) :]
        else:
            # The input string is shorter than 16 characters
            input_string = ""

        # Output the current line with line number
        print(f"Line {line_number}: {current_line}")
        oled.text(current_line, 0, my_line * 8)
        my_line = my_line + 1

        # Increment the line number
        line_number += 1
    oled.show()

    time.sleep(8)
    my_line = 0
    clear_oled()

    input_string = selected_match["venue"]
    # Initialize line number
    line_number = 1
    # Process the input string
    while input_string:
        # Extract up to 16 characters from the input string
        current_line = input_string[:16]

        # Check if there are more than 16 characters left
        if len(input_string) > 16:
            # Find the first space from the end within the first 16 characters
            last_space_index = current_line.rfind(" ")

            if last_space_index != -1:
                # Include the space character in the current line
                current_line = current_line[: last_space_index + 1]

            # Remove the processed characters from the input string
            input_string = input_string[len(current_line) :]
        else:
            # The input string is shorter than 16 characters
            input_string = ""

        # Output the current line with line number
        print(f"Line {line_number}: {current_line}")
        oled.text(current_line, 0, my_line * 8)
        my_line = my_line + 1

        # Increment the line number
        line_number += 1

    input_string = selected_match["date"]
    # Initialize line number
    line_number = 1
    # Process the input string
    while input_string:
        # Extract up to 16 characters from the input string
        current_line = input_string[:16]

        # Check if there are more than 16 characters left
        if len(input_string) > 16:
            # Find the first space from the end within the first 16 characters
            last_space_index = current_line.rfind(" ")

            if last_space_index != -1:
                # Include the space character in the current line
                current_line = current_line[: last_space_index + 1]

            # Remove the processed characters from the input string
            input_string = input_string[len(current_line) :]
        else:
            # The input string is shorter than 16 characters
            input_string = ""

        # Output the current line with line number
        print(f"Line {line_number}: {current_line}")
        oled.text(current_line, 0, my_line * 8)
        my_line = my_line + 1

        # Increment the line number
        line_number += 1

    oled.show()
    time.sleep(3)

    my_line = 0
    clear_oled()
    input_string = selected_match["status"]
    # Initialize line number
    line_number = 1
    # Process the input string
    while input_string:
        # Extract up to 16 characters from the input string
        current_line = input_string[:16]

        # Check if there are more than 16 characters left
        if len(input_string) > 16:
            # Find the first space from the end within the first 16 characters
            last_space_index = current_line.rfind(" ")

            if last_space_index != -1:
                # Include the space character in the current line
                current_line = current_line[: last_space_index + 1]

            # Remove the processed characters from the input string
            input_string = input_string[len(current_line) :]
        else:
            # The input string is shorter than 16 characters
            input_string = ""

        # Output the current line with line number
        print(f"Line {line_number}: {current_line}")
        oled.text(current_line, 0, my_line * 8)
        my_line = my_line + 1

        # Increment the line number
        line_number += 1

    oled.show()
    time.sleep(1)


#             back_button_state = back_button.value()
#             if(back_button_state==0):
#                 #back_to_main_menu()
#                 break
# break

# Display a list of matches based on the current scroll position
# ...

for i in range(scroll_position, min(scroll_position + 3, len(matches))):
    match_info = matches[i]
    short_names = [team["shortname"] for team in match_info["teamInfo"]]
    match_display = " vs ".join(short_names)
    oled.text(f"{i + 1}. {match_display}", 0, 16 * (i - scroll_position) + 16)
    print(f"{i + 1}. {match_display}")
    oled.show()

# Check for button presses
while True:
    # Read the button states
    up_button_state = up_button.value()
    down_button_state = down_button.value()
    select_button_state = select_button.value()
    back_button_state = back_button.value()

    # Handle button presses with debounce
    if up_button_state == 0:
        print("up")
        time.sleep_ms(DEBOUNCE_DELAY_MS)  # Debounce delay
        if up_button.value() == 0:
            # Button is still pressed after debounce, handle the press
            scroll_position = (
                (scroll_position - 1) if scroll_position > 0 else len(matches) - 5
            )
            main_menu()

    if down_button_state == 0:
        print("down")
        time.sleep_ms(DEBOUNCE_DELAY_MS)  # Debounce delay
        if down_button.value() == 0:
            # Button is still pressed after debounce, handle the press
            scroll_position = (scroll_position + 1) % len(matches)
            main_menu()

    if select_button_state == 0:
        print("slect")
        time.sleep_ms(DEBOUNCE_DELAY_MS)  # Debounce delay
        if select_button.value() == 0:
            # Button is still pressed after debounce, handle the press
            selected_match = matches[scroll_position]
            display_match_information(selected_match)
            print("display ended")
            # while select_button.value() == 1:
            # pass

    if back_button_state == 0:
        print("back")
        time.sleep_ms(DEBOUNCE_DELAY_MS)  # Debounce delay
        if back_button.value() == 0:
            # Button is still pressed after debounce, handle the press
            back_to_main_menu()
