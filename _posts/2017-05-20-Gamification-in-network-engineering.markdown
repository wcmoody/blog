---
layout: post
title: Gamification in a Network Engineering Class 
date: 2017-05-20 13:37:42
excerpt_separator: <!--more-->
disqus: true
author: clay
image: assets/images/gamification/high-speed-internet.jpg
---

In my [IT350](http://wclaymoody.com/teaching/cy-350-networking-engineering-and-design) course, I like to add some capture the flag events on the final project as bonus questions. I take this opportunity to expose the students to CTF games and also allow them to go deeper on a subject that has been covered in class.

This semester I had a three-part problem with three flags. The first two flags were worth three points each and the last one was for four points. The flags were to be solved in order and the difficulty increased with each one. Below is the problem statement given in the assignment:

<!--more-->

```
A cadet learns much about ********** in IT350. A snippet of a router running configuration file can be found on the host 10.R.0.51. (R is the last 2 of your classroom number [52|64]). There are three stages of flags hidden in these systems, see if you can recover the flags. Stage 1 and 2 are worth 3 points each, stage 3 is 4 points. Flags start with IT350. This is also worth endless internet cool points so, no inter-group collaboration!
```

My course was taught in two different classrooms and each classroom has its own subnet within our academic research network. The room number determines the subnet to which each classroom is directly connected. The setup for these problems involved a simple CentOS VM from our ESXi cluster with the address of `10.R.0.51` and a Cisco router in the classroom connected as `10.R.0.50`. This was setup in both the 52 and 64 classrooms. 

### Stage One

The first task for the students was to remotely connect to the VM at the `.51` address in each classroom. This was pretty simple since the first sentence of the problem states a `cadet` and `**********`. This is a hint since the default username in the class is `cadet` and the default password is `**********`. The students learn about secure shell and its advantages over the unsecure telnet application. So if the student connects via ssh to the VM with those credentials, they have access to the machine in question.

This account is very locked down in this environment. They have the ability to create files in their local directory but most of the existing files are locked down so that they are not the owners, can only read and execute those files. A detailed directory listing is below:

```sh
[cadet@it350b1 ~]$ ls -la
total 16
drwx------. 3 cadet  cadet  4096 May 12 07:45 .
drwxrwxr-x. 2 madeye madeye   19 Apr 26 17:54 .
drwxr-xr-x. 4 root   root     31 Apr 27 10:15 ..
-rw-r--r--. 1 madeye cadet    44 Apr 27 10:43 .bash_history
-rw-r-x---. 1 madeye cadet    40 Apr 27 10:41 .bash_login
-rw-r-x---. 1 madeye cadet     0 Apr 27 10:39 .bash_logout
-rw-r--r--. 1 madeye cadet  1170 Apr 26 17:49 running_config.txt
``` 

Before we jump into capturing the flags, let me describe some of the more fun things in their system. The `.bash_login` file sets the prompt and allows no history to be saved.

```sh
[cadet@it350b1 ~]$ cat .bash_login
shopt -u -o history
PS1='[\u@\h \w]\$ '
```

But there is an entry saved in their history.

```sh
cadet@it350b1 ~]$ cat .bash_history
#what are you doing? trying to FIND a hint?
```
This really frustrated the students since they could not use the arrow keys to navigate through their command history when working in the system. This nugget was actually a hint itself. Since most of the students are not from our department, many are not familiar with the intricacies of Linux. They probably do not default to doing a long listing of the directory with hidden files and miss the fact there is what appears to be two current directories (`.`). Actually the one owned by the user madeye, is a period and a space. In this directory is a file called `.hints`, which could be found with the `find` program in the following way.

```sh
cadet@it350b1 ~]$ find . -name "*hint*"
./. /.hints
```
I will talk about what is in this file at the end.

Now to the flag, so from the problem statement the students know a partial router config is located on this host. A simple directory listing will show only one file called `running_config.txt`. The contents of this file (for the 64 classroom)is below:

```
!
hostname <redacted>
!
boot-start-marker
boot-end-marker
!
!
no aaa new-model
memory-size iomem 5
!
ip cef
!
!

!
no ip domain lookup
no ipv6 cef
multilink bundle-name authenticated
!
!
!
!
license udi pid CISCO2901/K9 sn FJC1840A098
!
!
!
!
!
!
interface Embedded-Service-Engine0/0
 no ip address
 shutdown
!
interface GigabitEthernet0/0
 description IT350{stage_1_vms_are_cool}
 ip address 10.64.0.50 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 no ip address
 shutdown
 duplex auto
 speed auto
!
interface FastEthernet0/0/0
 no ip address
 shutdown
 duplex auto
 speed auto
!
interface FastEthernet0/0/1
 no ip address
 shutdown
 duplex auto
 speed auto
!
ip forward-protocol nd
!
ip http server
no ip http secure-server
!
ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0
!
access-list 10 permit 10.52.0.51
!
!
control-plane
!
!
line con 0
line aux 0
line 2
 no activation-character
 no exec
 transport preferred none
 transport output pad telnet rlogin lapb-ta mop udptn v120 ssh
 stopbits 1
line vty 0 4
 access-class 10 in
 password 7 1505041B3B3E23253C0C222300381302124F
 login
 transport input telnet
!
scheduler allocate 20000 1000
!
end
```
If they view this file, they will see the first flag: `IT350{stage_1_vms_are_cool}`

### Stage Two:

The second stage is where I want the cadets to begin applying what they learned in the course: specifically configuring router interfaces, creating access control lists, and securing vty lines. They should now want to connect to the router in order to recovery more flags.

Since the description of the GigabitEthernet 0/0 interface is where the first flag was, they should know its IP address. If they try to ping this address, they will see the router is on the network and operational. Now they should try to access it. If they skip down to the configuration for `line vty 0 4` they will see that only the telnet protocol is allowed as the inbound transport protocol. If they try to connect from their VM (or any workstation in the classroom) to this router they will be denied.

```sh
[cadet@it350b1 ~]$ telnet 10.64.0.50
Trying 10.64.0.50...
telnet: connect to address 10.64.0.50: Connection refused
```

They then should begin to ask themselves why is that? Going back to the configuration, they should see that standard access list 10 is applied in the inbound direction on those vty lines. Finding this ACL in the config, shows it permits only the single IP address of `10.52.0.51`. Since this is the 64 classroom VM, they should realize the other classrooms VM can connect to their classroom's router and vice versa. This is my attempt to show them the need to pivot. They have two choices, they can now ssh into the other classrooms VM and connect to their classrooms router via telnet, or they can assume they can connect to the 52 classroom's router and go from there. Either way is sufficent to recover this stage's flag.

When they do either of these they get the following message (this is a connection to the 52 classroom's router from the 64 classroom VM)

```
[cadet@it350b1 ~]$ telnet 10.52.0.50
Trying 10.52.0.50...
Connected to 10.52.0.50.
Escape character is '^]'.

You've reach correct router, but if you don't see
a text block below with instructions, you have
connected the wrong way


***************************************
* Welcome to the IT350 Flag Router    *
*                                     *
* wow, you are doing well. Your next  *
* flag is:                            *
*                                     *
* IT350{stage_2_stnd_acls_on_vty0-4}  *
***************************************

[==o=]
Constant Vigilance!

User Access Verification

Password:
``` 

And there is the second stage flag.

_Note_: The first block of text saying they have reached the correct routers is the message of the day banner. The welcome message below is the login banner. This way if a student attempts to console into my router physically, they will not see the flag since its only shown on telnet logins.

### Stage Three

The final flag requires a little stretch from what they learned in class. We teach them to the password-encryption service provided by Cisco, to "encrypt" their local account, console, and vty line passwords. We mention the 7 indicates the algorithm used, but do not mention its weakness and simple reversibility. 

Knowing there is a third flag, hopefully they are motivated to login to the router. Many cadets tried to use the standard default password for the class to no avail. If they decide to investigate the encrypted password from the config (`1505041B3B3E23253C0C222300381302124F`) and do a simple Google search for "decrypt cisco password" the first result will be [IFM - Cisco Password Cracker](http://www.ifm.net.nz/cookbooks/passwordcracker.html). Using this site, they will quickly decrypt the password as shown:

![](/assets/images/gamification/passwordcrack.png)

Using that password as the login reveals the third and final flag in the hostname of the device:

```
User Access Verification

Password:
IT350_stage_3_cisco_encryption_ftl>
```

Interestingly, curly braces are not valid characters in Cisco host names.

### Hint File

So if they had found the hint file and viewed its contents, they would have seen the following:

```
[cadet@it350b1 ~]$ find -name "*hint*" -exec cat {} \;
can you read a config file?

do you understand ACLs?

are the passwords secure?

IT350{...what...are...you...doing...in...my...files?}
```
They would not have gotten points for the last line, but the rest of the file would guide them on the path to success.

### Conclusion

The few teams that finished this puzzle thought it was fun. I think it provided a good opportunity for them to apply what they learned in an almost reverse fashion. Instead of configuring a network given a specification, they were given a configuration and needed to explore that network. Also, the amazing weakness in the Cisco encryption protocol should open their eyes to the truth that you should never try to write your own crypto unless you name is Diffie, Hellman, Merkle, Rivest, Shamir, Adlemen, etc.
