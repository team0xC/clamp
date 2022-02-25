#import swpag_client
from collections import namedtuple
from types import SimpleNamespace
import time


class GameClient:

  _game_url = '52.37.204.0'
  _flag_token_id = '5XOiDDskapSVTXw3tEoC'
  ServiceRecord = namedtuple('Service', ['name', 'id', 'port'])
  TeamRecord = namedtuple('Team', ['id', 'name', 'hostname'])

  def __init__(self):
    if self._game_url[:7] != 'http://':
      self._game_url = 'http://' + self._game_url
    self._init_service_list()
    self._init_team_hosts()
    self.start_time = int(time.time())

    self.team = SimpleNamespace()
    self.team.submit_flag = GameClient.submit_flag
    self.team.get_game_status = GameClient.get_game_status

  def _init_service_list(self):
    """
    Retrieves the list of services from swpag_client and stores them as a list
    of named tuples, e.g.

    self.services = {
      ServiceRecord("backup", 1, 10001),
      ServiceRecord("saywhat", 2, 10002),
      ...
    }
    """
    self.services = [
      self.ServiceRecord("backup", 1, 10001),
      self.ServiceRecord("saywhat", 2, 10002),
      self.ServiceRecord("flaskids", 3, 10003),
      self.ServiceRecord("sampleak", 4, 10004)
    ]
    

  def _init_team_hosts(self):
    """
    Retrieves the list of teams and hostnames from swpag_client and stores them
    as a list of named tuples, e.g.

    self.teams = {
      ...
      TeamRecord("0xC", 13, "team13"),
      ...
    }
    """
    t = [
      {'id': '1', 'name': 'D3bugZ0mbies'},
      {'id': '2', 'name': 'Scaramouche'},
      {'id': '3', 'name': 'PhlagPhishing'},
      {'id': '4', 'name': 'Team 4'},
      {'id': '5', 'name': 'ElectroBandits'},
      {'id': '6', 'name': 'ASCii PWners'},
      {'id': '7', 'name': 't34m7'},
      {'id': '8', 'name': 'lostpointers'}] 

    self.teams = []
    for team in t:
      hostname = 'team' + team['id']
      self.teams.append(self.TeamRecord(int(team['id']), team['name'], hostname))

  def service(self, identity):
    """
    Gets the ServiceRecord associated with any kind of identifying information
    related to services (either name, id or port number).
    
    :param      identity:  Service identifier (name, id or port number)
    :type       identity:  string (if name), else integer
    
    :returns:   ServiceRecord associated with matching service
    :rtype:     ServiceRecord (namedtuple)
    """
    if type(identity) == str:
      id_type = 0
    elif identity < 10:
      id_type = 1
    else:
      id_type = 2
    for service in self.services:
      if service[id_type] == identity:
        return service

  # more compact way of getting tick info
  def tick_info(self):
    tick_length = 100
    current_time = int(time.time())
    tick_num = (current_time - self.start_time) // tick_length
    seconds_left = tick_length - ((current_time - self.start_time) % tick_length)
    return (tick_num, seconds_left)

  def submit_flag(flags):
    results = []
    for flag in flags:
      if flag == 'FLGd5KDBXRcLh7KU':
        results.append('correct')
      else:
        results.append('incorrect')
    return results

  def get_game_status():

    return {'service_states': {
      '1': {
        '1': {'service_state': 'up'},
        '2': {'service_state': 'down'},
        '3': {'service_state': 'up'},
        '4': {'service_state': 'up'}
        },
      '2': {
        '1': {'service_state': 'up'},
        '2': {'service_state': 'up'},
        '3': {'service_state': 'up'},
        '4': {'service_state': 'up'}
      }
    }}

game_client = GameClient()
team = game_client.team