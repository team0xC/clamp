import os
import time
from scapy.all import *
from common_stub import game_client, team
from interceptor_files.shared_resources import SharedResources
from interceptor import Interceptor

home_ip = '127.0.1.1'
away_ip = '10.0.9.3'
service_port = 10001

def create_packet(src_port):
  ip = IP(src=away_ip, dst=home_ip)
  tcp = TCP(sport=src_port, dport=service_port)
  packet = ip / tcp
  return packet.__class__(bytes(packet))


def comms_packet(interceptor, category, packet, msg):
  packet = packet.copy() / Raw(load=msg)
  load = interceptor.decode_load(packet)
  interceptor.add_communication(category, load, packet)
  print(interceptor.open_sessions[category]['comms'][-1])


if __name__ == '__main__':
  res = SharedResources(os.getcwd())
  res.set_services(game_client.services)
  interceptor = Interceptor(res)
  interceptor.update_tick(1)

  print(res.services)
  print("own ip: {0}".format(interceptor.own_ip()))

  packet = create_packet(22339)
  print("Incoming packet")
  packet.show()
  response = interceptor.flip_packet(packet)
  print("Response packet")
  response.show()

  print("valid: {0}".format(interceptor.is_valid_packet(packet)))

  category = interceptor.categorize(packet)
  print(category)

  packet[TCP].flags = 'S'
  print("packet is SYN: {0}".format(interceptor.is_syn(packet)))

  packet[TCP].flags = 'PA'
  data_packet = packet / Raw(load="Hello world!")
  print("packet is data: {0}".format(interceptor.is_data(packet)))
  print("data packet is data: {0}".format(interceptor.is_data(data_packet)))
  packet[TCP].flags = 'RA'
  print("packet is RST: {0}".format(interceptor.is_reset(packet)))

  print("direction of packet: {0}".format(interceptor.get_direction(packet)))
  print("direction of response: {0}".format(interceptor.get_direction(response)))

  start_time = interceptor.timestamp()
  print("start time: " + interceptor.time_format(start_time))
  time.sleep(3)
  end_time = interceptor.timestamp()
  print("end time: " + interceptor.time_format(end_time))
  print("difference in minutes: " + interceptor.diff_minutes(start_time, end_time))

  print("writing metadata...")
  packet[TCP].flags = 'S'
  interceptor.write_metadata(category, packet)
  print(interceptor.open_sessions[category])
  packet[TCP].flags = 'PA'

  time.sleep(0.5)
  response[TCP].flags = 'PA'

  comms_packet(interceptor, category, response, "Welcome to this made up service!\n")
  comms_packet(interceptor, category, response, "\n")
  time.sleep(0.3)
  comms_packet(interceptor, category, response, "Please enter your name:\n")

  time.sleep(1)
  comms_packet(interceptor, category, packet, "User123\n")

  time.sleep(0.3)
  comms_packet(interceptor, category, response, "Please enter your password\n")

  time.sleep(0.5)
  packet[TCP].ack = 576844
  packet[TCP].seq = 257444558
  comms_packet(interceptor, category, packet, "password\n")

  time.sleep(0.3)
  response[TCP].flags = 'RA'
  comms_packet(interceptor, category, response, "Your password sucks! Good bye!\n")
  print(interceptor.open_sessions[category]['metadata'])
  interceptor.close_session(category, {
    'summary': 'CONNRESET',
    'details': interceptor.conn_reset_msg })