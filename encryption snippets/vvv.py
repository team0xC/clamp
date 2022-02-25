import os
myPath = "opt/ictf/services"
split_char = '_'

"""
    vvv() takes an input string and a key string as arguments, and returns an encrypted/decrypted string

    DESIGN CRITERIA:
        Cryptographic - 
            1) Requires a user provided key to encrypt/decrypt (which is not stored or known by the server) 
            2) Difficult to detect pattern (no obvious cipher of known substrings like "FLG")
            3) A single character change in the string to be encrypted causes a domino effect (no obvious ciphered "FLG")
            4) A single character change in the key causes a domino effect 
            5) Even if the algorithm is known, it is impractical to attempt decryption because the key is required
        String -
            6) String of arbitrary length as key
            7) Alphanumeric encryption only (to limit errors when used in other programs)
            8) Does not alter nonalphanumeric characters (in case they are used by the program)
            9) Output is identical in length to input (to limit errors when used in other programs)
        Patching - 
            10) The same function can be used to decrypt and encrypt
            11) Standardized behavior between languages in case services interact
            12) Require minimum external libraries
            13) Minimum size that meets the criteria (13 lines of code)

    HOW IT IS USED:
    It is assumed that there are 3 pieces of information, which are sufficiently random other than the "FLG" prefix.
        -Username (provided by user)
        -Password (provided by user)
        -Contents (returned to user)
    The goal is to make it so all of these pieces of information are known only by the user, and are unknown by the server or an attacker.

    This encryption should be used in a way that ensures confideniality/integrity/availability:
        Confidentiality - The identifying data and the confidential data is only ever saved encrypted
        Integrity - Integrity is preserved because it can be decrypted and strlen and non-alphanumeric chr are constant
        Availability - Unencrypted data is available when a key is present, so it does not adversely affect availability

    Service/server:
    The function that writes username, password and contents to file should be modified as well as the one for retrieval.
    The server never stores information as plaintext, and never saves any way to decrypt the files.
    Technically a hash may be used for Username/Password because these will always be provided by the bot, and only need to be verified.

    Hacker POV:
    The hacker only knows the unencrypted flagID and at best only only has access to encrypted data.
    The hacker will not even be able to identify the encrypted flagID because the encryption key is the unknown password.
    The hacker will have to spend time studying a non-standard encryption method.
    The hacker will have to expend a limited resource (time) on cracking encryption rather than other exploits with higher ROI.
    
    This provides another line of defense on top of the standard exploit patching, and resists standard exploits that rely on plaintext.
    This can be prepared in advance without knowing specific vulnerabilities, because it tackles the general problem of plaintext.   

Fig 1. Because the flagIDs are encrypted the files can not be found by flagID
          ^ ^
    __   ('w')~ meow.gif __________
   /  \ <(cat flagID)   |  ______  | ('where is flagID??')  wSfnFc_QM9u5.bak [MeleW]
 _|,  ,|_               | |SERVER| | ,'                     3dw4Rd_WhPt4.bak [b3B0p]
|  l33t  |              | |______| |                        Db173h_d744s.bak [W75nk]
 (hacker)    ('huh?')>  |__________|                        ip2Bd3_fmut3.bak [61T5x]       
                           ======                           

Fig 2. Even if the hacker gets access to flags, they can not be mass submitted because they are encrypted
          ^ ^
    __   ( *~)           __________
   /  \ <(cat *)        |  ______  |                        wSfnFc_QM9u5.bak [MeleW]
 _|,  ,|_    (MeleW)    | |SERVER| |                        3dw4Rd_WhPt4.bak [b3B0p]
|  l33t  |   (b3B0p)    | |______| |                        Db173h_d744s.bak [W75nk]
 (hacker)    (W75nk)>   |__________|                        ip2Bd3_fmut3.bak [61T5x]                         
             (6175s)       ======                           

Fig 3. Even if the hacker has full shell access and can see what we see, s/he still won't know what the flag is...
because the server doesn't know and neither do we! 
Neither the unencrypted flag or flagID is on the server, nor is the key to unencrypt them
    __                   __________      __   (wut??)
   /  \ <(shell)        |  ______  |    /  \ ,'             wSfnFc_QM9u5.bak [MeleW]                    
 _|,  ,|_               | |SERVER| |  _|,  ,|_              3dw4Rd_WhPt4.bak [b3B0p]  (i dunno either)> [un:admin]
|  l33t  |              | |______| | |  l33t  |             Db173h_d744s.bak [W75nk]                    [pw:admin]
 (hacker)               |__________| (hacker in the shell)  ip2Bd3_fmut3.bak [61T5x]                   (the $ADMIN$)
                           ======                           

Fig 4. Only the flag bot with both the unencrypted flagID and pw can access the file.
The server only verifies the login info against the encrypted login info and has the key to decrypt the contents.

TT,.-=*^^-._. <(flagID)  __________  
|| FLAG BOT/   (FLGpw)  |  ______  | (vvv(flagID,FLGpw)->)  wSfnFc_QM9u5.bak [MeleW]                    
||BEEP BOOP|            | |  \/  | | ,'                     3dw4Rd_WhPt4.bak [b3B0p]  
||.-=*^^-.__\  (FLGfl)> | |__/\__| | (<-vvv(MeleW,FLGpw))   Db173h_d744s.bak [w75nk]             
||                      |__________| ~'                     ip2Bd3_fmut3.bak [61T5x]
      ~*¡CORRECT!*~        ======                           

    The function can be used to encrypt all data, such as passwords, usernames and file contents.
    All of these 3 strings can be encrypted or used as a key without any major alterations to the serivce.

    A false flag can also be planted for each flagID:
        Filename: flagID_randomstring
        Contents: FLGrandomstring

    It may also be ideal to delete or overwrite the contents of old files.

    The initial values for adv, pair_i and the advance rotor modulo can be altered to produce different results. 
    Additional rotors may be added, or rotors may be removed, at the risk of compromizing certain characteristics.

    HOW IT WORKS:
    Encrypts iterating one character at a time                                      (un_ord: ordinal username; char as int)
    Encodes character as an integer representation of alphanumeric                  (ani: alphanumeric index offset; -1 is non-alnum flag)
    If not alphanumeric then no change                                              (un_ord: ordinal username)
    Key is translated into 2 sub-rotors to produc up to n^2 unique offsets          (pw[i%pw_l]; pw[adv%pw_l])
    Key rotor #1 stepped by increment to promote domino effect                      (pw[i%pw_l]: key rotor stepped by increment) 
    Key Rotor #2 is used as a rotor stepped by prev adv to be affected by other var (pw[adv%pw_l]: key rotor stepped by prev advance)
    Index causes an advance to promote change with each character                   (i: index of input string character)
    Index of the matched pair from the mirror reflector to promote domino effect    (pair_i: index of matched character pair) 
    Previous advance is also used so that all previous variable have aftereffects   (adv: prior advance value before reassignment)                                              
    Advances the Caesar rotor by the offset, modulo is used to emulate rotation     (...+adv)%62: 62 alnum vals; 1-to-1 & onto func)
    Sends the input through the Caesar rotor                                        (un_ord-ani+adv: un_ord+ani is an alnum index)
    Uses a mirror reflector to make it involutory                                   ((185-un_ord...)%62: unordered tuples{(0,61),(1,60)...})
    Gets the a unique value for the unordered tuple for advance offset              (abs(un_ord+un_ord-61): pair_i as above; for involution)
    Sends the input through the Caesar rotor in the reverse direction               (...-adv)%62: 62 alnum vals; 1-to-1 & onto func)
    Encodes the character as ASCII                                                  (un_ord: ordinal username)
    Adds to string                                                                  (out += chr(un_ord); converts int to chr)
    Returns string

    Fig 5. Series rotor representation
                   ___         ___         ___         ___         ___     __
      [input]--> /abcde\\    /mnopa\\    /jklmn\\<---/bcefg\\--->/defgh\\   '\
                |p     f||->|l     b||  |i     o||  |a     h||<-|c     i||->-.\
     [output]<--|o  O  g||======O  c||======O  p||======O  i||======O  j||   v ) mirror reflector (retroreflector)
                |n     h||<-|j     d||->|g     a||  |p     j||  |a     k||-<-'/-.
                 \mlkji//    \ihgfe//<---\fedcb//--->\onmlk//    \ponml//  _./   \ 
       advances   ^   |         ^         |    ^           ^        ^             | 
                  |   |         |       .' ___  `.     ___  `.      |            /
                   `-'        (inc)    |  / K \\  |   / E \\  |      `----------'
                (prev*adv)             `>|  O E||-'  |K O Y||-'        (pair_i)
                *total adv                \_Y_//      \___//
                                        (prev*adv)    (inc)   secondary rotors (separate to create up to nth triangle # advance offsets)

    Fig 6. Modified with counting rotor
                   ___     __
      [input]--> /abcde\\   '\
                |p     f||->-.\
     [output]<--|o  O  g||   v ) mirror reflector (retroreflector)
                |n     h||-<-'/-.
          ____   \mlkji//  _./   |
         / E \\     ^            |  
     .->|K O Y||-.  |            | (pair_i)
    |    \___//   | |            |
    |             V_|____        |
    |           /1234567\\<-----'          
  (inc)------>/no       89\\
    .---------|m    O    a||    
    V         \lk       cb//    advance offset counting rotor
  (prev adv)--->\jihgfed//      (a=10, b=11..)
    |     ___     ^   
    |    / K \\   |   
     `->|  O E||-'  
         \_Y_//      
 
    A single advancing rotor does almost the same thing as multiple rotors individually stepped with shift cipher and relatively cheap.
    Primarily relies on int addition, modulo and string/array indexing.
    Instead of 5 separate rotors, there is a separate rotor that counts steps, which also rotates with a modulo function.    
    The path is the same from input->output as it is from output->input. 
    The advance changes the effective center point of the reflector relative to the input side of the rotor.
    Secondary key rotors are like simplified 90's DRM codewheels.
    Rotor behavior electromechanically like brushes plus a rotor.
    
    "Veni, vidi, vexi"
        -Some guy abusing Latin

    References:
        "Caesar cipher" by Caesar, G. J. (~80BC)
        "Enigma machine" by Scherbius, A. (1918 not-BC)
        "Dial-A-Pirate" by Lucasfilm Games (1990)

    Appendix/Glossary:

    Caesar cipher - A substitution cipher that offsets the character by 3, although it is often used for cipher disks that use any offset.

    Flexibility is offers because the offset can be varied and the cipher disk loops around to the start. Commonly used as ROT13 which is the involutory variant.
    ABCDEFGHIJLKMNOPQRSTUVWXYZ
    DEFGHIJKLMNOPQRSTUVWXYZABC

    Enigma machine - An rotor based electromechanical encryption device used in WWII. A reflector made the machine involutory.
    Advancing rotors made it notoriously difficult to crack. The 'bombe,' based on the prior art the Polish 'bomba,' 
    was designed by Alan Turing as an electromechanical computer to crack enigma encryption.

    Dial-a-Pirate - A cardboard cipher disk for the 1990 Lucasfilms game "The Secret of Monkey Island."
    Not the first of its kind, but was many guys' first brush with anti-piracy digital rights management. 
    It was meant to help stop pirates attempting to discover the secret of Monkey Island™. 
    The cipher disk utilized faces of pirates that were split into upper and lower halves as the key. 
    The user would have to match a face combination given by the computer program and give a year based on a location on the cipher disk.
    Prior art was often just referencing passwords in a manual.

    :param un: string to be encrypted
    :param pw: string to be used as key
    :return: returns encrypted string
"""

def vvv(un,pw):
    pw_l, out, adv, pair_i,= len(pw), '', 0, 0
    for i in range(len(un)):
        un_ord, ani = ord(un[i]), -1 
        ani = 48 if 48 <= un_ord <= 57 else 55 if 65 <= un_ord <= 90 else 61 if 97 <= un_ord <= 122 else ani
        if ani >= 0:
            adv = (i + pair_i + adv + ord(pw[i%pw_l]) + ord(pw[adv%pw_l]))%97
            un_ord = (un_ord - ani + adv)%62
            pair_i = abs(un_ord + un_ord - 61)
            un_ord = (185 - un_ord - adv)%62 
            un_ord += 48 if un_ord <= 9 else 55 if un_ord <= 35 else 61
        out += chr(un_ord)
    return out




# UTILITY FUNCTIONS
def vvv_test():
    un = "h4ck3r0n573r01d5"
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
    file_list_2 = file_list.copy()
    for i in range(len(file_list)):
        unpw = file_list_2[i][:-11].split(split_char)
        if len(unpw) == 2:
            un = unpw[0]
            pw = unpw[1]
            e_un = vvv(un,pw)
            e_pw = vvv(pw,un)
            if (e_un+split_char+e_pw+'.secure.bak' in file_list):
                file_list.remove(e_un+split_char+e_pw+'.secure.bak')
                file_list.remove(un+split_char+pw+'.secure.bak')
    for file in file_list:
        unpw = file[:-11].split(split_char)
        if len(unpw) == 2:
            un = unpw[0]
            pw = unpw[1]
            e_un = vvv(un,pw)
            e_pw = vvv(pw,un)
            file1 = open(myPath+file, "r")
            cont = file1.read()
            file1.close()
            e_cont = vvv(cont,pw)
            file2 = open(myPath + e_un + '_' + e_pw + '.secure.bak', "w")
            file2.write(e_cont)
            file2.close()
            num_files += 1

    print("Created " + str(num_files) + " files.")

def main():
    vvv_test()
    #vvv_encrypt_files()

if __name__ == "__main__":
    main()
