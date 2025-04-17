#!/home/astro/qc_suite/installation/bin/python2.7

import os
import sys
import subprocess
import string
import paramiko
import select


targetfolder="/home/lssciops/sciweb/lasilla/sciops/CCDs/WFI/qc_suite/plots"
hostname= "epu.ls.eso.org"
usn="lssciops"
pw="2good4u"
   
   #connect to seimprver
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(hostname, username=usn, password=pw)
(stdin, stdout, stderr) = ssh.exec_command('cd '+targetfolder+' ; webcp *')
for line in stdout.readlines():
   print line
ssh.close
# while True:
#    l, wl, xl = select.select([channel],[],[],0.0)
#    if len(rl) > 0:
      # Must be stdout
#       print channel.recv(1024)