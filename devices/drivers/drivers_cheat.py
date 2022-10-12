#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
for pin in [13, 15, 29, 31, 32, 33, 35, 37, 38, 40]:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, GPIO.HIGH)

def driver_control(interface):
  exitString = 'Exiting Chat.'
  interface.log('Driver control started.', 0, True)
  chatting = True
  while chatting:
    pin = interface.get_input('Enter pin number: ')
    if pin == 'exit':
      interface.log(exitString, 1, True)
      return
    pin = int(pin)
    period = interface.get_input('Enter period (seconds): ')
    if period == 'exit':
      interface.log(exitString, 1, True)
      return
    period = float(period)
    onState = interface.get_input('Enter on state: ', ['Low', 'High'])
    if onState == 'exit':
      interface.log(exitString, 1, True)
      return
    onStateVal = GPIO.LOW if onState == 'Low' else GPIO.HIGH
    offStateVal = GPIO.HIGH if onState == 'Low' else GPIO.LOW
    interface.log('Starting driver control on pin ' + str(pin) + ' with period ' + str(period) + ' seconds, ON state: ' + onState, 0, True)
    GPIO.output(pin, onStateVal)
    sleep(period)
    GPIO.output(pin, offStateVal)
    interface.log('Driver control complete.', 0, True)

