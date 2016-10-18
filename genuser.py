#import os
#import binascii
import names
import argparse
import random

# A sample entry
"""dn: inum=@!AE1F.6E2B.849B.7678!0001!18E5.E69D!0000!AC0A.F4A8,ou=people,o=@!AE1F.6E2B.849B.7678!0001!18E5.E69D,o=gluu
objectClass: ox-AE1F6E2B849B7678000118E5E69D
objectClass: gluuPerson
objectClass: top
givenName: Shouro
uid: shouro
cn: Shouro shouro
gluuStatus: active
sn: Chow
userPassword: {SSHA512}F2YV+g0H1A0brv89AM8wjqDxrdKoA9IwDqdkPzbftqHArPIPBPUsFfLgeecpkSchu/0rHUGFFp12pY1g0wvGGOx+CAdQuA7H
mail: shouro@gluu.org
iname: *person*shouro
displayName: shouro
inum: @!AE1F.6E2B.849B.7678!0001!18E5.E69D!0000!AC0A.F4A8
"""

tmpl = """dn: inum={inum},ou=people,o=@!EDD8.F0BB.1EED.03F6!0001!DFD1.52B0,o=gluu
objectClass: gluuPerson
objectClass: top
givenName: {fname}
uid: {uid}
cn: {fname} {uid}
gluuStatus: active
sn: {lname}
userPassword: {{SSHA512}}b3AjXKcf3Cfjujv96bzQIDZU/MugwXRQJquw5MnFzBJO3B4mkKdHJXmolayDzBruwFAmE58PE4Gaaektx/Ql0sK+yRy9AsCg
mail: {uid}@gluu.org
iname: *person*{uid}
displayName: {uid}
inum: {inum}
"""

UCON = set()

def oxrand(size=1):
    if size < 1:
        return None
    #r = binascii.b2a_hex(os.urandom(size*2)).upper()
    r = '%0x' % random.randrange(16**(size*4))
    r = r.upper()
    return '.'.join([r[i:i+4] for i in xrange(0, len(r), 4)])
    
def gen_name():
    name = str(names.get_full_name()).split()
    return name[0], name[1]

def gen_inum(F4QUAD):
    while True:
        r = oxrand(2)
        if r not in UCON:
            UCON.add(r)
            break
    return '@{}!0001!18E5.E69D!0000!{}'.format(F4QUAD,r)

def gen_continuous_uid(num):
    start = 1000000000
    return (i for i in xrange(start, (start + num)))

def data_dic(uid, f4q):
    fname, lname = gen_name()
    data = {
        'inum' : gen_inum(f4q),
        'fname' : fname,
        'lname' : lname,
        'uid' : 'user_{}'.format(uid),
        }
    return data

def main():
    parser = argparse.ArgumentParser(description='Parse genuser arguments.')
    parser.add_argument('-n','--number', metavar='int', type=int, help='number of entry to generate',required=True)
    args = parser.parse_args()
    num = args.number

    F4QUAD = oxrand(4)
    uidg = gen_continuous_uid(num)
    container = []

    for x in xrange(num):
        d = data_dic(uidg.next(), F4QUAD)
        container.append(tmpl.format(**d))

    for entry in container:
        print entry
        
    print '# Report'
    print '# Total entry: {}'.format(len(UCON))

if __name__ == '__main__':
    main()
