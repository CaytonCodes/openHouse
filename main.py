#! /usr/bin/env python

# Import necessary libraries for communication and display use
import interface.lcd.class_lcd_manager as lcd_manager
import class_open_house as house_manager
from time import sleep

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
manager = house_manager.OpenHouse()
display = manager.display

# Main body of code
try:
    while True:
        print(display.settings)
        print("Writing to display")
        display.write("Greetings Human!", 1)  # Write line of text to first line of display
        display.write("Demo Pi Guy code", 2)  # Write line of text to second line of display
        display.clear()                                # Clear the display of any data
        sleep(2)                                           # Give time for the message to be read
        display.stats_list((("TEMP", "75.5C"), ("RH", "52"), ("Time", "10:30A"), ("STATUS", "NORMAL")), True)
        sleep(20)
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    # display.clear()
