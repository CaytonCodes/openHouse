#! /usr/bin/env python

# Import necessary libraries for communication and display use
# import interface.lcd.class_lcd_manager as lcd_manager
import class_open_grow as house_manager
from time import sleep

manager = house_manager.OpenGrow()

# Main body of code
try:
    while True:
        print("Starting up...")
        print(manager)
        manager.stats_screen()
        sleep(20)
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    # display.clear()
