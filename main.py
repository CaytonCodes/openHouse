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
        # print(manager)
        # manager.stats_screen()
        # sleep(1)
        # print('finding ph')
        # print(vars(manager.sensors['PH1'].query('Find', 1)))
        # sleep(4)
        # print('releasing ph')
        # print(manager.sensors['PH1'].query('i', 1).get_data())
        # print(manager.sensors['PH1'].query('i', 1).get_data(type = 'string'))
        print(type(manager.sensors['PH1'].query('r', 1).get_data(type = 'float')))
        sleep(4)
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    # display.clear()
