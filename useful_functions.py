from python_hosts import Hosts

def team_hostnames():
  """
  Queries /etc/hosts for information about the other teams.
  
  :returns:   Map of hostname : ip-address
  :rtype:     Dict
  """
  teams = {}
  for entry in Host().entries:
    if entry.entry_type == 'ipv4' and entry.names[0] != 'localhost':
      teams[entry.names[0]] = entry.address
  return teams
