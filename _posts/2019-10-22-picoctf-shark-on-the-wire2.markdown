---
layout: post
title: "picoCTF 2019 - Shark on the Wire 2 aka 'Mama Shark'"
date: 2019-10-22 13:37:11
excerpt_separator: <!--more-->
disqus: true
author: clay
image: assets/images/pico2019/shark2/mama_shark.jpg
categories:
  - ctf
  - network
  - pcap
  - pico

---

Back to another picoCTF challenge, this time to a challenge that is more in my wheelhouse. Network traffic forensics... specifically "shark on the wire 2" for 300 points. There is a first challenge in this series, which would be _Baby Shark_ so this one is _Mama Shark_

<!--more-->

**Describe It**

The problem description:

```
We found this packet capture. Recover the flag that was pilfered from the network. You can also find the file in /problems/shark-on-wire-2_0_3e92bfbdb2f6d0e25b8d019453fdbf07.
```

You can grab a copy of the pcap file [here](/blog/assets/images/pico2019/shark2/capture.pcap).

When I solved this on the first Sunday night of the competition, I was only the 26th person to solve the challenge. By far my earliest solve of the event. At the time of writing this blog, there were 522 solves. Which is still considerably less than the 3733 that had solved the first wireshark challenge.

**Analyze It**

On to the challenge... looking at the pcap with the file command we see that yes it is a packet capture file.

```bash
$ file capture.pcap
capture.pcap: tcpdump capture file (little-endian) - version 2.4 (Ethernet, capture length 262144)
```

So this file was created with tcpdump. We will open it with [wireshark](https://www.wireshark.org/download.html), but eventually will extract the flag with some other cool tools.

In wireshark, the "Statistics" menu has some good places to start. I like to look at [Endpoints.](https://www.wireshark.org/docs/wsug_html_chunked/ChStatEndpoints.html) Here you get a breakdown of the number of logical endpoints for a specific protocol layer. Here we see a list of IPv4, TCP, and UDP endpoints.

![](/blog/assets/images/pico2019/shark2/shark-2-ipv4-endpoints.png)

34 `IPv4` distinct addresses were seen in the capture. Most of them are RFC 1918 [private address](https://en.wikipedia.org/wiki/Private_network). This makes sense as most of the time CTF traffic is between two local private hosts.

![](/blog/assets/images/pico2019/shark2/shark-2-tcp-endpoints.png)

Only two `IP:TCP` port tuples observed. Telling us there is only one TCP flow in the capture. A quick easy place to start and probably quickly rule out.

![](/blog/assets/images/pico2019/shark2/shark-2-udp-endpoints.png)

80 total `IP:UDP` port tuples observed. Sorting by _bytes sent_ we see lots of use of port `5000` and `8990`.

The next statistic I like to look at to get a feel for the packet capture is the [Protocol Hierarchy](https://www.wireshark.org/docs/wsug_html_chunked/ChStatHierarchy.html). This provides a quick glance at how the protocols in percentage of traffic in the file. 

![](/blog/assets/images/pico2019/shark2/shark-2-proto-hier.png)

Here we see that 56% of the traffic is `IP`, 42% is `ARP`. Furthermore, 45% is `IP/UDP` and 40% is `IP/UDP-Data`. So ARP and UDP-Data are the most interesting.

We can quickly rule out the lone TCP flow by seeing there is not an entire flow there. Additionally the ARP traffic appears to be only `10.0.0.5` looking for a bunch of MAC addresses for other hosts in its network. So UDP-Data packets are where we will focus.

A quick filter in wireshark of `udp and data` will give us look at those interesting packets. 

![](/blog/assets/images/pico2019/shark2/shark-2-filter-udp-data.png)

From here, what I like to do is highlight the field I am interested in the bottom panel, and then select the packet back in the top frame. Using the arrow keys, I can scroll down and quickly see how the highlighted field in the hex dump changes. For this pcap, I see few mentions of "picoCTF" and wanting to get flags. These are red-herrings. I keep going further and further into the pcap, and begin to think maybe this is a dead end. Then I hit somethign interesting.

![](/blog/assets/images/pico2019/shark2/shark-2-start-1104.png)

In packet 1104, I see the message `start`. This packet has a source port of 5000 and a destination port of 22. I try and see what other traffic has these characterists. Only one other packet matches, but its data is set to "end". This is packet 1303. So something is happening between "start" and "end" of packets 1104-1303.

![](/blog/assets/images/pico2019/shark2/shark-2-ports-5000-22.png)

Scrolling through these packets, nothing looks obvious. A few common themes do arise though. The data length is consistently 5, but its just five lowercase `a`'s. The destination ports seem to only be 22 and 100, but none of the source ports stay consistent for the traffic desintated for port 22. There is a block of traffic between ports 1234 on both ends. I decide to filter on the destination port 22 traffic since that is what our "start" and "end" message had.

![](/blog/assets/images/pico2019/shark2/shark-2-dstport-22.png)

Now we are getting hotter. Nothing changes from packet to packet except the source udp port. In fact the port minus 5000 (our start and end message port), looks like values in the ASCII range.

![](/blog/assets/images/pico2019/shark2/shark-2-srcport-5000.png)

ASCII character 112, 105, 99, 111 are `pico` so I am pretty sure we just hit pay dirt.

**Solve It**

That is enough of wireshark, now its time for some python magic. Featuring the powers of `scapy`. If you don't have `scapy` a quick `pip install scapy` will hook you up.

Firing up `ipython`, we will start by importing importing scapy into our workspace.

```python
In [1]: from scapy.all import *
```

Next we want to open the pcap file we have so we can parse it for the data we want. We also will initial our `flag` as an empty list.

```python
In [2]: packets = rdpcap('capture.pcap')

In [3]: flag = []
```

We will now loop through each packet, and check if it a UDP packet and if so check its destination port is 22. We cannot check the udp ports until we know for sure it's udp.

```python
In [4]: for p in packets:
   ...:     if UDP in p and p[UDP].dport == 22:
```

We now want to make sure the source port is greater than 5000 since we plan to subtract 5000 from it.

```python
   ...:         if p[UDP].sport > 5000:
```

Now we will append the source port - 5000 to our flag list.

```python
   ...:             flag.append(p[UDP].sport - 5000)
   ...:
```

Now lets print that flag as characters...

```python
In [5]: print ''.join(chr(c) for c in flag)
picoCTF{p1LLf3r3d_data_v1a_st3g0}
```

Boom! Now with the magic of `%save` in ipython, we can save our script.

```python
In [6]: %save exploit.py 1-5
The following commands were written to file `exploit.py`:
from scapy.all import *
packets = rdpcap('capture.pcap')
flag = []
for p in packets:
    if UDP in p and p[UDP].dport == 22:
        if p[UDP].sport > 5000:
            flag.append(p[UDP].sport - 5000)

print ''.join(chr(c) for c in flag)
```

And there you have it.... but one last thing...

Some `tshark` and bash kung-fu... hit me up if you want an explaination.

```bash
$ tshark -r capture.pcap -Tfields -e udp.srcport "udp and udp.dstport==22" | grep -v 5000 | awk {'printf "%c", (int($0)-5000)'};echo
picoCTF{p1LLf3r3d_data_v1a_st3g0}
```

**But Why?**

Why would you need to be able to do this and where would you see such a thing? Data exfiltration is a big problem. Many pieces of malware these days will try to leak your data out across a network without network defenses detecting it. UDP is normally not monitoried that closely. This exfil was suttle in that it was small (only 5 bytes in the data field and that was just `aaaaa`) and was not a consistent flow from the same source port. Is this a realistic exfil? probably not, but the ability and exposure to find hidden gems in network traffic would be a learning point. And as discussed, only 522 of the 18,212 teams in picoCTF solved this challenge.


