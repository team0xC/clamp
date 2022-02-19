import os
import random

fake_flags = None

class FakeFlagsHoneypot:

  def __init__(self, resources):
    self.res = resources
    self.paths = resources.paths
    self.files = resources.files

    self.seen_files = set()
    self.n_files = {service.name: 0 for service in self.res.services}
    self.load_data()

    self.ratio = 5


  def load_data(self):
    if os.isfile(self.files.real_files):
      with open(self.files.real_files, 'r') as f:
        for filename in f:
          self.add_seen_file(filename)


  def update(self):
    for service in self.res.services:
      directory = self.paths.flag_dict[service.name]
      files = next(os.walk(directory))[2]
      if len(files) > self.n_files[service.name]:
        self.n_files[service.name] = len(files)
        for file in files:
          file_parts = file.split('_')
          if len(file_parts) != 2:
            continue
          token = file_parts[0]
          flag = file_parts[1]
          if self.res.token_like_found(token) and self.res.flag_like_found(flag):
            if file not in self.seen_files:
              self.add_seen_file(file)
              self.add_real_token(token)
              self.add_real_flag(flag)
              self.obscure(directory, token)


  def obscure(self, directory, token):
    for i in range(self.ratio):
      fake_file = self.fake_filename(token)
      contents = []
      for j in range(1,50):
        contents.append(self.random_flag())
      contents = ''.join(contents)
      with open(directory + fake_file, 'w') as f:
        f.write(contents)
      self.add_seen_file(fake_file)


  def fake_filename(self, token):
    random_flag = self.res.create_random_flag()
    new_filename = lambda: token + '_' + random_flag
    filename = new_filename()
    while os.isfile(filename):
      filename = new_filename()
    return filename


  def add_seen_file(self, filename):
    self.seen_files.add(filename)
    with open(self.files.seen_files, 'a') as f:
      f.write(filename + '\n')


  def add_real_token(self, token):
    with open(self.files.real_tokens, 'a') as f:
      f.write(token + '\n')


  def add_real_flag(self, flag):
    with open(self.files.real_flags, 'a') as f:
      f.write(flag + '\n')
