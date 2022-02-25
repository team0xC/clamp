import os
from common_stub import game_client
from interceptor_files.shared_resources import SharedResources

def random_filename(res):
  token = res.create_random_token()
  flag = res.create_random_flag()
  new_file = lambda: token + '_' + flag + '.secure.bak'
  filename = new_file()
  while os.path.isfile(filename):
    filename = new_file()
  return filename

def create_file(directory, filename):
  full = directory + filename
  with open(full, 'a') as f:
    print("real file: " + full)
    f.write(res.create_random_flag())

if __name__ == '__main__':
  res = SharedResources(os.getcwd())
  res.set_services(game_client.services)
  for service in res.services:
    directory = res.paths.flag_dict[service.name]

    # Create two flags per service
    for i in range(2):
      create_file(directory, random_filename(res))
