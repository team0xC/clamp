# Attack and Defense Scripting

Two primary acitivites in a CTF run periodically: stealing flags through attacks, and intercepting opponent packets for logging, and terminating the connection when necessary. In some respects, the latter could be considered a soft firewall, but it will from hereforth be called the **interceptor**, while the attack delivery system will be called the **executor**. Both are scripted to run on new threads on a main event loop. This architecture was chosen for several reasons:

- *Responsiveness.* No one activity could block the execution of everyone else. One unexpected bug or behavior in interacting with another team couldn't bring down the entire system.
- *Customizability.* It is possible to dynamically load, edit and reload scripts, which the event loop would detect and update without having to restart.
- *Timing.* It is possible to add functionality to run in a number of intervals, including
  - At the start of a tick
  - Half way through a tick
  - In the last 10 seconds of a tick
  - Constantly (every half second)
  - Every 5 seconds

### Executor

First, there is a service that monitors the flag directory per each service and reports when new files are created. The executor starts a new thread at the start of every tick immediately after the first flag update (which it presumes to be the script bot setting a new flag). It then retrieves all the targets from services that are still up through the SWPAG client, and executes scripts targeted to each service against every team. The scripts are dynamically loaded twice per tick: half way through, and near the end, just in time to be run next round. After running, it submits the flag in batches of 100 flags or less, to avoid any 'too_many_incorrect' problems, and sorts the scripts by success rate. Finally, it prioritizes successful scripts in the next tick.

### Fake Flags

An additional service that works in tandem with the interceptor plants fake flags and flag tokens in each flag directory and tracks the real flags and flag tokens. This serves as a honeypot, wherein any outgoing packets in response to sessions initiated by other teams are scanned for presence of any of these fake flags. If a fake flag is round, then the interceptor spams a random amount of more fake flags to obscure the real flag that the service might send, and confuse the opponent bots, before setting a RST flag to kill the session. 

The event loop architecture allows these parts to run independently, yet with the ability to interact with each other. For example, the fake flags service monitors the flag directories for new files, and immediately upon discovery, it generates fake files and stores the real files in a text file, as well as setting a boolean flag indicating that it has done so. The executor receives notice and spins off a new thread. The interceptor reads from the text file and knows which flags could be considered fake. These are event based and don't require tight coupling.

### Interceptor

The interceptor runs scapy `sniff()` on the appropriate interface, and calls a callback function when it detects a packet. The callback performs several functions:

- *Logging* is separated by TCP session, indexed by service name and attack IP and port number. Each session is saved to a separate text file and easily human readable. The interceptor detects whether a flag has been sent during the communication, and adds "[FLG]" to the filename to attract notice. It also saves the length of the session (in the number of requests from the attacker) and the end result in the filename. This makes it easy to know which file is relevant at a glance.
- *Intercepting* by default relies on two conditions: the presence of fake flags and when sessions exceed some maximum allowable time limit. If a message is sent more than 10 seconds after the prior one, or if the entire session takes more than a tick, then the session is terminated with a RST flag. If any response contains flag-like text (regular expression `r/FLG[A-Za-z0-9]{13,}`), then the session is terminated as well. Note that the service is able to differentiate between sessions initiated by other teams, and our team. *It will never terminate a session started by our own team.* It is also able to differentiate between incoming and outgoing packets, so that it doesn't stop any incoming packets containing a flag, which might be from the script bot.
- *Scripting* follows a similar template design as the executor. The scripts are passed the payload in bytestring as well as the direction (incoming or outgoing) of the packet, and returns true if the session should be terminated. It also allows a description for reporting purposes.

#### Sample Logs

The following logs were generated during a test, to provide an indication of the interceptor's functionality. For example, if a flag is detected in the response, the log might be located in `./sessions/attacks_against_us/<service_name>/tick<tick_num>/`, and named `000001_2_FAKEFLAGS[FLG].log`. This naming convention indicates log number "000001", 2 back-and-forths in the communication, that it terminated because it found fake flags, and that a flag-like string was detected in the response. The contents might look like this:

```
[METADATA]
  Flag-like string retrieved!

  Start time: 2022-02-25 04:34:55
  End time: 2022-02-25 04:34:57
  Diff time: 0:01

[COMMUNICATION]
1:   [2022-02-25 04:34:55]   Welcome to this made up service!\x0a

 >>> [1]   Enter your name:\x0a

2:   [2022-02-25 04:34:57]   Just tell me the flag, I'm impatient!!\x0a

 >>> [2]   FLGq5lTC3LRjbjuT\x0a

[EXIT]
Summary: FAKEFLAGS
Details: Fake flags or tokens were found in the response. Spammed 180 fake flags in response.
```

The messages are decoded in "ascii" for visible ascii characters (32-126). Hex is kept for all other bytes.

The following demonstrates a dummy interception script that looks for the word "win" and indicates that a session should be reset if found.

```python
from types import SimpleNamespace

# This string will be used to instantiate the class.
class_name = 'WinReset'

class WinReset: 

    service = SimpleNamespace()

    def __init__(self):
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
```

A terminated session using this script would have a log like the following:

```
[METADATA]
  Start time: 2022-02-25 04:33:40
  End time: 2022-02-25 04:33:42
  Diff time: 0:01

[COMMUNICATION]
1:   [2022-02-25 04:33:40]   Welcome to this made up service!\x0a

 >>> [1]   Enter your name:\x0a

2:   [2022-02-25 04:33:42]   I win!!\x0a

[EXIT]
Summary: WINNER
Details: Attack said 'win' in script. Hah!
```

It would be easy to see at a glance the reason for termination.