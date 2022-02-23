import os
from types import SimpleNamespace
import importlib
import string
import re

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
    self.paths.script_log = self.paths.log + 'script_logs/'

    self.intercept_scripts_folder = 'intercept_scripts'
    self.exploit_scripts_folder = 'exploit_scripts'
    self.paths.reset_scripts = (self.paths.base + '/' + 
      self.intercept_scripts_folder + '/')
    self.paths.exploit_scripts = (self.paths.base + '/' + 
      self.exploit_scripts_folder + '/')
    self.paths.services = '/opt/ictf/services/'

    self.files = SimpleNamespace()
    self.files.real_tokens = self.paths.script_log + 'real_tokens.log'
    self.files.fake_tokens = self.paths.script_log + 'fake_tokens.log'
    self.files.fake_flags = self.paths.script_log + 'fake_flags.log'
    self.files.real_flags = self.paths.script_log + 'real_flags.log'
    self.files.seen_files = self.paths.script_log + 'seen_files.log'

    self.token_chars = string.ascii_lowercase + string.digits
    self.flag_chars = self.token_chars + string.ascii_uppercase

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


  def read_script_files(self, script_path):
    # Gets only files as opposed to os.listdir
    files = next(os.walk(script_path))[2]
    for i in range(len(files)):
      if files[i][-3:] == '.py':
        files[i] = files[i][:-3]
    return files


  def reload_scripts(self, package_name, script_files, modules):
    for file in script_files:
      module_path = package_name + '.' + file

      # Check if exploit has previously been imported, dynamically reload if so
      if file not in modules:
        modules[file] = importlib.import_module(module_path)
      else:
        modules[file] = importlib.reload(modules[file])
    return modules


  def initialize_script(self, module):
    class_name = module.class_name
    script_obj = getattr(module, class_name)
    return script_obj()


  def set_services(self, services):
    self.services = services
    self.paths.flag_dict = {}
    for service in self.services:
      service_base_path = self.paths.services + service.name + '/service'
      append_path = service_base_path + '/append/'
      rw_path = service_base_path + '/rw/'
      if len(os.listdir(append_path)) > 0:
        self.paths.flag_dict[service.name] = append_path
      else:
        self.paths.flag_dict[service.name] = rw_path


  def create_random_token(self):
    return ''.join(random.choices(self.token_chars, k=20))


  def create_random_flag(self):
    return 'FLG' + ''.join(random.choices(self.flag_chars, k=13))


  # returns iteration object
  def detect_flag_like(self, load):
    regexp = r'FLG[A-Za-z0-9]{13}'
    return re.finditer(regexp, load)


  def detect_token_like(self, load):
    regexp = r'[a-z0-9]{20}'
    return re.finditer(regexp, load)


  def flag_like_found(self, load):
    flag_found = None
    for match in self.detect_flag_like(load):
      flag_found = match.group()
      break
    return flag_found is not None


  def token_like_found(self, load):
    token_found = None
    for match in self.detect_token_like(load):
      token_found = match.group()
      break
    return token_found is not None