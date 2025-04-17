#!/home/astro/qc_suite/installation/bin/python2.7
#
#------------------------------------------------------------------------
#|--------------------- qc_fetch.py ------------------------------------|
#|									|
#|	This program fetches the qc files from a server.		|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	This program looks for files on the server, which are not	|
#|	already in the database. Then it fetches them using scp.	|
#|									|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	Written by Christoph Saulder and Fernando Selman for ESO	|
#|									|
#|	Last update by Christoph Saulder on the 6th of November 2012    |
#|									|
#|----------------------------------------------------------------------|
#


import sys
import string
import shutil 
import os
import socket
import subprocess
import paramiko
import time
import datetime
from   sys          import argv
from qc_suite_lib import *

def printHelpMessage():
   print """\n\n        GENERAL HELP:

        This routine fetches opslog files for qc_suite

        DEPENDENCIES:


        ALGORITHM:


        EXAMPLES:

                1. qc_fetch.py -QC_SUITE_DIR \'/diska/home/astro/qc_suite\'

                \n\n
        """
   return

def printUsageMessage():
   printHelpMessage()
   return



tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
todayslogfile = open(tlfname, 'a' )
now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
todayslogfile.write(now+"------------------------------------------------\n")
todayslogfile.write(now+"program qc_fetch started\n")
todayslogfile.close()

QC_SUITE_DIR = './'
varlistNames = ['QC_SUITE_DIR', 'help']

# We need to pass options
for token in argv:
   if token == '-help':
     printHelpMessage()
     sys.exit(0)


try:
    lineargs = getopts(argv)
except Exception, e:
 tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
 todayslogfile = open(tlfname, 'a' )
 now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
 todayslogfile.write(now+"options not recognized (error: %s)\n" % (e))
 todayslogfile.close()
 print "options not recognized (error: %s)" % (e)
 sys.exit(0)


  # if there is an optfile we read the variable values from it
if lineargs.has_key('-optfile'):
   try:
      optionfile = open(lineargs['-optfile'])
      optionfile.seek(0)
      filestr = optionfile.read()
      optionfile.close()
      splitted= filestr.split('\n')
   except Exception, eee:
      tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
      todayslogfile = open(tlfname, 'a' )
      now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
      todayslogfile.write(now+"cannot open file (error: %s)\n" % (eee))
      todayslogfile.close()
      print "cannot open file (error: %s)" % (eee)
      sys.exit(0)
   #print splitted
   optDict = getopts(splitted)
   for i in range(len(varlistNames)):
      thekey = '-' + varlistNames[i]
      if optDict.has_key(thekey):
            exec(varlistNames[i] + " = " + str(optDict[thekey]))


# now we fill the rest of the variables in the
# command line
#
for i in range(len(varlistNames)):
   thekey = '-' + varlistNames[i]
   if lineargs.has_key(thekey):
         #print lineargs[thekey]
         exec(varlistNames[i] + " = " + str(lineargs[thekey]))

# now we strip all the commands and their arguments and
# whatever is left will be considered to be the list
# of input files
#
parsedFileList =  getFileList(argv)

# minimal error checking...
if len(parsedFileList) != 0:
   printUsageMessage()
   sys.exit(0)

# load configuration file
configfile = open(QC_SUITE_DIR+"config.dat")
configfile.seek(0)
filestr = configfile.read()
configfile.close()
# get pathes and username and password from the file
pathtologs= filestr.split('\n')[2]
host= filestr.split('\n')[3]
targetfolder= QC_SUITE_DIR+filestr.split('\n')[1]
uname=filestr.split('\n')[4]
pword=filestr.split('\n')[5]
ihelp=filestr.split('\n')[20]
instrument=ihelp.upper()
ignored_names = os.listdir(targetfolder) 

#connecting to server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
ssh.connect(host, username=uname, password=pword)
#Read folder
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls '+pathtologs)
readout=ssh_stdout.read() 
filelist=readout.split('\n')

# get date
datetime=time.strftime("%Y-%m-%d %H %M %S", time.localtime())
today=datetime[0:10]

#calculate yesterday
year=int(today[0:4])
month=int(today[5:7])
day=int(today[8:10])

if day==1:
   if month>1:
     if month==2:
       day=31
     if month==3:
       day=28
       if (year%4)==0:
         day=29
         if (year%400)==0:
	   day=28
     if month==4:
       day=31  
     if month==5:
       day=30  
     if month==6:
       day=31
     if month==7:
       day=30     
     if month==8:
       day=31      
     if month==9:
       day=31     
     if month==10:
       day=30      
     if month==11:
       day=31     
     if month==12:
       day=30     
     month=month-1  
   else:
      year=year-1
      month=12
      day=31
else:
   day=day-1

syear=str(year)
if month<10:
  smonth='0'+str(month)
else:
  smonth=str(month)
if day<10:
  sday='0'+str(day)
else:
  sday=str(day)
  
yesterday=syear+'-'+smonth+'-'+sday

# see if today's and yesterday's files are there
filecount= len(filelist)
todayexists=False
yesterdayexists=False

todaysfile="QC1_"+instrument+"."+today+".ops.log"
yesterdaysfile="QC1_"+instrument+"."+yesterday+".ops.log"

for i in range(0,filecount):
  if todaysfile==filelist[i]:
    todayexists=True
  if yesterdaysfile==filelist[i]:
    yesterdayexists=True


if filestr.split('\n')[6]=='2': #just fetch the two newest files
  ftp = ssh.open_sftp()
  if todayexists:
    ftp.get(pathtologs+'/'+todaysfile, targetfolder+'/'+todaysfile)
    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write(now+"fetching "+todaysfile+"\n")
    todayslogfile.close()
  else:
    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write("WARNING: today\'s file("+todaysfile+") does not exit\n")
    todayslogfile.close()
  if yesterdayexists:
    ftp.get(pathtologs+'/'+yesterdaysfile, targetfolder+'/'+yesterdaysfile)
    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write(now+"fetching "+yesterdaysfile+"\n")
    todayslogfile.close()
  else:
    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write("WARNING: yesterday\'s file("+yesterdaysfile+") does not exit\n")
    todayslogfile.close()
  ftp.close()
else:
  
  ftp = ssh.open_sftp()
  if filestr.split('\n')[6]=='1': #fetch all files for the instrument
    for i in range(0,filecount): 
      if string.find(filelist[i],"QC1_"+instrument) != -1:
	 ftp.get(pathtologs+'/'+filelist[i], targetfolder+'/'+filelist[i])
	 tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
	 todayslogfile = open(tlfname, 'a' )
	 now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
	 todayslogfile.write(now+"fetching "+filelist[i]+"\n")
	 todayslogfile.close()
	 
  else: #fetch all new files that fit the parameters
    for i in range(0,filecount): 
      if string.find(filelist[i],"QC1_"+instrument) != -1:
	if filelist[i] in ignored_names:
	  continue
	ftp.get(pathtologs+'/'+filelist[i], targetfolder+'/'+filelist[i])
	tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
	todayslogfile = open(tlfname, 'a' )
	now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
	todayslogfile.write(now+"fetching "+filelist[i]+"\n")
	todayslogfile.close()
  ftp.close()

  
tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
todayslogfile = open(tlfname, 'a' )
now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
todayslogfile.write(now+"program qc_fetch terminated\n")
todayslogfile.write(now+"------------------------------------------------\n")
todayslogfile.close()


# --- If this line is here, the source code will be complete. ---
