# Makes encrypted copies of files in the path that conform to the filename format:
# %s_%s
# This allows users to access previously unencrypted files via the encrypted copy

import os
myPath = ""
split_char = '_'

"""
vvv() encrypts/decrypts

DESIGN CRITERIA:
1) Alphanumeric only (to limit errors when used in other programs)
2) Requires a user provided key to encrypt/decrypt (which is not stored or known by the server)
3) Output is identical in length to input (to limit errors when used in other programs)
4) A single character change in the string to be encrypted causes a domino effect
5) A single character change in the key causes a domino effect
6) The same function can be used to decrypt and encrypt
7) Even if the algorithm is known, it is impractical to attempt decryption because the key is required
8) Minimum size that meets the criteria

HOW IT IS USED:
It is assumed that there are 3 pieces of information.
-Username (provided by user)
-Password (provided by user)
-Contents (sent to user)
The goal is to make it so all of these pieces of information are known only by the user, and are unknown by the server or any malicious party.
The function that writes username, password and contents to file should be modified as well as the one for retrieval.

This is done by taking the following steps:
username2file = vvv(username, password)
password2file = vvv(password, username)
contents2file = vvv(contents, password)

The same process can be used for retrieval:
username2match = vvv(username, password)
password2match = vvv(password, username)
contents2send  = vvv(contents, password)

A false flag can also be planted for each flagID:
Filename: username_randomstring
Contents: FLGrandomstring

It may also be ideal to delete or overwrite the contents of old files.

HOW IT WORKS:
Encrypts iterating one character at a time
Encodes character as an integer representation of alphanumeric
If not alphanumeric then no change
Determines an offset value based on index, reflector pair, previous advance, and key
Advances the Ceasar rotor by the offset
Sends the input through the Ceasar rotor
Uses a mirror reflector
Sends the input through the Ceasar rotor in the reverse direction
Encodes the character as ASCII
Adds to string
Returns string

"Veni, vidi, vexi"
    -Some guy abusing Latin

:param un: string to be encrypted
:param pw: string to be used as key
:return: returns encrypted string
"""

def vvv(un,pw):
    pw_l, out, adv, pair_i = len(pw), '', 0, 0
    for i in range(len(un)):
        un_ord, ani = ord(un[i]), -1 
        ani = 48 if 48 <= un_ord <= 57 else 55 if 65 <= un_ord <= 90 else 61 if 97 <= un_ord <= 122 else ani
        if ani >= 0:
            adv = (i + pair_i + adv + ord(pw[adv%pw_l]))%99
            un_ord = (un_ord - ani + adv)%62     
            pair_i = abs(un_ord + un_ord - 61)
            un_ord = (185 - un_ord - adv)%62 
            un_ord += 48 if un_ord <= 9 else 55 if un_ord <= 35 else 61
        out += chr(un_ord)
    return out

def vvv_test():
    un = "h4ck3r0n5t3r01d5"
    pw = "t3hpvv4n1d10tvv0u1du530nh151u6646310ck"
    cont = "0123456789.ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz!@#$%^&*()"

    e_un = vvv(un,pw) 
    e_pw = vvv(pw,un)
    e_cont = vvv(cont,pw)

    print("\nFilename: " + e_un + '_' + e_pw)
    print("Encrypted Contents: " + e_cont + '\n')
    print("Retrieve from file:")
    if e_un == vvv(un,pw):
        if e_pw == vvv(pw,un):
            print("Decrypted Contents: " + vvv(e_cont,pw))

    print(vvv(e_un,e_pw))
    print(vvv(e_pw,e_un))

def vvv_encrypt_files():
    num_files = 0
    file_list = next(os.walk(myPath))[2]
    for file in file_list:
        unpw = file.split(split_char)
        if len(unpw) == 2:
            un = unpw[0]
            pw = unpw[1]
            file1 = open(myPath+file, "r")
            cont = file1.read()
            file1.close()
            e_un = vvv(un,pw)
            e_pw = vvv(pw,un)
            e_cont = vvv(cont,pw)
            file2 = open(myPath + e_un + '_' + e_pw, "w")
            file2.write(e_cont)
            file2.close()
            num_files += 1

    print("Created " + str(num_files) + " files.")

def main():
    vvv_test()
    vvv_encrypt_files()

if __name__ == "__main__":
    main()