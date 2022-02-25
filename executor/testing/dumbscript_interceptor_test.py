import os
import time
from scapy.all import *
import random
import threading
from common_stub import game_client, team
from interceptor_files.shared_resources import SharedResources
from interceptor import Interceptor

home_ip = '127.0.1.1'
away_ip = '10.0.9.3'
service_port = 10001

def create_packet(src_port, is_attack):
  if is_attack:
    ip = IP(src=home_ip, dst=away_ip)
    tcp = TCP(sport=service_port, dport=src_port)
  else:
    ip = IP(src=away_ip, dst=home_ip)
    tcp = TCP(sport=src_port, dport=service_port)
  packet = ip / tcp
  return packet.__class__(bytes(packet))


def random_port():
  return int(random.random() * 65535)


def data_packet(interceptor, packet, msg):
  packet = packet.copy() / Raw(load=msg)
  interceptor.callback(packet)


def fake_flags_script(interceptor, port, is_attack):
  packet = create_packet(port, is_attack)
  response = interceptor.flip_packet(packet)
  packet.show()
  response.show()

  packet[TCP].flags = 'S'
  interceptor.callback(packet)

  time.sleep(2)
  response[TCP].flags = 'PA'
  data_packet(interceptor, response, "Welcome to this made up service!\n")
  time.sleep(0.3)
  data_packet(interceptor, response, "\n")
  time.sleep(0.3)
  data_packet(interceptor, response, "Enter your name:\n")

  time.sleep(1)
  packet[TCP].flags = 'PA'
  data_packet(interceptor, packet, "I win!!\n")

  time.sleep(0.3)
  data_packet(interceptor, response, "Oh really?\n")
  print(interceptor.open_sessions)


if __name__ == '__main__':
  res = SharedResources(os.getcwd())
  res.set_services(game_client.services)
  interceptor = Interceptor(res)
  interceptor.load_scripts()
  interceptor.update_tick(1)

  port = random_port()

  thread = threading.Thread(target=fake_flags_script, 
    args=(interceptor, port, False))

  # Reset connection when they type 'win'
  thread.start()