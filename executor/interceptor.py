#!/usr/bin/env python3
# CSE545 Spring A - Team 12 (team0xC)
# https://github.com/team0xC/clamp

from scapy.all import *
import socket
from collections import namedtuple
import os
import datetime

Category = namedtuple('Category', 
    ['service', 'attack_ip', 'attack_port'])


class Interceptor:

  def __init__(self, resources):
    self.res = resources
    self.paths = resources.paths
    self.files = resources.files
    self.attack = 'attack'
    self.defense = 'defense'
    self.dir_out = 'outgoing'
    self.dir_in = 'incoming'
    self.open_sessions = {}
    self.max_time_between_messages = 10
    self.max_session_time = 180
    self.tick_num = 0

    self.real_flags = set()
    self.real_tokens = set()

    self.modules = {}

    self.session_timeout_msg = ("Session timeout: " + 
      str(self.max_session_time) + "s have elapsed since session started.")
    self.message_timeout_msg = ("Message timeout: " + 
      str(self.max_time_between_messages) + "s have elapsed since the last " + 
      "message was sent.")
    self.conn_reset_msg = "The other server sent a TCP RST flag."
    self.fake_flags_msg = lambda n: ("Fake flags or tokens were found in the "
      "response. Spammed " + str(n) + " fake flags in response.")
    self.new_session_msg = "New session started without closing old."


  def update_tick(self, tick_num):
    self.tick_num = tick_num


  def load_scripts(self):
    """
    Load reset scripts, saving each module object in memory.
    """
    files = self.res.read_script_files(self.paths.reset_scripts)
    self.modules = self.res.reload_scripts(
      self.res.intercept_scripts_folder, files, self.modules)


  def find_new_flags(self):
    """
    Find new flags that have been catalogued when the flag directories 
    increased in size. These are used to recognize fake flags for the 
    honeypot.
    """
    if os.path.isfile(self.files.real_tokens):
      with open(self.files.real_tokens, 'r') as f:
        for token in f:
          token = token.rstrip('\n')
          if len(token) > 0:
            self.real_tokens.add(token)

    if os.path.isfile(self.files.real_flags):
      with open(self.files.real_flags, 'r') as f:
        for flag in f:
          flag = flag.rstrip('\n')
          if len(flag) > 0:
            self.real_flags.add(flag)


  def callback(self, packet):
    """
    Callback function from scapy sniff() to log session and run reset scripts.
    
    :param      packet:  The packet
    :type       packet:  scapy.packet.Packet
    """

    # Reset session if sent to invalid port
    if not self.is_valid_packet(packet):
      response = self.flip_packet(packet)
      self.send_reset(response)
      return

    # Categorize packet by target service and attacker ip/port as a unique
    # identifier to log session data
    category = self.categorize(packet)

    # Craft a response packet in preparation to reset connection
    generic_response = self.flip_packet(packet)

    # Start a new session log if SYN detected
    if self.is_syn(packet):
      self.write_metadata(category, packet)

    # Add to session log if data packet (ignore handshake and ACK)
    else:
      if self.is_data(packet):
        # Valid session
        load = self.decode_load(packet)
        if category in self.open_sessions:
          self.add_communication(category, load, packet)
        else:
          self.send_reset(generic_response)
          return

        # Look for fake flags in the response body
        trapped = self.detect_fake_flags(category, load, packet)
        if trapped: # if found, spam fake flags to confuse other team
          num_spammed = self.spam_fake_flags(category, generic_response)
          self.close_session(category, {
            'summary': 'FAKEFLAGS',
            'details': self.fake_flags_msg(num_spammed) })
          self.send_reset(generic_response)
          return

        # Run custom reset scripts
        reset_msg = self.run_reset_scripts(category, packet)
        if reset_msg is not None:
          self.close_session(category, reset_msg)
          self.send_reset(generic_response)
          return

      # Check if a reset was initiated
      if self.is_reset(packet):
        if category in self.open_sessions:
          self.close_session(category, {
            'summary': 'CONNRESET',
            'details': self.conn_reset_msg })
          return
    

  def is_valid_packet(self, packet):
    """
    Determines whether the specified packet uses the relevant protocol and
    ports.
    
    :param      packet:  The packet
    :type       packet:  scapy.packet.Packet

    :returns:   True if packet is relevant
    :rtype:     boolean
    """
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
    """
    Determines whether the specified TCP packet has the SYN flag.
    
    :param      packet:  TCP packet
    :type       packet:  scapy.packet.Packet

    :returns:   True if packet is a SYN packet
    :rtype:     boolean
    """
    return packet[TCP].flags == 'S'


  def is_data(self, packet):
    """
    Determines whether the specified TCP packet is a data packet with a 
    non-zero load.
    
    :param      packet:  TCP packet
    :type       packet:  scapy.packet.Packet

    :returns:   True if packet is a data packet
    :rtype:     boolean
    """
    has_load = packet.haslayer(Raw) and len(packet[Raw].load) > 0
    return has_load


  def is_reset(self, packet):
    """
    Determines whether the specified TCP packet has the RST flag.
    
    :param      packet:  TCP packet
    :type       packet:  scapy.packet.Packet

    :returns:   True if packet is a RST packet
    :rtype:     boolean
    """
    return 'R' in packet[TCP].flags


  def categorize(self, packet):
    """
    Categorize packet by target service name, and ip and port of the attacker.
    
    :param      packet:  TCP packet
    :type       packet:  scapy.packet.Packet

    :returns:   A namedtuple with the target service name, and info about the
                attacker.
    :rtype:     Category
    """
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
    """
    Get our own ip address

    :returns:   IP address using our own hostname
    :rtype:     string
    """
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


  def get_direction(self, packet):
    """
    Determines whether the packet is incoming or outgoing.
    
    :param      packet:  TCP packet
    :type       packet:  scapy.packet.Packet

    :returns:   "incoming" or "outgoing"
    :rtype:     string
    """
    if packet[IP].dst == self.own_ip():
      direction = self.dir_in
    else:
      direction = self.dir_out
    return direction


  def write_metadata(self, category, packet):
    """
    Tracks some metadata to start a session communication by storing it into
    a dictionary entry representing the current session. Particularly, it 
    saves whether the session is initiated by us or another team, the service
    it targets, whether a flag has been detected, etc.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet
    """
    if category in self.open_sessions:
      self.close_session(category, {
          'summary': 'NEWSTARTED',
          'details': self.new_session_msg })
      
    self.open_sessions[category] = {
      'metadata': {}, 'comms': []
    }
    meta = self.open_sessions[category]['metadata']
    if self.get_direction(packet) == self.dir_out:
      meta['action'] = self.attack
      meta['ip'] = packet[IP].dst
      meta['port'] = packet[TCP].dport
      meta['service port'] = packet[TCP].sport
    else:
      meta['action'] = self.defense
      meta['ip'] = packet[IP].src
      meta['port'] = packet[TCP].sport
      meta['service port'] = packet[TCP].dport
    meta['service'] = category.service
    meta['flag'] = False
    meta['ignore flags'] = False
    self.update_seq_ack(packet, meta)


  def service_name(self, service_id):
    """
    Get the service name from service ID.
    
    :param      service_id:  The service identifier, either ID or port
    :type       service_id:  integer

    :returns:   Name of the service
    :rtype:     string
    """
    for service in self.res.services:
      if service_id == service.id or service_id == service.port:
        return service.name
    raise ValueError("Invalid port.")


  def add_communication(self, category, load, packet):
    """
    Appends to the list of communication of the session with a new entry
    representing a new data request or response.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      packet:    decoded load
    :type       packet:    string
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet
    """
    self.open_sessions[category]['comms'].append({})
    meta = self.open_sessions[category]['metadata']
    comms = self.open_sessions[category]['comms']
    message = comms[-1]

    # Add latest time and number of requests to session metadata
    self.update_message_timestamp(meta, message)
    updated = self.update_message_count(meta, category, packet, message)

    message['load'] = load
    if updated: # Request
      self.update_seq_ack(packet, meta)
    else: # Response
      if self.res.flag_like_found(load):
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
    """
    Add first or last message times to session metadata.
    
    :param      meta:     Session metadata object
    :type       meta:     dict
    :param      message:  Object representing latest data request
    :type       message:  dict
    """
    message['timestamp'] = self.timestamp()
    if 'first message' not in meta:
      meta['first message'] = message['timestamp']
    else:
      meta['last message'] = message['timestamp']


  def update_message_count(self, meta, category, packet, message):
    """
    Update request count in the metadata if packet is a request.
    
    :param      meta:     Session metadata object
    :type       meta:     dict
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet
    :param      message:  Object representing latest data request
    :type       message:  dict

    :returns:   Whether the request count has been updated
    :rtype:     boolean
    """
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
    """
    Determines whether latest packet is a request 
    (i.e. from the initiator/attacker of the session)
    
    :param      action:     "attack" or "defense"
    :type       action:     string
    :param      direction:  "incoming" or "outgoing"
    :type       direction:  string

    :returns:   True if packet is a request
    :rtype:     boolean
    """
    return ((action == self.defense and direction == self.dir_in) or 
      (action == self.attack and direction == self.dir_out))


  def detect_fake_flags(self, category, load, packet):
    """
    Detect if fake flags are present in genuine service responses (e.g. not
    spammed by the interceptor).
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      packet:    decoded load
    :type       packet:    string
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet

    :returns:   True if response is genuine and contains a fake flag
    :rtype:     boolean
    """
    meta = self.open_sessions[category]['metadata']
    if meta['ignore flags']: # fake flags are being spammed
      return False
    # only look at responses to other teams' attacks
    if (meta['action'] == self.defense and 
      self.get_direction(packet) == self.dir_out):
      
      for match in self.res.detect_flag_like(load):
        detected_flag = match.group()
        if detected_flag not in self.real_flags: # fake flag returned!
          return True

      for match in self.res.detect_token_like(load):
        detected_token = match.group()
        if detected_token not in self.real_tokens:
          return True

    return False


  def decode_load(self, packet):
    """
    Decode load bytestring to ascii if alphanumeric, keep other bytes visually intact.

    e.g. b'Hello\x90' --> "Hello\\x90"
    
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet

    :returns:   The decoded load
    :rtype:     string
    """
    load_bytes = packet[Raw].load
    bytes_list = chexdump(load_bytes, dump=True).split(', ')
    for i in range(len(bytes_list)):
      hex_val = int(bytes_list[i][2:], 16)
      if hex_val >= 32 and hex_val <= 126:
        bytes_list[i] = chr(hex_val)
      else:
        bytes_list[i] = '\\' + bytes_list[i][1:]
    return ''.join(bytes_list)


  def update_seq_ack(self, packet, meta):
    """
    Stores SEQ and ACK numbers, and length of latest load in session metadata.
    
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet
    :param      meta:     Session metadata object
    :type       meta:     dict
    """
    meta['seq'] = int(packet[TCP].seq)
    meta['ack'] = int(packet[TCP].ack)
    if packet.haslayer(Raw):
      meta['len'] = len(packet[Raw].load)
    else:
      meta['len'] = 0


  def spam_fake_flags(self, category, response):
    """
    Spams random number of packets with a random number of fake flags each to
    sender. This is done if a real flag is detected in a genuine response,
    hopefully to confuse the other team.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      response:    TCP packet with ip/port flipped
    :type       response:    scapy.packet.Packet

    :returns:   Number of fake flags spammed
    :rtype:     integer
    """
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
      new_response = self.replenish_checksums(new_response)
      send(new_response)
    return num_spammed


  def run_reset_scripts(self, category, packet):
    """
    Run reset scripts from all current modules in memory. Return termination
    message if reset is requested.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet

    :returns:   Termination reason if session should reset, otherwise None
    :rtype:     string or None
    """
    meta = self.open_sessions[category]['metadata']
    # only look at other teams' attacks
    if (meta['action'] == self.defense):
      load_bytes = packet[Raw].load
      for name, module in self.modules.items():
        script = self.res.initialize_script(module)
        if self.service_name(script.service.id) == category.service:
          direction = self.get_direction(packet)
          should_reset = script.run(load_bytes, direction)
          if should_reset:
            return script.message()
    return None


  def check_for_timeout(self):
    """
    Check if too much time has elapsed between requests in a session or in the
    session overall. Terminate session if true.
    """
    current_time = self.timestamp()
    open_sessions = list(self.open_sessions.items())
    for category, session in open_sessions:
      meta = session['metadata']
      # only look at other teams' attacks
      if meta['action'] == self.defense:
        ip = IP(src=self.own_ip(), dst=meta['ip'])
        tcp = TCP(sport=meta['service port'], dport=meta['port'],
          seq=meta['ack'], ack=meta['seq'] + meta['len'])
        response = ip / tcp

        session_time = current_time - meta['first message']
        if session_time.seconds >= self.max_session_time:
          self.close_session(category, {
            'summary': 'TIMEOUT',
            'details': self.session_timeout_msg })
          self.send_reset(category, response)
        
        elif 'last message' in meta:
          message_time = current_time - meta['last message']
          if message_time.seconds >= self.max_time_between_messages:
            self.close_session(category, {
              'summary': 'TIMEOUT',
              'details': self.message_timeout_msg })
            self.send_reset(response)


  def close_session(self, category, reason):
    """
    Finalize session data and write to log file.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      reason:    Reason to terminate session
    :type       reason:    dict
    """
    session_log = self.session_log_path(category, reason)
    self.write_attack_log(category, reason, session_log)
    del self.open_sessions[category]


  def session_log_path(self, category, reason):
    """
    Get filename and path of log file using session metadata.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      reason:    Reason to terminate session
    :type       reason:    dict
    """
    meta = self.open_sessions[category]['metadata']
    is_attack = (meta['action'] == self.attack)
    service = category.service
    length = meta['n']
    result = reason['summary']
    bang = meta['flag']
    return self.res.session_log_path(
      is_attack, service, self.tick_num, length, result, bang)


  def write_attack_log(self, category, reason, filename):
    """
    Write details of a session out to a log file at the session's close.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      reason:    Reason to terminate session
    :type       reason:    dict
    :param      filename:  Log filename to write to
    :type       filename:  string
    """
    session = self.open_sessions[category]
    meta = session['metadata']
    comms = session['comms']
    n = 0
    with open(filename, 'a') as f:
      f.write('[METADATA]\n')

      start_time = self.time_format(meta['first message'])
      end_time = self.time_format(meta['last message'])
      diff_time = self.diff_minutes(
        meta['first message'], meta['last message'])
      if meta['flag']:
        f.write('  Flag-like string retrieved!\n\n')
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
          if msg['load'] != '\n' and msg['load'] != '\\x0a':
            f.write(' >>> [{0}]   {2}\n\n'.format(n, msg_time, msg_load))

        i += 1

      f.write('[EXIT]\n')
      f.write('Summary: ' + reason['summary'] + '\n')
      f.write('Details: ' + reason['details'] + '\n')


  def flip_packet(self, packet):
    """
    Edit a packet to prepare it to be sent back to the attacker.
    
    :param      category:  namedtuple uniquely identifying current session
    :type       category:  Category
    :param      packet:    TCP packet
    :type       packet:    scapy.packet.Packet

    :returns:   The intended response packet
    :rtype:     scapy.packet.Packet
    """
    packet = packet.copy()
    
    # swap ip addresses
    src_ip = packet[IP].src
    packet[IP].src = packet[IP].dst
    packet[IP].dst = src_ip

    # swap ports
    src_port = packet[TCP].sport
    packet[TCP].sport = packet[TCP].dport
    packet[TCP].dport = src_port

    # send correct sequence and ack
    seq = packet[TCP].seq
    packet[TCP].seq = packet[TCP].ack
    length = len(packet[Raw].load) if self.is_data(packet) else 0
    packet[TCP].ack = seq + length

    # replenish checksums
    packet = self.replenish_checksums(packet)

    return packet


  def replenish_checksums(self, packet):
    """
    Packet checksums need to be updated when the packet contents are updated.
    Scapy has no built-in way to do this, but if checksums are deleted, they could
    be remade by calling the constructor. Unfortunately, this causes a bug on the
    TCP payload and turns it into "Padding". This could be fixed by disassembling
    the packet before replenishing.
    
    :param      packet:  The packet
    :type       packet:  scapy.packet.Packet

    :returns:   The intended response packet
    :rtype:     scapy.packet.Packet
    """
    del packet[IP].chksum
    del packet[TCP].chksum
    tcp = packet[TCP].copy()
    packet.remove_payload()
    packet = packet.__class__(bytes(packet))
    tcp = tcp.__class__(bytes(tcp))
    packet /= tcp
    return packet


  def send_reset(self, response):
    """
    Send a reset flag back to attacker.
    
    :param      response:  TCP packet with ip/port flipped
    :type       response:  scapy.packet.Packet
    """
    response[TCP].flags = 'RA'
    response = self.replenish_checksums(response)
    send(response)


  def sniff(self):
    sniff(iface = 'tun0', filter = "tcp", prn = self.callback, store = False)


  