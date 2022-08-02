#!/usr/bin/env python

import sys
import threading
import time
import queue

DEFAULT_BREAKER = '\n'

class KeyboardWatcher():
  def __init__(self, breaker = DEFAULT_BREAKER):
    self.breaker = breaker
    self.runningString = {'val': '', 'complete': False}
    # self.check_keyboard()
    self.queue_in = self.prep_queue()

  def set_breaker(self, breaker):
    self.breaker = breaker

  def add_input(self, input_queue):
    while True:
      input_queue.put(sys.stdin.read(1))

  def get_running_string(self):
    if self.runningString['complete']:
      self.runningString = {'val': '', 'complete': False}
    while not self.queue_in.empty():
      key = self.queue_in.get()
      if key == self.breaker:
        self.runningString['complete'] = True
      else:
        self.runningString['val'] += key
    return self.runningString

  def prep_queue(self):
    queue_in = queue.Queue()
    thread = threading.Thread(target=self.add_input, args=(queue_in,))
    thread.daemon = True
    thread.start()
    return queue_in

  def check_keyboard(self):
    queue_in = queue.Queue()

    thread = threading.Thread(target=self.add_input, args=(queue_in,))
    thread.daemon = True
    thread.start()
    last_update = time.time()

    while True:
      if time.time() - last_update > 0.5:
        sys.stdout.write('')
        sys.stdout.flush()
        last_update = time.time()

      if not queue_in.empty():
        key = queue_in.get()
        print('keyhit: ', key)
        self.runningString['val'] += key
        if key == self.breaker:
          self.runningString['complete'] = True
