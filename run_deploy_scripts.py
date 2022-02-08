from argparse import ArgumentParser
from test import swpag_client_stub as swpag_client
from deploy import create_ssh_script

def _decode(arg):
  return arg.encode('ascii', 'ignore').decode()


def handle_args():
  parser = ArgumentParser(prog="reflector",
  description='Reflects attacks over network back to source.')

  parser.add_argument('game_url', help='URL or IP address of the virtual machine')
  parser.add_argument('flag_token', help='Token string to log into virtual machine')

  args = parser.parse_args()
  config = {
    'game url': _decode(args.game_url),
    'flag token': _decode(args.flag_token)
  }

  return config


if __name__ == '__main__':

  config = handle_args()

  team = swpag_client.Team(
        config['game url'],
        config['flag token'])

  ip_address = create_ssh_script.create(team)