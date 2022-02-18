#decryption test
from vvv import * #runs copy script
import os

flags = 0
na = 0
original_flags = []

file_list = next(os.walk(myPath))[2]

for file in file_list:
    unpw = file.split(split_char)
    if len(unpw) == 2:
        un = unpw[0]
        pw = unpw[1]
        e_un = vvv(un,pw)
        e_pw = vvv(pw,un)
        #check for encrypted un/pw
        if (e_un + split_char + e_pw) in file_list:
            file1 = open(myPath+e_un + split_char + e_pw, "r")
            #get the contents
            e_cont = file1.read()
            file1.close() 
            #decrypt contents
            d_cont = vvv(e_cont,pw)
            #print flag
            print(d_cont.split('\n')[0])
            flags += 1
        
            #normal login info, unencrypted plaintext
            file2 = open(myPath + file, "r")
            o_cont = file2.read()
            file2.close() 
            print(o_cont.split('\n')[0])
        else:
            na += 1
    
print("Flags: " + str(flags))
print("Invalid Login: " + str(na))