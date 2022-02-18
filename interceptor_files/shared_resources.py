import os
from types import SimpleNamespace

class SharedResources:

  def __init__(self, base_path='.'):
    if base_path[-1] == '/':
      base_path = base_path[:-1]
    self.paths = SimpleNamespace()
    self.paths.base = base_path
    self.paths.log = self.paths.base + '/interceptor_files/'    
    self.paths.sessions = self.paths.log + 'sessions/'
    self.paths.attack = self.paths.sessions + 'attacks_against_others/'
    self.paths.defense = self.paths.sessions + 'attacks_against_us/'
    self.paths.script_log = self.path.log + 'script_logs/'

    self.intercept_scripts_folder = 'intercept_scripts'
    self.exploit_scripts_folder = 'exploit_scripts'
    self.paths.reset_scripts = (self.paths.base + '/' + 
      self.intercept_scripts_folder + '/')
    self.paths.exploit_scripts = (self.paths.base + '/' + 
      self.exploit_scripts_folder + '/')
    self.paths.services = '/opt/ictf/services/'

    self.files = SimpleNamespace()
    self.files.real_tokens = self.paths.script_log + 'real_files.log'
    self.files.fake_tokens = self.paths.script_log + 'fake_files.log'
    self.files.fake_flags = self.paths.script_log + 'fake_flags.log'

    self._get_services() # self.paths.flag = {<service_name>: <path>}
    self.n_session_logs = 0


  def session_log_path(self, is_attack, service, tick, length, result, bang):
    path = self.paths.attack if is_attack else self.paths.defense
    path += service + '/' + str(tick) + '/'
    os.makedirs(path, exist_ok=True)

    file_id = "%.6d" % self.n_session_logs
    self.n_session_logs += 1
    comms_length = str(length)
    notice = '[FLG]' if bang else ''
    file = "{0}_{1}_{2}{3}.log".format(file_id, comms_length, result, notice)
    return path + file


  def update_scripts(self):
    # Gets only files as opposed to os.listdir
    files = lambda path: next(os.walk(directory))[2]
    self.exploit_scripts = files(self.paths.exploit_scripts)
    self.intercept_scripts = files(self.paths.intercept_scripts)


  def _get_services(self):
    self.service_names = next(os.walk(self.services))[1]
    self.paths.flag_dict = {}
    for service_name in self.service_names:
      service_base_path = self.paths.services + service_name
      append_path = service_base_path + '/append/'
      rw_path = service_base_path + '/rw/'
      if len(os.listdir(append_path)) > 0:
        self.paths.flag_dict[service_name] = append_path
      else:
        self.paths.flag_dict[service_name] = rw_path
