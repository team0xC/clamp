from scapy.all import *
import socket
from collections import namedtuple
import os
import datetime

Category = namedtuple('Category', 
    ['service', 'attack_ip', 'attack_port'])

class Interceptor:

  def __init__(self, resources, services):
    self.res = resources
    self.paths = resources.paths
    self.files = resources.files
    self.attack = 'attack'
    self.defense = 'defense'
    self.dir_out = 'outgoing'
    self.dir_in = 'incoming'
    self.open_sessions = {}
    self.secs_between_timeout_checks = 5
    self.last_time_update = self.timestamp()
    self.max_time_between_messages = 10
    self.max_session_time = 180

    self.real_flags = set()
    self.real_tokens = set()

    self.session_timeout_msg = ("Session timeout: " + 
      str(self.max_session_time) + "s have elapsed since session started.")
    self.message_timeout_msg = ("Message timeout: " + 
      str(self.max_time_between_messages) + "s have elapsed since the last " + 
      "message was sent.")
    self.conn_reset_msg = "The other server sent a TCP RST flag."
    self.fake_flags_msg = "Fake flags or tokens were found in the response. "\
      "Spammed " + str(self.n_spammed) + " fake flags in response."
    self.new_session_msg = "New session started without closing old."


  def update_tick(self, tick_num):
    self.tick_num = tick_num


  def load_scripts(self):
    files = self.res.read_script_files(self.paths.reset_scripts)
    self.modules = self.res.reload_scripts(
      self.intercept_scripts_folder, files, self.modules)


  def find_new_flags(self):
    with open(self.files.real_tokens, 'r') as f:
      for token in f:
        token = token.rstrip('\n')
        self.real_tokens.add(token)

    with open(self.files.real_flags, 'r') as f:
      for flag in f:
        flag = flag.rstrip('\n')
        self.real_flags.add(flag)


  def callback(self, packet):
    if not self.is_valid_packet(packet):
      self.reset(packet)
      return

    category = self.categorize(packet)
    generic_response = self.flip_packet(packet)
    if self.is_syn(packet):
      self.write_metadata(category, packet)

    elif self.is_data(packet): # ignore handshake and acknowledgements
      if category in self.open_sessions:
        self.add_communication(category, packet)
        trapped = self.detect_fake_flags(category, packet)
        if trapped:
          self.n_spammed = self.spam_fake_flags(generic_response)
          self.close_session(category, {
            'summary': 'FAKEFLAGS',
            'details': self.fake_flags_msg })
          self.send_reset(generic_response)

        reset_msg = self.run_reset_scripts(packet)
        if reset_msg is not None:
          self.close_session(category, reset_msg)
          self.send_reset(generic_response)

    elif self.is_reset(packet): # close if reset sent
      self.close_session(category, {
        'summary': 'CONNRESET',
        'details': self.conn_reset_msg })

    current_time = timestamp()
    time_diff = current_time - self.last_time_update
    if time_diff.seconds >= self.secs_between_timeout_checks:
      self.last_time_update = current_time
      self.check_for_timeout(current_time, generic_response)
    

  def is_valid_packet(self, packet):
    has_ip = packet.haslayer(IP)
    has_tcp = packet.haslayer(TCP)
    valid = False
    if has_ip and has_tcp:
      src_port = int(packet[TCP].sport)
      dst_port = int(packet[TCP].dport)
      for service in self.res.services:
        if src_port == service.port or dst_port == service.port:
          valid = True
          break
    return valid


  def is_syn(self, packet):
    return packet[TCP].flags == 'S'


  def is_data(self, packet):
    has_load = packet.haslayer(Raw) and len(packet[Raw].load) > 0
    return packet[TCP].flags == 'PA' and has_load


  def is_reset(self, packet):
    return 'R' in packet[TCP].flags


  def categorize(self, packet):
    direction = None
    service = None
    attack_ip = None
    attack_port = None

    if packet[IP].dst == self.own_ip(): # incoming packet
      attack_ip = packet[IP].src
      attack_port = int(packet[TCP].sport)
      service_port = int(packet[TCP].dport)
        
    else: # outgoing packet
      attack_ip = packet[IP].dst
      attack_port = int(packet[TCP].dport)
      service_port = int(packet[TCP].sport)

    service = self.service_name(service_port)
    return Category(service, attack_ip, attack_port)


  def own_ip(self):
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


  def get_direction(self, packet):
    if packet[IP].dst == self.own_ip():
      direction = self.dir_in
    else:
      direction = self.dir_out
    return direction


  def write_metadata(self, category, packet):
    if self.open_sessions[category]:
      self.close_session(category, {
          'summary': 'NEWSTARTED',
          'details': self.new_session_msg })
      
    self.open_sessions[category] = {
      'metadata': {}, 'comms': []
    }
    meta = self.open_sessions[category]['metadata']
    if self.get_direction(packet) == self.dir_out:
      meta['action'] = self.attack
    else:
      meta['action'] = self.defense
    meta['service'] = category.service
    meta['flag'] = False
    meta['ignore flags'] = False


  def service_name(self, service_id):
    for service in self.res.services:
      if service_id == service.id or service_id == service.port:
        return service.name
    return self.invalid


  def add_communication(self, category, packet):
    self.open_sessions[category]['comms'].append({})
    meta = self.open_sessions[category]['metadata']
    comms = self.open_sessions[category]['comms']
    message = comms[-1]

    self.update_message_timestamp(meta, message)
    updated = self.update_message_count(meta, category, packet, message)
    load = self.update_load(packet, message)
    if updated: # Request
      self.update_seq_ack(meta, packet)
    else: # Response
      if self.res.flag_like_found(load) is not None:
        meta['flag'] = True


  def timestamp(self):
    return datetime.datetime.now()


  def time_format(self, dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


  def diff_minutes(self, start_time, end_time):
    diff = end_time - start_time
    minutes = str(diff.seconds // 60)
    seconds = "%.2d" % (diff.seconds % 60)
    return minutes + ":" + seconds


  def update_message_timestamp(self, meta, message):
    message['timestamp'] = self.timestamp()
    if 'first message' not in meta:
      meta['first message'] = message['timestamp']
    else:
      meta['last message'] = message['timestamp']


  def update_message_count(self, meta, category, packet, message):
    action = meta['action']
    direction = self.get_direction(packet)
    updated = True
    if 'n' not in meta:
      meta['n'] = 1
    elif self.attack_message(action, direction):
      meta['n'] += 1
    else:
      updated = False
    message['n'] = meta['n']
    return updated


  def attack_message(self, action, direction):
    return ((action == self.defense and direction == self.dir_in) or 
      (action == self.attack and direction == self.dir_out))


  def detect_fake_flags(self, category, packet):
    meta = self.open_sessions[category]['metadata']
    if meta['ignore flags']: # fake flags are being spammed
      return False
    # only look at responses of other teams' attacks
    if (meta['action'] == self.defense and 
      self.get_direction(packet) == self.dir_out):
      
      load = packet[Raw].load
      for match in self.res.detect_flag_like(load):
        detected_flag = match.group()
        if detected_flag not in self.real_flags(): # fake flag returned!
          return True

      for match in self.res.detect_token_like(load):
        detected_token = match.group()
        if detected_token not in self.real_tokens():
          return True

    return False


  def update_load(self, packet, message):
    load = packet[Raw].load
    message['load'] = load
    return load


  def update_seq_ack(self, packet, meta):
    meta['seq'] = int(packet[TCP].seq)
    meta['ack'] = int(packet[TCP].ack)
    meta['len'] = len(packet[Raw].load)


  def spam_fake_flags(self, category, response):
    meta = self.open_sessions[category]['metadata']
    meta['ignore flags'] = True
    num_spammed = 0
    for packets_to_spam in range(1, 5):
      flags_list = []
      for flags_per_packet in range(5, 50):
        flags_list.append(self.res.create_random_flag())
      num_spammed += len(flags_list)  
      new_response = response.copy()
      new_response[Raw].load = ''.join(flags_list)
      send(new_response)
    return num_spammed


  def run_reset_scripts(self, category, packet):
    meta = self.open_sessions[category]['metadata']
    # only look at other teams' attacks
    if (meta['action'] == self.defense):
      load = packet[Raw].load
      for name, module in self.modules.items(): 
        script = self.res.initialize_script(module)
        should_reset = script.run(load, direction)
        if should_reset:
          return script.message()
    return None


  def check_for_timeout(self, current_time, response):
    for category, session in self.open_sessions.items():
      meta = session['metadata']
      session_time = current_time - meta['first message']
      if session_time >= self.max_session_time:
        self.close_session(category, {
          'summary': 'TIMEOUT',
          'details': self.session_timeout_msg })
        self.send_reset(category, response)

      message_time = current_time - meta['last message']
      if message_time >= self.max_time_between_messages:
        self.close_session(category, {
          'summary': 'TIMEOUT',
          'details': self.message_timeout_msg })
        self.send_reset(response)


  def close_session(self, category, reason):
    # write dictionary entry to file, clear entry
    session_log = self.session_log_path(category, reason)
    self.write_attack_log(category, reason, session_log)
    del self.open_sessions[category]


  def session_log_path(self, category, reason):
    meta = self.open_sessions[category]['metadata']
    is_attack = (meta['action'] == self.attack)
    service = category.service
    length = meta['n']
    result = reason['summary']
    bang = meta['flag']
    return self.shared.session_log_path(
      is_attack, service, self.tick_num, length, result, bang)


  def write_attack_log(self, category, reason, filename):
    session = self.open_sessions[category]
    meta = session['metadata']
    comms = session['comms']
    n = 0
    with open(filename, 'a') as f:
      f.write('[METADATA]\n')

      start_time = self.time_format(meta['first message'])
      end_time = self.time_format(meta['last message'])
      diff_time = self.diff_minutes(start_time, end_time)
      if meta['flag']:
        f.write('  Flag-like string retrieved!')
      f.write('  Start time: ' + start_time + '\n')
      f.write('  End time: ' + end_time + '\n')
      f.write('  Diff time: ' + diff_time + '\n\n')

      f.write('[COMMUNICATION]\n')

      i = 0
      while i < len(comms):
        msg = comms[i]
        msg_time = self.time_format(msg['timestamp'])
        msg_load = msg['load']

        if n < msg['n']: # Request
          n = msg['n']
          f.write('{0}:   [{1}]   {2}\n\n'.format(n, msg_time, msg_load))

        else: # Response
          if msg['load'] != '\n':
            f.write(' >>> [{0}]   {2}\n\n'.format(n, msg_time, msg_load))

        i += 1

      f.write('[EXIT]\n')
      f.write('Summary: ' + reason['summary'] + '\n')
      f.write('Details: ' + reason['details'] + '\n')


  def flip_packet(self, category, packet):
    meta = self.open_sessions[category]['metadata']
    packet[IP].dst = packet[IP].src
    packet[IP].src = self.own_ip()
    packet[TCP].sport = packet[TCP].dport
    packet[TCP].dport = category.attack_port
    packet[TCP].seq = meta['ack']
    packet[TCP].ack = meta['seq'] + meta['len']
    return packet


  def send_reset(self, response):
    response[TCP].flags = 'R'
    send(response)


  def sniff(self):
    sniff(iface = 'tun0', filter = "tcp", prn = self.callback, store = False)


  