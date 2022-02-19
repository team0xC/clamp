import string
from common import game_client

class_name = 'SampleResetScript'

class SampleReseScript: 

  target_service = "simplecalc"

  def __init__(self):
    self.service = game_client.service(target_service)

  def __str__(self):
    return "Sample reset template"

  # Return: Reason for resetting TCP will be written at the bottom of
  #         the log files.
  def message(self):
    msg = {}
    msg['summary'] = 'INVALID REGISTERS'
    msg['details'] = "Script contains in valid register formatting."
    return msg

  # Arguments:
  #   load      -- the load of the packet
  #   direction -- either "outgoing" or "incoming" 
  #   (our team's attack scripts are ignored and will never be reset)
  # Return: True to reset TCP, False for no action
  def run(self, load, direction):
    # Assume simplecalc
    if '[]' in load:
      return True
    for i in range(len(load) - 1):
      if load[i] == 'V':
        if load[i+1] == '1' and i < len(load) - 2:
          if load[i+2] not in '0123456789 =':
            return True
        elif load[i+1] not in string.digits:
          return True
    return False
