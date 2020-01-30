---
layout: post
title:  "picoCTF - Insp3ct0r with Jupyter"
date:   2019-10-23 12:07:25 +0000
excerpt_separator: <!--more-->
author: clay
image: assets/images/jupyter/jupyter-logo.png
categories:
  - ctf
  - python
  - web
---

I am experimenting with Juypter notebooks for solving CTF problems. Here is a notebook converted to a blog entry. You can find the original Jupyter Notebook file [here](/assets/jupyter/picoCTF-2019-web-inspector.ipynb)

<!--more-->

**Problem Statement**

Kishor Balan tipped us off that the following code may need inspection: [https://2019shell1.picoctf.com/problem/63975/](https://2019shell1.picoctf.com/problem/63975/) or [http://2019shell1.picoctf.com:63975](http://2019shell1.picoctf.com:63975)


**Solve**

First we will import the functionality we will need for this challenge. Requests will allow us to easily talk to the webserver and BeautifulSoup will allow us to work with the HTML code that is the webserver provides us.

```python
import requests
from bs4 import BeautifulSoup as bs
from bs4 import Comment
```

We will create a session object, get our URL for the challenge, initialize an empty flag, and get the main page.


```python
s = requests.session()
url = 'https://2019shell1.picoctf.com/problem/63975/'
flag = ""
r = s.get(url)
```

Now that we have the base webpage's source code in our request object `r`, we will build see if there is a flag in our source.


```python
[line for line in r.text.split('\n') if 'flag' in line]
```




    ['\t<!-- Html is neat. Anyways have 1/3 of the flag: picoCTF{tru3_d3 -->']



So we have a comment with that tells us the flag will be in parts. Seems that we have part 1. Lets creat a regular expression based on this, that may help us find the rest of the pieces.


```python
from re import compile
patt = compile('flag: ([\w{}_?]*) ')
```

We have the source code for the site, lets build a BeautifulSoup object so we can grab that comment.


```python
soup = bs(r.text,features="html.parser")
```

Since our regular expression has the a capture group defined, we will just grab that chunk from our comments and add them to our flag.


```python
m = patt.findall(r.text)
if m:
    flag += m[0]
```

We will now grab all the hyperlinks from our `soup` object, and see if we have any pieces of the flag there.


```python
htmls = ""
for link in soup.findAll('link'):
    r = s.get(url + link['href'])
    htmls += r.text
[line for line in htmls.split('\n') if 'flag' in line]
```




    ["/* You need CSS to make pretty pages. Here's part 2/3 of the flag: t3ct1ve_0r_ju5t */"]



Now we will grab that piece of the flag and add it to `flag` variable.


```python
for link in soup.findAll('link'):
    r = s.get(url + link['href'])
    m = patt.findall(r.text)
    if m:
        flag += m[0]
```

Another place to look are any javascript files that might exist. So we will check anything from a `script` tag.


```python
js = ""
for script in soup.findAll('script'):
    r = s.get(url + script['src'])
    js += r.text
[line for line in js.split('\n') if 'flag' in line]
```




    ['/* Javascript sure is neat. Anyways part 3/3 of the flag: _lucky?d3db9182} */']



Now we will grab that final piece of the flag and append to our `flag` variable


```python
for script in soup.findAll('script'):
    r = s.get(url + script['src'])
    m2 = patt.findall(r.text)
    if m2:
        flag += m2[0]
```

And now we can check out final flag. Looks good to me.


```python
flag
```




    'picoCTF{tru3_d3t3ct1ve_0r_ju5t_lucky?d3db9182}'


