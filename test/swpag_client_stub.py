"""
Stub (with fake data) created from swpag-client 0.3.7,
using the formats provided in its docstrings.

NOTE: Formats for get_team_list() and get_team_service() 
methods were inferred from the iCTF framework Github. Use 
these methods at your own descretion.
-----------------------------------------------------------

Written by subwire and the iCTF team, 2019
# The TeamInterface game client

This client lets you interact with the game, including
getting the game status, obtaining a list of potential targets, and 
submitting flags.

To get started, you will have received a "flag token" with your game registration.
You may also need to know the URL of your game's "team interface".
Note that for some games (e.g., iCTF) this will be automatically discovered for you.
You will also need access to your team's virtual machine, on which you should run the client.

You are heavily encouraged to use this library to help you automate the exploitation of services
and the submission of flags.

You can now do the following:

>>> from teaminterface_client import Team
>>> t = Team("http://your.team.interface.hostname/", "your_flag_token_here")

With this team object, you can then get the info to login to your machine:

>>> t.get_vm()

Get game status information:

>>> t.get_game_status()

This includes information on scores, teams, services, and timing information regarding the game's "ticks".

Your first task will be to explore the game services which you must attack and defend, and find exploits
You will see them on your VM's filesystem, but to get a list of services with descriptions, you can run
>>> t.get_service_list()

This will produce a list of services, including the "service ID" of the service.

Once you have reverse-engineered a service, and developed your new leet exploit, you then need to
obtain a list of the other teams, which you can attack.
However, each service hosted by each team may contain multiple flags; in order to prove your 
control over the vulnerable service, you must find the _correct_ flag, which the game tells you to find.
Each flag is associated with a "flag ID", which gets cycled each game tick (see the game rules for
more details).  Your exploit needs to then obtain the flag associated with a given flag ID, hosted
hosted by a given opponent team.

With the service ID obtained above, you can then do the following:

>>> t.get_targets(service_id)

This will return a list of the teams' IP addresses, port numbers, and flag IDs.

Finally, you need to capture and submit some flags!
Once you've pwned the service, and captured the flag, all you need to do is:

>>> t.submit_flag("FLGxxxxxxxxxxxxx")

You can also submit a lot of flags at once:

>>> t.submit_flag(["FLGxxxxxxxxxxxxx", "FLGyyyyyyyyyyyyy", ...])

You'll get a status code (or a list of status codes) in return.

The client can provide a wealth of information on the game, which is discussed in the documentation.

Happy hacking!

- the iCTF team

"""
import random
from collections import namedtuple
import string
import re


rsa_key = """-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----"""


letters = string.ascii_uppercase = string.ascii_lowercase + string.digits

Service_ = namedtuple("Service_", "name description")
service_list = [
  Service_('to_the_moon', "Meme stock trading simulator"),
  Service_('kyc', "Blockchain login validator"),
  Service_('gopher_coin', "Submit Tweets to Crypto Bros Taking Ls"),
  Service_('swiss_keys', "Manage keypairs with Swiss Keys")]

Team_ = namedtuple("Team_", "name country url")
team_list = [
  Team_('0xC', 'US', 'https://team0xC.com/welcome'),
  Team_('gr00t', 'US', 'http://members.geocities.com/groot_sec'),
  Team_('medicine.jar', 'BR', 'https://letsgetahighscore.com')]

service_statuses = [
  ['up', 'up', 'up', 'up'], # Team 1 0xC
  ['up', 'up', 'down', 'untested'], #Team 2 gr00t
  ['down', 'down', 'up', 'up']] #Team 3 medicine.jar

exploited = [
  [1, 2], # Service 1 to_the_moon
  [], # Service 2 kyc
  [3], # Service 3 gopher_coin
  [3]] # Service 4 swiss_keys

First_Blood_ = namedtuple("First_Blood_", "timestamp team_id")
first_bloods = [
  First_Blood_('2022-02-15 12:46:23', 3),
  None,
  First_Blood_('2022-02-15 15:12:01', 1),
  First_Blood_('2022-02-15 14:05:57', 1)]

# Team 1 exploited Team 2's service 1, and Team 3's service 3
# Team 2 exploited Team 3's service 4
# Team 3 exploited Team 1's service 1 and Team 2's service 1
Score_Types_ = namedtuple("Score_Types_", "attack defense avail")
team_scores = [
  Score_Types_(75, 150, 100), # Team 1 0xC
  Score_Types_(50, 50, 50), # Team 2 gr00t
  Score_Types_(75, 0, 50)] # Team 3 medicine.jar


submitted_flags = set()


class Team(object):
  """
  This object represents a logged-in iCTF team.
  This object can be used to perform actions on behalf of the team, such as submitting game artifacts
  """

  def __init__(self, game_url, flag_token=None):
    self._flag_token = flag_token
    self._login_token = None
    self.game_url = game_url if game_url[-1] == '/' else game_url + '/'

  def __str__(self):
    return "<Team %s>" % self._flag_token

  def _get_flag_id(self, service_id):
    seed = 10000 + service_id
    random.seed(seed)
    while True:
      yield "".join(random.choice(letters) for _ in range(20))

  def _get_team_status(self, team_id):
    """
    Get your team's current status.
    """
    token = self._flag_token if self._flag_token else self._login_token
    if token:
      results = {str(team_id): {}}
      for i, service in enumerate(service_list):
        service_id = i + 1
        results[str(team_id)][str(service_id)] = {
          'service_name': service.name,
          'service_state': service_statuses[team_id - 1][i]
        }

      return results

    else:
      raise RuntimeError("An unknown error occurred getting the team status!")

  def _get_service_states(self):
    results = {}
    for team_id in range(1, len(team_list) + 1):
      results.update(self._get_team_status(team_id))
    return results

  def _get_team_dict(self):
    results = {}

    for i, team in enumerate(team_list):
      team_id = i + 1

      results[str(team_id)] = {
        'id': team_id,
        'name': team.name,
        'url': team.url,
        'country': team.country,
        'logo': ''
      }

    return results

  def _get_exploited_services(self):
    exploited_services = {}
    for i, service in enumerate(exploited):
      service_id = i + 1
      total_stolen = len(service)
      if total_stolen > 0:
        exploited_services[str(service_id)] = {
          'service_name': service_list[i].name,
          'teams': [],
          'total_stolen_flags': total_stolen
        }

      for team_id in service:
        team_name = team_list[team_id - 1].name
        exploited_services[str(service_id)]['teams'].append({
          'team_id': str(team_id),
          'team_name': team_name
        })
    return exploited_services

  def _get_first_bloods(self):
    results = {}
    for i, first_blood in enumerate(first_bloods):
      if first_blood is None:
        continue
      service_id = i + 1
      results[str(service_id)] = {      
        'created_on': first_blood.timestamp,
        'team_id': first_blood.team_id
      }
    return results

  def _get_scores(self):
    results = {}
    for i, scores in enumerate(team_scores):
      team_id = i + 1
      total = scores.attack + scores.defense + scores.avail
      results[str(team_id)] = {
        'attack_points': float(scores.attack),
        'service_points': float(scores.defense),
        'sla': float(scores.avail),
        'total_points': float(total)
      }
    return results

  def get_team_list(self):
    """
    Return the list of teams!
    """
    token = self._flag_token if self._flag_token else self._login_token
    if token:
      return list(self._get_team_dict().values())

    else:
      raise RuntimeError("An unknown error occurred getting the team list")

  def get_vm(self):
    """
    Return the vm info about your team, ip address and ssh keys.
    """
    token = self._flag_token if self._flag_token else self._login_token
    if token:
      return {
        'ip': '13.56.227.247',
        'team_id': '1',
        'ctf_key': '{0}'.format(rsa_key)
      }
    else:
      raise RuntimeError("An unknown error occurred getting the VM information for the team")

  def get_tick_info(self):
    """
    Return information about the current game "tick".

    The iCTF game is divided into rounds, called "ticks".  Scoring is computed at the end of each tick.
    New flags are set only at the next tick.

    If you're writing scripts or frontends, you should use this to figure out when to
    run them.

    The format looks like:
    {u'approximate_seconds_left': <int seconds>,
    u'created_on': Timestamp, like u'2015-12-02 12:28:03',
    u'tick_id': <int tick ID>}
    """
    token = self._flag_token if self._flag_token else self._login_token
    if token:
      return {
        'approximate_seconds_left': '180',
        'created_on': '2022-02-15 12:28:03',
        'tick_id': '42'
      }
    else:
      raise RuntimeError("An unknown error occurred getting the tick info.")

  def submit_flag(self, flags):
    """
    Submit a list of one or more flags
    note: Requires a flag token
    :param flags: A list of flags
    :return: List containing a response for each flag, either:
    	"correct" | "ownflag" (do you think this is defcon?)
                | "incorrect"
                | "alreadysubmitted"
                | "notactive",
                | "toomanyincorrect",

    """
    token = self._flag_token if self._flag_token else self._login_token
    if not isinstance(flags,list):
        raise TypeError("Flags should be in a list!")
    
    length = len(flags)
    num_incorrect = 0

    if token:
      results = []
      for flag in flags:
        if re.match(r'FLG[A-Za-z0-9]{13}', flag):
          if flag in submitted_flags:
            results.append("alreadysubmitted")
          else:
            results.append("correct")
            submitted_flags.add(flag)
        elif num_incorrect >= 100:
          results.append("toomanyincorrect")
        else:
          results.append("incorrect")
          num_incorrect += 1

      return results

    else:
      raise RuntimeError("An unknown error occurred submitting flags.")

  def get_targets(self, service):
    """
    Get a list of teams, their hostnames, and the currently valid flag_ids.
    Your exploit should then try to exploit each team, and steal the flag with the given ID.

    You can/should use this to write scripts to run your exploits!

    :param service: The name or ID of a service (see get_service_list() for IDs and names)
    :return: A list of targets:
      [
        {
          'team_name' : "Team name",
          'hostname' : "hostname",
          'port' : <int port number>,
          'flag_id' : "Flag ID to steal"
        },
        ...
      ]
    """
    token = self._flag_token if self._flag_token else self._login_token
    svc = None
    service_id = None
    services = self.get_service_list()
    if isinstance(service,str):
      selected_services = list(filter(lambda x: x['service_name'] == service, services))
    else:
      selected_services = list(filter(lambda x: int(x['service_id']) == service, services))
    
    if not selected_services:
      raise RuntimeError("Unknown service " + str(service))
    
    service_id = int(selected_services[0]['service_id'])
    port_num = "1000{0}".format(service_id) 

    if token:

      results = []
      flag_gen = self._get_flag_id(service_id)

      for selected_service in selected_services:
        team_id = int(selected_service['team_id'])
        if team_id == 1: # skip own flag
          continue
        team_name = team_list[team_id - 1].name
        hostname = "team" + str(team_id)

        results.append({
          'team_name': team_name,
          'hostname' : hostname,
          'port' : port_num,
          'flag_id': next(flag_gen)
        })

      return results

    else:
      raise RuntimeError("Something went wrong getting targets.")

  def get_service_list(self):
    """
    Returns the list of services, and some useful information about them.

    The output will look like:

    [
      {
        'service_id' : <int service id>,
        'team_id' : <team_id which created that service>
        'service_name' : "string service_name",
        'description' : "Description of the service",
        'flag_id_description' : "Description of the 'flag_id' in this service, indicating which flag you should steal",
        'port' : <int port number>
      }
    ]
    """
    token = self._flag_token if self._flag_token else self._login_token
    if token:
      results = []
      for i, service in enumerate(service_list):
        service_id = i + 1
        flag_gen = self._get_flag_id(service_id)
        for j, team in enumerate(team_list):
          team_id = j + 1

          results.append({
            'service_id': str(service_id),
            'team_id': str(team_id),
            'service_name': service.name,
            'description': service.description,
            'flag_id_description': next(flag_gen),
            'port': "1000{0}".format(service_id)
            })

      return results

    else:
      raise RuntimeError("An unknown error occurred getting the service list.")

  def get_game_status(self):
    """
    Return a dictionary containing game status information.
    This will include:
      - The scores of all teams
      - Game timing information
      - Information about services, including their status, number of exploitations, etc

    This API is suitable for use in the creation of frontends.

    The return value is a large dictionary, containing the following:
      - 'teams' : Basic team info, name, country, latitude, longitude, etc
      - 'service_states': For each team and service, provides its "state" (up/down/etc)
      - 'exploited_services': For each service that has been exploited, list who exploited it
      - 'first_bloods': For each service, which team scored on it first (they get extra points!)
      - 'scores': The scoring data for each team.
      - 'tick': Info about the game's current "tick" -- see get_tick_info()
    It will look something like:

    {
      'teams' :
        {
          <team_id> :
            {
              'country' : "ISO 2 letter country code",
              'logo' : <base64 logo>,
              'name' : "1338-offbyone"
              'url' : "http://teamurl.here"
            }
        }
      'exploited_services' :
        {
          <service_id> :
            {
              'service_name' : "string_service_name",
              'teams' :
                [
                  {
                    'team_id' : <team_id>,
                    'team_name' : "string team name"
                  },
                  ...
                ],
              'total_stolen_flags' : <integer>
            }
        }
      'service_states' :
        {
          <team_id> :
            {
              <service_id> :
                {
                  'service_name' : "string_service_name"
                  'service_state' : "untested" | "up" | "down"
                }
            }
        },
      'first_bloods' :
        {
          <service_id> :
            {
              'created_on' : Timestamp eg. '2015-12-02 10:57:49',
              'team_id' : <ID of exploiting team>
            }
        },
      'scores' :
        {
          <team_id> :
            {
              'attack_points' : <float number of points scored through exploitation>,
              'service_points' : <float number of points for having a "cool" service, see rules for details>,
              'sla' : <float SLA score>
              'total_points' : <float normalized final score>
            }
        },
      'tick' :
        {
          'approximate_seconds_left': <int seconds>,
          'created_on': Timestamp, like '2015-12-02 12:28:03',
          'tick_id': <int tick ID>
        }
    }

    """
    token = self._flag_token if self._flag_token else self._login_token
    if token:

      results = {
        'teams': self._get_team_dict(),

        'exploited_services': self._get_exploited_services(),

        'service_states': self._get_service_states(),

        'first_bloods': self._get_first_bloods(),

        'scores' : self._get_scores(),

        'tick': self.get_tick_info()
      }

      return results

    else:
      raise RuntimeError("An unknown error occurred contacting the game status! Perhaps try again?")

  def get_team_status(self):
    """
    Get your team's current status.
    NOTE: There is no certain example for the output of this method.
    """
    return self._get_team_status(1)
