import os
import binascii
import names
import argparse
import multiprocessing
from concurrent import futures
#from multiprocessing import Manager

tmpl = """dn: inum={inum},ou=people,o=@!AE1F.6E2B.849B.7678!0001!18E5.E69D,o=gluu
objectClass: gluuPerson
objectClass: top
givenName: {fname}
uid: {uid}
cn: {fname} {uid}
gluuStatus: active
sn: {lname}
userPassword: {{SSHA512}}F2YV+g0H1A0brv89AM8wjqDxrdKoA9IwDqdkPzbftqHArPIPBPUsFfLgeecpkSchu/0rHUGFFp12pY1g0wvGGOx+CAdQuA7H
mail: {uid}@gluu.org
iname: *person*{uid}
displayName: {uid}
inum: {inum}
"""

CPU_CORE = multiprocessing.cpu_count()
EFECTIVE_CPU_THREAD = 2*CPU_CORE + 1
grand_list = []

def oxrand(size=1):
    if size < 1:
        return None
    r = binascii.b2a_hex(os.urandom(size*2)).upper()
    return '.'.join([r[i:i+4] for i in xrange(0, len(r), 4)])
    
def gen_name():
    name = str(names.get_full_name()).split()
    return name[0], name[1]

def gen_inum(F4QUAD):
    r = oxrand(2)
    return '@{}!0001!18E5.E69D!0000!{}'.format(F4QUAD,r)

def split_data(int_total_data_size):
    start = 1000000000
    glist = []
    split_size = int_total_data_size / EFECTIVE_CPU_THREAD
    for i,x in enumerate(xrange(start, start + int_total_data_size, split_size)):
        if i == EFECTIVE_CPU_THREAD:
            glist.append(range(x, (int_total_data_size%EFECTIVE_CPU_THREAD)+x ))
            break
        else:
            glist.append(range(x,x+split_size))
    return glist

def data_dic(uid, F4QUAD):
    fname, lname = gen_name()
    data = {
        'inum' : gen_inum(F4QUAD),
        'fname' : fname,
        'lname' : lname,
        'uid' : 'user_{}'.format(uid),
        }
    return data

def gendata(g):
    tmplist = []
    for i in g:
        d = data_dic(i, F4QUAD)
        tmplist.append(tmpl.format(**d))
    return tmplist
F4QUAD = oxrand(4)

def main():
    parser = argparse.ArgumentParser(description='Parse genuser arguments.')
    parser.add_argument('-n','--number', metavar='int', type=int, help='number of entry to generate',required=True)
    args = parser.parse_args()
    num = args.number

    if num < EFECTIVE_CPU_THREAD:
        print 'Total entry must be greater than minimum slicing length: ', EFECTIVE_CPU_THREAD
        return

    glist = split_data(num)
    with futures.ProcessPoolExecutor(max_workers=EFECTIVE_CPU_THREAD) as executor:
        result = executor.map(gendata, glist)
        executor.shutdown(wait=True)

    for p_out in result:
        for entry in p_out:
            print entry

if __name__ == '__main__':
    main()
