---
layout: post
title: "C3T Tryout Challenges - Stevie and Ray"
date: 2017-11-01 23:30:00
excerpt_separator: <!--more-->
disqus: true
author: clay
categories:
  - ctf
  - c3t
  - python
image: assets/images/c3t/stevie-jamie.jpg
---

**Stevie Wonder and Jamie Foxx playing the role of the late great Ray Charles**

For our internal CTF for tryouts the past two years, I have had a series of challenges called _Stevie and Ray_. 

These challenges were favorites with the cadets. Both challenges were released in the Fall 2016 challenge with many solves for the first part, but none for the second. For Fall 2017, I re-released Stevie and Ray 2 and it had 3 or 4 solves this semester. In this post, I will reveal the details of how Stevie and Ray are created, and how they can be solved.

<!--more-->

### Stevie and Ray

Hacker candidates were presented with the challenge description of `There is an odd service running at {{server}} on port {{port}}. See if you can break its code and interact with it.`.

When the connecting to the service the following mesage is received:
```
.. .o o. o. .o .. oo o. .. oo o. o. .. .o o. oo .o ..
.. oo oo .. oo .. .o .o .. .o .o .. .. oo .. .o oo o.
.o .o .. .. o. .. .. o. .. oo o. oo .. .o .. o. o. oo
```
This appears to be garabage, but after a few minutes of studying, you may see that it is Braille. Braille is an interesting encoding scheme. A single character
is represent by a series of flat or raised dots in the arrangement of 3 rows and 2 columns. There is a character for the 26 lowercase letters. There is also a
shift symbol and a number sign symbol. When the letter `a` through `j` is preceeded with by the `number` character that is the number 1-0 [where a is 1 and j is
0]. When proceeded by a `shift` symbol, the following letter is a capital letter.

The encoded provided is using a lower case letter O for a raised dot and a period for a flat dot. Decoding the provided prompt, we see the message is `What do you want?`. The user is able to interact with the service by typing a response, but nothing happens until after three lines have been entered. Afterwards, another encoded message is returned. Providing the input of `flag` three times provides the following message:

```
.. .o o. o. o. oo .. .. .. oo o. .. oo .o oo o.
.. o. .o oo oo .o oo .. .. .o .o .. .o o. .. .o
.o o. o. o. o. oo o. .. .o o. o. .. .. .. .. ..
```

This decodes to `Sorry, no dice` and the service is closed. Since the Braille message is three lines long, the student should see they have to enter their
response in Braille. Encoding either `Flag` or `flag` will provide the flag encoded in Braille.

```
.. .o o. o. o. oo .. .. .. oo o. .. oo .o oo o.
.. o. .o oo oo .o oo .. .. .o .o .. .o o. .. .o
.o o. o. o. o. oo o. .. .o o. o. .. .. .. .. ..
```
The flag is `C3T Br4il3 4 The W1n`. There are no symbols for `{ }` so the normal flag pattern is not followed, but its a quick solve at this point.

The server code that generates the prompt can be seen below:

```python
#!/usr/bin/env python

import sys, os
from random import randint as ri
from string import digits

lowercase = [chr(x) for x in range(97,123)]
uppercase = [chr(y) for y in range(65,91)]

letterdots = [[1,],[1,2], [1,4], [1,4,5], [1,5], [1,2,4], [1,2,4,5], [1,2,5],
        [2,4], [2,4,5], [1,3], [1,2,3], [1,3,4], [1,3,4,5], [1,3,5],[1,2,3,4],
        [1,2,3,4,5], [1,2,3,5], [2,3,4], [2,3,4,5], [1,3,6], [1,2,3,6], 
        [2,4,5,6], [1,3,4,6], [1,3,4,5,6], [1,3,5,6]]
shift = [6,]
numbersign = [3,4,5,6]
punctuation = " .,?;!"
puncdots = [[], [2,5,6], [2,], [2,3,6], [2,3], [2,3,5]]


def d2l(dotlist):
    if dotlist in letterdots:
        return lowercase[letterdots.index(dotlist)]
    elif dotlist in puncdots:
        return punctuation[puncdots.index(dotlist)]
    else:
        return "&"

def d2i(dotlist):
    ind = (lowercase.index(d2l(dotlist)) + 1) % 10
    return digits[ind]

def build(message):
    brows = []

    for line in message.split('\n'):
        brow = []
        for letter in line:
            if letter in lowercase:
                brow.append(letterdots[lowercase.index(letter)])
            elif letter in uppercase:
                brow.append(shift)
                brow.append(letterdots[lowercase.index(letter.lower())])
            elif letter in digits:
                brow.append(numbersign)
                brow.append(letterdots[(digits.index(letter) -1) % 10])
            elif letter in punctuation:
                brow.append(puncdots[punctuation.index(letter)])
        brows.append(brow)
    final = []
    for row in brows:
        base = ri(22,90)
        for dotrow in range(3):
            braille = ''
            for letter in row:
                if dotrow + 1 in letter:
                    braille += 'o'
                else: braille += '.'
                if dotrow + 4 in letter:
                    braille += 'o'
                else: braille += '.'
                braille += ' '
            final.append(braille)
    return '\n'.join(final)


if __name__ == "__main__":
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    print(build("What do you want?"))
    answer1 = raw_input()
    answer2 = raw_input()
    answer3 = raw_input()
    answer = '\n'.join([answer1, answer2, answer3])
    if answer == build("Flag") or answer == build("flag"):
        print(build("C3T Br4il3 4 The W1n"))
    else:
        print(build("Sorry! No dice"))
```

The code to solve the challenge can be found here:
```python
#!/usr/bin/env python

import sys
from random import randint as ri
from string import digits

lowercase = [chr(x) for x in range(0x61, 0x61 + 27)]
uppercase = [chr(x) for x in range(0x61, 0x41 + 27)]

letterdots = [[1,],[1,2], [1,4], [1,4,5], [1,5], [1,2,4], [1,2,4,5], [1,2,5],
        [2,4], [2,4,5], [1,3], [1,2,3], [1,3,4], [1,3,4,5], [1,3,5],[1,2,3,4],
        [1,2,3,4,5], [1,2,3,5], [2,3,4], [2,3,4,5], [1,3,6], [1,2,3,6], 
        [2,4,5,6], [1,3,4,6], [1,3,4,5,6], [1,3,5,6]]
shift = [6,]
numbersign = [3,4,5,6]
punctuation = " .,?;!"
puncdots = [[], [2,5,6], [2,], [2,3,6], [2,3], [2,3,5]]


def d2l(dotlist):
    if dotlist in letterdots:
        return lowercase[letterdots.index(dotlist)]
    elif dotlist in puncdots:
        return punctuation[puncdots.index(dotlist)]
    else:
        return "&"
def d2i(dotlist):
    ind = (lowercase.index(d2l(dotlist)) + 1) % 10
    return digits[ind]

def solve(data):
    for linecount, line in enumerate(data.split('\n')):
        #print("Line count is {} and line len is \
               # {}".format(linecount,len(line)))
        if len(line)==0: continue
        line = line.strip()
        if linecount == 0:
            letters = []
            for pairs in line.strip().split(' '):
                letters.append([])
            #print("all letters initialized ")

        lettercount = len(letters)
        for i, pairs in enumerate(line.split(' ')):
            #print ("looking at pair #%d (%s) from line %d" % (i, pairs, \
                #linecount))
            if len(pairs) == 0: continue
            for j, column in enumerate(pairs):
                if len(column) == 0: continue
                if j==0 and column == 'o':
                    #print ("    we got raised in column 0 (%s)" % column)
                    letters[i].append(linecount+1 )
                if j==1 and column == 'o':
                    #print ("    we got raised in column 1 (%s)" % column)
                    letters[i].append(linecount + 4)
                #print ("letter %d is now" % i, letters[i])

        if linecount == 2:
            message = ''
            i = 0
            while i < len(letters):
                letter = sorted(letters[i])
                if letter == shift:
                    nextletter = sorted(letters[i+1])
                    message += d2l(nextletter).upper()
                    i += 2
                elif letter == numbersign:
                    nextletter = sorted(letters[i+1])
                    message += d2i(nextletter)
                    i += 2
                else:
                    message += d2l(letter)
                    i += 1
            return message

if __name__ == "__main__":

    cipher = \
""".. .o o. o. .o .. oo o. .. oo o. o. .. .o o. oo .o ..
.. oo oo .. oo .. .o .o .. .o .o .. .. oo .. .o oo o.
.o .o .. .. o. .. .. o. .. oo o. oo .. .o .. o. o. oo"""

    print(solve(cipher))
```

_Note:_ these challenges are not making fun of either of these great performers. As a elementary school kid, I had the opportunity to 
meet and perform with Stevie Wonder on the steps of the State House in Columbia, SC. It was a great experience. The year prior, Stevie Wonder
made an appearance on the "Cosby Show." The kids on the show called him "Mr. Wonder" and he said "Call me Stevie." That day when I met him, I told
my mom, I was going to call him "Mr Wonder" also and see if he would tell me the same thing. Well, he did! What a great day.
