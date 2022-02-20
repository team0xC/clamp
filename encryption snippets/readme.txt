    vvv README

    DESIGN CRITERIA:
    1) Alphanumeric only (to limit errors when used in other programs)
    2) Requires a user provided key to encrypt/decrypt (which is not stored or known by the server)
    3) Output is identical in length to input (to limit errors when used in other programs)
    4) A single character change in the string to be encrypted causes a domino effect
    5) A single character change in the key causes a domino effect 
    6) The same function can be used to decrypt and encrypt
    7) Standardized behavior between languages in case services interact
    8) Even if the algorithm is known, it is impractical to attempt decryption because the key is required
    9) Require minimum external libraries
    10) Minimum size that meets the criteria (13 lines of code)

    HOW IT IS USED:
    It is assumed that there are 3 pieces of information, which are sufficiently random.
        -Username (provided by user)
        -Password (provided by user)
        -Contents (returned to user)
    The goal is to make it so all of these pieces of information are known only by the user, and are unknown by the server or any malicious party.
    The function that writes username, password and contents to file should be modified as well as the one for retrieval.
    The server never stores information as plaintext, and never saves any way to decrypt the files.
    Technically a hash may be used for Username and Password because these will always be provided by the bot, and only needs to be verified.
    The hacker only knows the unencrypted flagID and at best only only has access to encrypted data.
    The hacker will not even be able to idendity the encrypted flagID because the encryption key is the unknown password.
    Even if the hacker creates files to observe the enryption behavior or can study the algorithm, the encryption is much more difficult to crack than something like a ROT13 cipher.
    Even relative security is sufficient due to the opprotunity cost of trying to develop an exploit that only works on one team, only have to be more secure than other bikes on the bike rack.
    It is ideal that the hacker not have access to encrypted data or the shell in the first place, but this provides another line of defence even if exploits are patched and new ones are found.
    This approach can be planned even without knowing the specific vulnerabilities because it takes a generalized approach.

    Confidentiality - The identifying data and the confidential data is only ever saved encrypted
    Integrity - The encrypted data can be decrypted only when a key is present, but the integrity is preserved because it can be decrypted and strlen and punctuation are constant
    Availability - No change is made to the availability of encrypted data but the unencrypted data is only available when a key is present, so no modification of availability needs to be patched

Fig 1. Because the flagIDs are encrypted the files can not be found by flagID
          ^ ^
    __   ('w')~ meow     __________
   /  \ <(cat flagID)   |  ______  | ('where is flagID??')  wSfnFc_QM9u5.bak [MeleW]
 _|,  ,|_               | |SERVER| | ,'                     1Ep8ui_8Vw2h.bak [m007y]
|  l33t  |              | |______| |                        Db173h_d744s.bak [W75nk]
 (hacker)    ('huh?')>  |__________|                        ip2Bd3_fmut3.bak [61T5x]       
                           ======                           3dw4Rd_WhPt4.bak [b3B0p]

Fig 2. Even if the hacker gets access to flags, they can not be mass submitted because they are encrypted
          ^ ^
    __   ( *~)           __________
   /  \ <(cat*)         |  ______  |                        wSfnFc_QM9u5.bak [MeleW]
 _|,  ,|_    (MeleW)    | |SERVER| |                        1Ep8ui_8Vw2h.bak [m007y]
|  l33t  |   (m007y)    | |______| |                        Db173h_d744s.bak [W75nk]
 (hacker)    (W75nk)>   |__________|                        ip2Bd3_fmut3.bak [61T5x]                         
             (6175s)       ======                           3dw4Rd_WhPt4.bak [b3B0p]
             (b3B0p)

Fig 3. Even if the hacker has full shell access and can see what we see, s/he still won't know what the flag is...
because the server doesn't know and neither do we! Neither the unencrypted flag or flagID is on the server, nor is the key to unencrypt them
    __                   __________      __   (wut??)
   /  \ <(shell)        |  ______  |    /  \ ,'             wSfnFc_QM9u5.bak [MeleW]                    
 _|,  ,|_               | |SERVER| |  _|,  ,|_              1Ep8ui_8Vw2h.bak [m007y]  (i dunno either)> [un:admin]
|  l33t  |              | |______| | |  l33t  |             Db173h_d744s.bak [W75nk]                    [pw:admin]
 (hacker)               |__________| (hacker in the shell)  ip2Bd3_fmut3.bak [61T5x]                   (the $ADMIN$)
                           ======                           3dw4Rd_WhPt4.bak [b3B0p]

Fig 4. Only the flag bot with both the unencrypted flagID and pw can access the file.
The server only verifies the login info against the encrypted login info and has the key to decrypt the contents

TT,.-=*^^-._. <(flagID)  __________  
|| FLAG BOT/   (FLGpw)  |  ______  | ( flagID # FLGpw -> )  wSfnFc_QM9u5.bak [MeleW]                    
||BEEP BOOP|            | |  \/  | | ,'                     1Ep8ui_8Vw2h.bak [m007y]  
||.-=*^^-.__\  (FLGfl)> | |__/\__| | ( <- m007y # FLGpw )   Db173h_d744s.bak [w75nk]             
||                      |__________| ~'  
      ~*¡CORRECT!*~        ======

    The function can be used to encrypt all data in a way that requires the key to be provided for decryption

    This is done by taking the following steps:
        username2file = vvv(username, password)
        password2file = vvv(password, username)
        contents2file = vvv(contents, password)

    The same process can be used for retrieval:
        username2match = vvv(username, password)
        password2match = vvv(password, username)
        contents2send  = vvv(contents, password)

    A false flag can also be planted for each flagID:
        Filename: flagID_randomstring
        Contents: FLGrandomstring

    It may also be ideal to delete or overwrite the contents of old files.

    HOW IT WORKS:
    Encrypts iterating one character at a time                                                          (un_ord: ordinal username; char as int)
    Encodes character as an integer representation of alphanumeric                                      (ani: Alpha-numeric index offset; -1 is non-alphanumeric flag)
    If not alphanumeric then no change                                                                  (un_ord: ordinal username)
    The key is translated into a rotor stepped by increment to promote domino effect based on key       (pw[i%pw_l]: key rotor stepped by increment) 
    The key is translated into a rotor stepped by previous steps to be influenced by other variables    (pw[adv%pw_l]: key rotor stepped by prev advance)
        including: index, prior character and prior key value
    The key has small set of advance offsets, non-key values are used so there are also non-key advances
    Index causes an advance to promote change with each character                                       (i: index of input string character)
    Index of the matched pair from the mirror reflector to promote domino effect based on previous char (pair_i: index of matched character pair) 
    Previous advance is also used so that all previous variable have aftereffects                       (adv: prior advance value before reassignment)                                              
    Advances the Caesar (shift cipher) rotor by the offset, modulo is used to emulate rotation          (...+adv)%62: 62 alphanumeric values, ensures 1-to-1 and onto function)
    Sends the input through the Caesar rotor                                                            (un_ord-ani+adv: un_ord+ani is an index that corresponds to alphanumeric)
    Uses a mirror reflector to make it symmetrical                                                      ((185-un_ord...)%62: unordered tuples {(0,61),(1,60),(2,59)...}; 185=61+62+62; tuples sum to 61, helps with negative differing modulo behaviors)
    Gets the a unique value for the unordered tuple for advance offset                                  (abs(un_ord+un_ord-61): pair_i as above; maintains encyption/decryption symmetry)
    Sends the input through the Caesar rotor in the reverse direction                                   (...-adv)%62: 62 alphanumeric values, ensures 1-to-1 and onto function)
    Encodes the character as ASCII                                                                      (un_ord: ordinal username)
    Adds to string                                                                                      (out += chr(un_ord); converts int to chr)
    Returns string
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

    A single advancing rotor does the same thing as multiple rotors individually stepped with shift cipher and relatively cheap.        
    The path is the same from input->output as it is from output->input. 
    The advance changes the effective center point of the reflector relative to the input side of the rotor.
    Secondary key rotors are like simplified 90's DRM codewheels.
    Rotor behavior electromechanically like brushes plus a rotor.
    
    "Veni, vidi, vexi"
        -Some guy abusing Latin

    References:
        "Caesar cipher" by Caesar, G. J. (~80BC)
        "Enigma machine" by Scherbius, A. (1918 not-BC)
        "Dial-A-Pirate" by Gilbert, R. (1990)
