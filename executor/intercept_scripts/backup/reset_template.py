import string
from common import game_client

# This string will be used to instantiate the class.
class_name = 'SampleResetScript'

class SampleReseScript: 

  target_service = "simplecalc"

  def __init__(self):
    # Retrieve the ServiceRecord object to get service
    # (name, id, port)
    self.service = game_client.service(target_service)

  def __str__(self):
    # For reporting purposes
    return "Sample reset template"

  def message(self):
    """
    Reason for resetting TCP will be written at the bottom of the log files.
    """
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
    """
    Pattern match for text in the payload of a TCP request or response packet
    in order to check for something in the attack, or perhaps a flag in the
    response of an attack.

    :param      load:  Payload of a packet
    :type       identity:  string
    :param      direction:  Either "incoming" or "outgoing"
    :type       identity:  string
    
    :returns:   True if a reset flag should be sent back to source
    :rtype:     boolean
    """
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
