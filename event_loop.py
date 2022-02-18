import os
import time
from common import game_client, team
from interceptor_files.shared_resources import SharedResources

resources = None

def start_of_new_tick():
  pass


def every_five_seconds():
  resources.update_scripts()


def halfway_through_tick():
  pass


def last_ten_seconds_of_tick():
  pass



if __name__ == '__main__':
  resources = SharedResources(os.getcwd())

  last_tick_num = -1
  tick_num, seconds_left = game_client.tick_info()
  start_time = time.time()
  five_seconds_ago = start_time
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

      elif current_time - five_seconds_ago >= 5.0:
        five_seconds_ago = time.time()
        every_five_seconds()

    else:
      tick_num, seconds_left = game_client.tick_info()
      if tick_num == last_tick_num or seconds_left < 5.0:
        time.sleep(round(seconds_left + 1))
      
      tick_num, seconds_left = game_client.tick_info()
      start_time = time.time()
      halfway = False
      start_of_new_tick()
