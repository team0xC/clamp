from types import SimpleNamespace

# This string will be used to instantiate the class.
class_name = 'WinReset'

class WinReset: 

    service = SimpleNamespace()

    def __init__(self):
        # Retrieve the ServiceRecord object to get service
        # (name, id, port)
        self.service.id = 1
        print(str(self))

    def __str__(self):
        # For reporting purposes
        return "Winner reset"

    def message(self):
        """
        Reason for resetting TCP will be written at the bottom of the log files.
        """
        msg = {}
        msg['summary'] = 'WINNER'
        msg['details'] = "Attack said 'win' in script. Hah!"
        return msg

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
        return 'win' in load.decode('latin1')
