import os
import random

fake_flags = None

class FakeFlagsHoneypot:

  def __init__(self, resources):
    self.res = resources
    self.paths = resources.paths
    self.files = resources.files

    # Set of all filenames that have been processed
    self.seen_files = set()

    # Number of files in the flag directories per each service
    self.n_files = {service.name: 0 for service in self.res.services}
    
    # Loads processed files in memory from backup log
    self.load_data()

    # Number of fake files to create per real file
    self.ratio = 4


  def load_data(self):
    """
    Loads all processed files into memory from a backup log for in case
    the process is interrupted.
    """
    if os.path.isfile(self.files.seen_files):
      with open(self.files.seen_files, 'r') as f:
        for filename in f:
          filename = filename.strip()
          if len(filename) > 0:
            self.seen_files.add(filename)


  def update(self):
    """
    Look for increases in the number of files in flag directories per each 
    service. Identify newly created files and create fake files for each
    genuine file. Log each file processed.
    """
    new_real_files = False
    for service in self.res.services:
      directory = self.paths.flag_dict[service.name]
      files = next(os.walk(directory))[2]

      # New files detected
      if len(files) > self.n_files[service.name]:
        self.n_files[service.name] = len(files)

        # Find files with the valid format
        for file in files:
          file_parts = file.split('_')
          if len(file_parts) == 2:
            token = file_parts[0]
            file_parts = file_parts[1].split('.')
            flag = file_parts[0]
            suffix = '.'.join(file_parts[1:])
            if self.res.token_like_found(token) and self.res.flag_like_found(flag):

              if file not in self.seen_files:
                new_real_files = True
                self.write_real_token(token)
                self.write_real_flag(flag)

                # Find flag in file contents
                with open(directory + file, 'r') as f:
                  line = f.readline().rstrip('\n') 
                  if self.res.flag_like_found(line):
                    self.write_real_flag(line)
                  
                self.obscure(directory, token, suffix)
                self.n_files[service.name] += self.ratio
          
          if file not in self.seen_files:
            self.write_seen_file(file)
          self.seen_files.add(file)
    return new_real_files


  def obscure(self, directory, token, suffix):
    """
    Create fake flag files for given real file by a fake file ratio.
    Write a random number of fake flag strings into each file.
    Each file will have a filename of the same token, but a new randomly
    generated flag.
    
    :param      directory:  The flag directory
    :type       directory:  string
    :param      token:      The flag token to search
    :type       token:      string
    """
    for i in range(self.ratio):
      fake_file = self.fake_filename(token, suffix)
      contents = []
      for j in range(1,50):
        contents.append(self.res.create_random_flag())
      contents = ''.join(contents)
      with open(directory + fake_file, 'w') as f:
        f.write(contents)
      self.write_seen_file(fake_file)
      self.seen_files.add(fake_file)


  def fake_filename(self, token, suffix):
    """
    Create a fake file using given flag token and a randomly generated flag ID.
    
    :param      token:  The flag token retrieved from targets
    :type       token:  string
    
    :returns:   Filename of new fake file
    :rtype:     string
    """
    random_flag = self.res.create_random_flag()
    new_filename = lambda: token + '_' + random_flag
    filename = new_filename()
    while os.path.isfile(filename):
      filename = new_filename()
    if len(suffix) > 0:
      filename += '.' + suffix
    return filename


  def write_seen_file(self, filename):
    with open(self.files.seen_files, 'a') as f:
      f.write(filename + '\n')


  def write_real_token(self, token):
    with open(self.files.real_tokens, 'a') as f:
      f.write(token + '\n')


  def write_real_flag(self, flag):
    with open(self.files.real_flags, 'a') as f:
      f.write(flag + '\n')
