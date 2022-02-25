import os
import time
from scapy.all import *
import random
import threading


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


def timeout_script(interceptor, port, is_attack):
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
  data_packet(interceptor, packet, "Random user\n")

  time.sleep(0.3)
  data_packet(interceptor, response, "Enter your password:\n")

  time.sleep(25)
  packet[TCP].flags = 'R'
  data_packet(interceptor, packet, "12345\n")
  print(interceptor.open_sessions)


def run_test(interceptor):
  attack_port = random_port()
  defense_port = random_port()

  attack_thread = threading.Thread(target=timeout_script, 
    args=(interceptor, attack_port, True))
  defense_thread = threading.Thread(target=timeout_script,
    args=(interceptor, defense_port, False))

  # If this works, the attack thread should end with CONNRESET,
  # and the defense thread should end with TIMEOUT. Only attacks
  # from other teams should be reset from timeout.
  attack_thread.start()
  defense_thread.start()


  