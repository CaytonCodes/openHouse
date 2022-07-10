#! /usr/bin/env python

# Import necessary libraries for communication and display use
import lcd.class_lcd_manager as lcd_manager
from time import sleep

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = lcd_manager.LcdManager()

# Main body of code
try:
    while True:
        print("Writing to display")
        display.write("Greetings Human!", 1)  # Write line of text to first line of display
        display.write("Demo Pi Guy code", 2)  # Write line of text to second line of display
        sleep(2)                                           # Give time for the message to be read
        display.write("I am a display!", 1)   # Refresh the first line of display with a different message
        display.write("This line will be too long.", 2)  # Write line of text to second line of display
        sleep(2)                                           # Give time for the message to be read
        display.lcd_clear()                                # Clear the display of any data
        sleep(2)                                           # Give time for the message to be read
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()
