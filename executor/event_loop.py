#!/usr/bin/env python3
# CSE545 Spring A - Team 12 (team0xC)
# https://github.com/team0xC/clamp

"""
Main event loop to query swpag_client for new ticks, and run various functions
from the executor and interceptor at various intervals:

    constantly()           # every half second
    every_five_seconds()
    start_of_new_tick()
    halfway_through_tick()
    last_ten_seconds_of_tick()
"""

import os
import time
import threading
from common import game_client, team
from interceptor_files.shared_resources import SharedResources
from executor import Executor
from interceptor import Interceptor
from fakeflags import FakeFlagsHoneypot


resources = None
executor = None
interceptor = None
fakeflags = None
last_tick_num = -1
flag_updates_in_tick = 0
first_flag_update_of_tick = False

exec_tick = 0
exec_threads = []
int_thread = None


def start_of_new_tick():
  interceptor.update_tick(last_tick_num)
  start_sniff()


def constantly():
  global fakeflags, flag_updates_in_tick, first_flag_update_of_tick
  global exec_threads
  # New files have been detected in a flag directory
  if fakeflags.update():
    # Check if it's the first update of a tick, might be the script bot
    if flag_updates_in_tick == 0:
      first_flag_update_of_tick = True
    flag_updates_in_tick += 1

    # Update list of real flags to sniffer
    interceptor.find_new_flags()
    
  # Exploit script thread execution has terminated. Log time run.
  if len(exec_threads) > 0:
    for thread, start_time in exec_threads:
      if not thread.is_alive():
        thread.handled = True
        runtime = time.time() - start_time
        print("Exploit script took {0}s to run".format(round(runtime, 2)))
    exec_threads = [t for t in exec_threads if not t[0].handled]


def every_five_seconds():
  global first_flag_update_of_tick, exec_threads, executor, interceptor
  # Run exploit scripts if they're not being run
  if first_flag_update_of_tick:
    first_flag_update_of_tick = False
    start_time = time.time()
    thread = threading.Thread(target=executor.run_all_exploits)
    exec_threads.append((thread, start_time))
    thread.start()

  # Reset connections that take too long
  interceptor.check_for_timeout()


def halfway_through_tick():
  global executor, interceptor
  # Dynamically reload scripts
  executor.load_exploits()
  interceptor.load_scripts()

  # Update list of real flags to sniffer
  interceptor.find_new_flags()


def last_ten_seconds_of_tick():
  global executor, interceptor
  # Dynamically reload scripts
  executor.load_exploits()
  interceptor.load_scripts()


def start_sniff():
  """
  Restart sniff() thread if it has been terminated due to a bug.
  """
  global int_thread, interceptor
  if int_thread is None or not int_thread.is_alive():
    int_thread = threading.Thread(target=interceptor.sniff)
    int_thread.start()


if __name__ == '__main__':
  # Initialize objects and script lists
  resources = SharedResources(os.getcwd())
  resources.set_services(game_client.services)
  executor = Executor(resources)
  executor.load_exploits()
  interceptor = Interceptor(resources)
  interceptor.load_scripts()
  fakeflags = FakeFlagsHoneypot(resources)
  start_sniff()

  tick_num, seconds_left = game_client.tick_info()
  interceptor.update_tick(tick_num)
  start_time = time.time()
  half_second_ago = start_time
  half_second_counter = 0
  halfway = False
  last_ten_passed = False

  # Event loop
  while True:
    current_time = time.time()
    time_elapsed = current_time - start_time

    if time_elapsed < seconds_left:

      if not halfway and time_elapsed > seconds_left // 2:
        halfway_through_tick()
        halfway = True

      elif seconds_left - time_elapsed < 10.0 and not last_ten_passed:
        last_ten_seconds_of_tick()
        last_ten_passed = True

      if current_time - half_second_ago >= 0.5:
        half_second_ago = time.time()
        half_second_counter += 1
        constantly()
        if half_second_counter == 10:
          half_second_counter = 0
          every_five_seconds()

    else:
      tick_num, seconds_left = game_client.tick_info()
      while tick_num == last_tick_num or seconds_left < 5.0:
        time.sleep(round(seconds_left + 1))
        tick_num, seconds_left = game_client.tick_info()
      
      print("Tick " + str(tick_num) + '\n')
      start_time = time.time()
      last_tick_num = tick_num
      halfway = False
      flag_updates_in_tick = 0
      first_flag_update_of_tick = False
      last_ten_passed = False
      start_of_new_tick()
