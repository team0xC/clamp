"""
This module initializes the game client and ssh into the game URL with 
credentials. It should also provide commonly used functions in a centralized
location. The GameClient class is instantiated once as a singleton (there is
no need to initialize and query the swpag_client or log in and log out of ssh
unnecessarily).

Using a context manager the class should handle establishing the ssh 
connection, and closing when there's an error.

Properties:
  client.config         dict          environment variables
  client.team_id        int           our team id
  client.teams          dict          map of hostname to ip address per team
  client.services_dir   str           directory to services
  client.<SWPAG funcs>  func          all swpag_client.Team methods work
                                      directly on client

Usage:
  from game_client import client

  with client:
    for service in client.team.get_service_list():
      if service['team_id'] != client.team_id: # we don't need our own flag!
        stdin, stdout, stderr = client.exec('nc {0} {1}').format(
          service['team_id'], service['port'])
    stdin, stdout, stderr = client.exec('ls -la ' + client.services_dir)
    print(stdout.read())

"""

import os
import contextlib
import swpag_client
import paramiko
from dotenv import dotenv_values
from python_hosts import Hosts


class GameClient(contextlib.ExitStack, swpag_client.Team):

  def __init__(self):
    self.config = dotenv_values('.env')

    contextlib.ExitStack.__init__()
    swpag_client.Team.__init__(
      config['GAME_URL'],
      config['FLAG_TOKEN'])

    self.vm = self.get_vm()
    self.team_id = self.vm['team_id']
    self.teams = None 

    self.ssh_username = 'ctf'
    self.ssh_key = self._create_ssh_key()
    self.client = None # Will be created by context manager

    self.services_dir = '/opt/ictf/services/'


  def __enter__(self):
    contextlib.ExitStack.__enter__()
    if self.client is None:
      try:
        self.client = self.enter_context(paramiko.SSHClient())
        self._connect_to_ssh(self.client)
      except:
        if not self.__exit__(*sys.exc_info()):
          raise

    return self


  def __exit__(self, exc_type, exc_value, traceback):
    contextlib.ExitStack.__exit__()
    if exc_type is not None:
      self.client.close()
      self.client = None


  def _create_ssh_key(self):
    key_file = self.config['KEY_FILE']
    private_key = self.vm['ctf_key']
    if not os.path.isfile(key_file):
      with open(key_file, 'w') as file:
        file.write(private_key)
        os.chmod(key_file, 0o600)
  
    ssh_key = paramiko.RSAKey.from_private_key_file(key_file)
    return ssh_key


  def _connect_to_ssh(self, ssh_client):
    ssh_ip = self.vm['ip']
    ssh_client.connect(ssh_ip, 
      username=self.ssh_username, 
      pkey=self.ssh_key)


  def _get_team_addresses(self, hosts):
    self.teams = {}
    for entry in hosts.entries:
      if entry.entry_type == 'ipv4' and entry.names[0] != 'localhost':
        self.teams[entry.names[0]] = entry.address


  def exec(self, command):
    stdin, stdout, stderr = self.client.exec_command(command)
    return stdin, stdout, stderr



client = GameClient()

with client:
  hosts = Hosts(hosts_path='/etc/hosts')
  client._get_team_addresses(hosts)