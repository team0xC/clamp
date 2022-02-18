#vvv generate random files
myPath = "C:/School/Security/append/"
import random
import string

def randstr():
    str = string.ascii_letters + string.digits
    return ''.join(random.choice(str) for i in range(random.randrange(10, 30)))

for i in range(100):
    file1 = open(myPath + randstr() + '_' + randstr(), "w")
    file1.write('FLG' + randstr())
    for i in range(20):
        file1.write('\nV' + str(i) + ':0')
    file1.close()