import os
import time
from common import game_client, team
from interceptor_files.shared_resources import SharedResources
from executor import Executor
from interceptor import Interceptor
from fakeflags import FakeFlagsHoneypot
from threading import Thread

resources = None
executor = None
interceptor = None
fakeflags = None
last_tick_num = -1
flag_updates_in_tick = 0
first_flag_update_of_tick = False

start_of_exec_scripts = None
exec_tick = 0
exec_thread = None
int_thread = None


def start_of_new_tick():
  start_sniff()


def constantly():
  if fakeflags.update():
    if flag_updates_in_tick == 0:
      first_flag_update_of_tick = True
    flag_updates_in_tick += 1
    interceptor.find_new_flags()
    
  if not exec_thread.is_active():
    exec_thread = None
    runtime = time.time() - start_of_exec_scripts
    print("For tick {0}: Exploit scripts took {1}s to run".format(
      last_tick_num, runtime))


def every_five_seconds():
  if first_flag_update_of_tick and exec_thread is None:
    first_flag_update_of_tick = False
    start_of_exec_scripts = time.time()
    exec_tick = last_tick_num
    exec_thread = Thread(target=executor.run_all_exploits)
    exec_thread.start()
    exec_thread.run()


def halfway_through_tick():
  executor.load_exploits()
  interceptor.load_scripts()
  interceptor.find_new_flags()


def last_ten_seconds_of_tick():
  executor.load_exploits()
  interceptor.load_scripts()


def start_sniff():
  if int_thread is None or not int_thread.is_active():
    int_thread = Thread(target=interceptor.sniff)
    int_thread.start()
    int_thread.run()


if __name__ == '__main__':
  resources = SharedResources(os.getcwd())
  resources.set_services(game_client.services)
  executor = Executor(resources)
  executor.load_exploits()
  interceptor = Interceptor(resources)
  fakeflags = FakeFlagsHoneypot(resources)
  start_sniff()

  tick_num, seconds_left = game_client.tick_info()
  start_time = time.time()
  half_second_ago = start_time
  half_second_counter = 0
  halfway = False

  # Event loop
  while True:
    current_time = time.time()
    time_elapsed = current_time - start_time

    if time_elapsed < seconds_left:

      if not halfway and time_elapsed > seconds_left // 2:
        halfway_through_tick()
        halfway = True

      elif seconds_left - time_elapsed < 10.0:
        last_ten_seconds_of_tick()

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
      start_of_new_tick()
