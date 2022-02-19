import time
import os 
from common import game_client, team
import importlib
import math
# import models


class Executor:

  def __init__(self, resources):
    self.res = resources
    self.paths = resources.paths
    self.files = resources.files

    self.modules = {}
    self.successes = {}
    self.current_tick = -1


  def load_exploits(self):
    files = self.res.read_script_files(self.paths.exploit_scripts)
    self.modules = self.res.reload_scripts(
      self.exploit_scripts_folder, files, self.modules)
    for name in files:
      if name not in successes:
        self.successes[name] = 0

      # self.add_exploit_to_db(name)


  def run_all_exploits(self):
    # e.g. {<service_id>: [<team_id>, ...], ...}
    target_services = services_up()

    # Q: Why exploit then team?; A: Allows us to stop running exploits when flag captured if you want to hide exploits
    # Alternatively, queue exploits for each team, don't fix what isn't broken and only change exploits for a given team (and only that team) if it stops working

    # process exploit with most successes first
    exploit_list = self.sort_exploits(self.successes) 
    for name in exploit_list:
      module = self.modules[name]
      exploit = self.res.initialize_script(module)
      flags = []
      target_team_ids = target_services[exploit.service.id]
      for team_id in target_team_ids:
        hostname = 'team' + str(team_id)
        try:
          print(str(exploit) + ' against ' + hostname)
          new_flags = exploit.run(hostname)
          if type(new_flags) == str:
              new_flags = [new_flags]
          flags.extend(new_flags)

        except Exception as e:
          print(e)

      batches = math.ceil(len(flags) / 100)
      for i in range(batches):
        submission = flags[i * 100:(i + 1) * 100]
        results = team.submit_flag(flags)
        self.successes[exploit_name] += self.count_correct(results)


  # Create dictionary of {<service_id>: [<team_id>, ...]...}
  # of all the services that are still up
  def services_up(self):
    service_list = {}
    team_services = team.get_game_status()['service_states']
    for team_id, services in team_services.items():
      for service_id, service in services.items():
        if service['service_state'] == 'up':
          team_id = int(team_id)
          service_id = int(service_id)
          if service_id in service_list:
            service_list[service_id].append(team_id)
          else:
            service_list[service_id] = [team_id]
      return service_list

  # Sort exploits by number of successes achieved
  def sort_exploits(self):
    exploit_list = list(self.successes.items())
    exploit_list.sort(key=lambda x: x[1], reverse=True)
    return exploit_list


  # add new modules to database
  def add_exploit_to_db(self, exploit_name):
    engine = models.get_db_engine()
    Session = models.get_db_session(engine)
    Exploit = models.Exploit
    rebuild_path = lambda name: self.paths.exploit_scripts + name + '.py'
    exploit_fullpath = rebuild_path(exploit_name)
    with Session() as session:
      with session.begin():
        if not session.query(Exploit.query.filter(
          Exploit.path == exploit_fullpath).exists()
          ).scalar():

          module = self.modules[exploit_name]
          exploit_obj = self.res.initialize_script(module)
          new_exploit = Exploit(
            path = exploit_fullpath,
            service_id = exploit_obj.service.id)
          session.add(new_exploit)

  # Count number of correct values returned after submitting flags
  def count_correct(self, lst):
    count = 0
    for value in lst:
      if value == 'correct':
        count += 1
    return count
