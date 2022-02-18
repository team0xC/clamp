import os

def create(team):
  """
  Creates private key file, sets appropriate permissions, then creates 
  bash script with the command that logs onto server.
  
  :param      team:  instance of Team object from swpag_client
  :type       team:  Team
  :returns    IP address of the SSH server
  :rtype      string
  """

  virtual_machine = team.get_vm()
  private_key = virtual_machine['ctf_key']
  address = virtual_machine['ip']

  key_file = 'deploy/ctf.key'
  script_file = 'ssh.sh'

  if not os.path.isfile(key_file):
    with open(key_file, 'w') as file:
      file.write(private_key)
      os.chmod(key_file, 0o600)

  command = "ssh -i deploy/{0} ctf@{1}\n".format(key_file, address)
  if not os.path.isfile(script_file):
    with open(script_file, 'w') as file:
      file.write(command)
      
  return address