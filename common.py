import swpag_client
from collections import namedtuple

_game_url = '52.37.204.0'
_flag_token_id = '5XOiDDskapSVTXw3tEoC'
ServiceRecord = namedtuple('Service', ['name', 'id', 'port'])
TeamRecord = namedtuple('Team', ['id', 'name', 'hostname'])

game_client = None
team = None

class GameClient:

  def __init__(self):
    if _game_url[:7] != 'http://':
      _game_url = 'http://' + _game_url
    self.team = swpag_client.Team(_game_url, _flag_token_id)
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
        self.services.append(ServiceRecord(name, id_num, port))

  def _init_team_hosts(self):
    self.teams = []
    for team in self.team.get_team_list():
      hostname = 'team' + team['id']
      self.teams.append(TeamRecord(team['id'], team['name'], hostname))

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


if __name__ == '__main__':
  game_client = GameClient()
  team = game_client.team