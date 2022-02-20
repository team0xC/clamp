import swpag_client
from collections import namedtuple


class GameClient:

  _game_url = '52.37.204.0'
  _flag_token_id = '5XOiDDskapSVTXw3tEoC'
  ServiceRecord = namedtuple('Service', ['name', 'id', 'port'])
  TeamRecord = namedtuple('Team', ['id', 'name', 'hostname'])

  def __init__(self):
    if self._game_url[:7] != 'http://':
      self._game_url = 'http://' + self._game_url
    self.team = swpag_client.Team(self._game_url, self._flag_token_id)
    self._init_service_list()
    self._init_team_hosts()

  def _init_service_list(self):
    self.services = []
    unique_services = set()
    for service in self.team.get_service_list():
      name = service['service_name']
      id_num = int(service['service_id'])
      port = int(service['port'])
      if name not in unique_services:
        unique_services.add(name)
        self.services.append(self.ServiceRecord(name, id_num, port))

  def _init_team_hosts(self):
    self.teams = []
    for team in self.team.get_team_list():
      hostname = 'team' + team['id']
      self.teams.append(self.TeamRecord(team['id'], team['name'], hostname))

  def service(self, identity):
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
    team.get_tick_info()
    tick_num = int(tick_info['tick_id'])
    seconds_left = int(tick_info['approximate_seconds_left'])
    return (tick_num, seconds_left)

game_client = GameClient()
team = game_client.team