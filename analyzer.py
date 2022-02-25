# CSE545 - Team 12 (team0xC) 
# Analyzer module to Lookup Flags, Find Sessions, and Vulns in captured PCAP file.
# References: 
# [1] Rehim Rejah, Effective Python Penetration Testing, 1st edition, Packt Publishing, 2016
# [2] Mohit, Python Penetration Testing Essentials, 1st edition, Packt Publishing, 2015
    

import swpag_client
import sys
import getopt
import string
from scapy.all  import *
import re

# We have these information
# IP address of the scoreboard       (ScoreboardIP)
# IP address of the teaminterface    (myIP)
# Flag Token                         (myToken)

# My notes during PCTF:
# In CTF competition, time is our main challenge.
# Scapy didn't have enough performance to deal with real time traffic analysis.
# Scapy is very powerful and handy tool that can manipulate network traffic at a very low level and allow us to use protocol stack and combine them
# We used pyShark in our firewall module and we got better performance.
# I believed that if we capture traffic with pyShark and process them with Scapy, we can get better performance.
# Analyzer module must use a predefind dictionary of attack vector, and also it must be equiped an algorithm to detect new attasck vector and add them to dictionary.
# Analyzer must be able to gatther enough information from vulnerability to detect related CVE number or find suitable exploit from exploit-db.
# Analyzer module must use deep learning algoeithm to detect and fin vulnerability patterns in captured traffic. 



# General Functions
class ProjectPCTF:

    def __init__ (self, ip, token):
        self.Team = Team(myIP, myToken)


    #Return all service IDs during the PCTF
    def getServices(self):
        myServiceIDs = []
        myServices = self.Team.get_service_list()

        for s in myServices:
                myServiceIDs.append(s['service_id'])

                print("Service %s: %s\n\t'%s'" % (myServiceIDs['service_id'], myServiceIDs['service_name'], myServiceIDs['description'])
        
        return myServiceIDs

    #Return all targets (IPs, Ports, FlagIDs) for the given service ID
    def getTargets(self, Service)
        Targets = self.Team.get_targets(Service)

        for t in Targets:
            for key in ['hostname', 'port', 'flag_id', 'team_name')]:
                print("%20s : %s" % (key, t[key]))
            print("\n")
        
        return Targets

    # Find sessions with Specific Target
    def getSessions(Target):
        Pkts = rdpcap("PCAP_FILE_NAME.pcap")

        #Get Protocol SpurceIP:SourcePort > DestinationIP:DestinationPort 
        #as Follow TCP Stream in Wireshark
        
        foundSessions = Pkts.sessions.keys()

        # Output:  <PacketList: TCP:## UDP:## ICMP:## Other:##>
        # Make decision based on Output
        # Update DB


    # Serach for FLAG/FLAG ID
    def findFLG():
        # Serach for Flag/Flag ID depends on Format and Length
        match_regex = 'FLG[0-9A-Za-z]{13}'
        
        # Lookup match_regex in packet.payload 
        # If found: Submit FLAG and Update DB


    # Search for Flag in Network Traffic
    # We have a PCAP file from all network traffic that flows to scoreboard
    def getFlag():
        
        # Lookup in PCAP file
        scapy.sniff(offline="PCAP_FILE_NAME.pcap", store=True, filter="ip dst host ScoreboardIP", prn=ProjectPCTF.findFLG)

    
    # Strings, Sings and Symbols in Binaries:
    # Network Functions (bind_addr, bindport, recv@@GLIBC, bindtoip, setsocketopt@@GLIBC, server_waitclient, resolve, inet_addr@@GLIBC, bind@@GLIBC  ,socket@@GLIBC  ,getaddrinfo@@GLIBC  ,listen@@GLIBC,  connect@@GLIBC)
    # Backdoor Functions (backdoor_register_hooks, backdoor_post_read_request ,backdoor_log_transaction, ap_hook_post_config ,ap_hook_post_read_request, backdoor_post_config, ap_hook_log_transaction, reverseShell ,startProxy, shell, auth_pass, shellPTY)    
    # System Functions (mkdir@@GLIBC, , umount@@GLIBC, write@@GLIBC, rmdir@@GLIBC, mount@@GLIBC)
    # Process Functions(getpid@@GLIBC, execvr@@GLIBC, kill@@GLIBC, pthread_create, waitpid@@GLIBC, getppid@@GLIBC, exit@@GLIBC, forkpty@@GLIBC, for@@GLIBC)
    def findFun():
        pass    
    # If find update DB    

    # Lookup binaries in Network Traffic
    # We have a PCAP file from all network traffic flows to our VM / Source IP: myIP
    def findBinaries():
            scapy.sniff(offline="PCAP_FILE_NAME.pcap", store=True, filter="ip dst host ScoreboardIP", prn=ProjectPCTF.findFunc)

def main(argv):
    
    global myIP
    global myToken
    global ScoreboardIP
     
    ShortArgs = "myIP:myToken"

    try: 
        opts, args = getopt.getopt(argv, ShortArgs)
    except getopt.GetoptError:
        print('Usage: python3 analyzer.py myIP: xxxx.xxxx.xxxx.xxxx myToken xxxxxxxxxxxxxx')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-myIP"):
            myIP = arg
        elif opt in ("-myToken"):
            myToken = arg

    myCall = ProjectPCTF(myIP, myToken)
    myCall.getServices()
    myCall.getTargets()
    
    # Select of Target
    # myCall.getSession(Target)     

    #myCall.getFLG()
    #myCall.findBinaries()


if __name__ == "__main__":
    main(sys.argv[1:])
