#!/home/astro/qc_suite/installation/bin/python2.7
#
#------------------------------------------------------------------------
#|--------------------- qc_main.py -------------------------------------|
#|									|
#|	This is the main controll script of the qc suite.		|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|									|
#|	This script calls all other subscripts for the qc process.	|
#|									|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	Written by Christoph Saulder and Fernando Selman for ESO	|
#|									|
#|	Last update by Christoph Saulder on the 27th of September 2012|
#|									|
#|----------------------------------------------------------------------|
#

#Initialization
import os
import sys
from   sys          import argv
import subprocess
import string
import paramiko
import select
from qc_suite_lib import *
def printHelpMessage():
   print """\n\n        GENERAL HELP:

        This is the main routine of the qc_suite

        DEPENDENCIES:

                qc_parser.py    # script used to parse opslog files
		qc_plotter.py	# script used to plot the QC parameters

        ALGORITHM:


        EXAMPLES:

                1. qc_main.py -plotnum 31

                \n\n
        """
   return

def printUsageMessage():
   printHelpMessage()
   return

print "------------------------------------------------"
print "start running the qc suite"

plotnum = -1
skip_fetch = 'F'
skip_prepare = 'F'
skip_sync = 'F'
QC_SUITE_DIR = '/diska/home/astro/qc_suite/'

print "QC_SUITE_DIR: %s" % (QC_SUITE_DIR,)

# we check whether an option was passed in the command line
varlistNames = ['plotnum', 'skip_fetch', 'skip_prepare', 'skip_sync', 'QC_SUITE_DIR', 'help']

# if there is a -help option we just print the general help message
# notice that this is the only no-argument option allowed.
#
# if we are creating a fake dataset we do that and exit
#
for token in argv:
   if token == '-help':
     printHelpMessage()
     sys.exit(0)


try:
    lineargs = getopts(argv)
except Exception, e:
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


if len(parsedFileList) != 0:
   printUsageMessage()
   sys.exit(0)


# load configuration file
configfile = open(QC_SUITE_DIR+'config.dat')
configfile.seek(0)
filestr = configfile.read()
configfile.close()


#get the name of the instrument:1

instrument=filestr.split('\n')[20]
qcfilefolder=filestr.split('\n')[1]

#see if instrument is known and how many qc plots are required
if instrument == "wfi":
  nplots=57
else:
  if instrument == "vimos":
    nplots=5
  else:
    if instrument == "vircam":
      nplots=28
    else:
      if instrument == "ocam":
	nplots=2
      else:
	print "unknown instrument: %s" %instrument
        sys.exit(0)


#calling qc_fetch to get new qc files from the server
if skip_fetch == 'F':
  comando = QC_SUITE_DIR+"installation/bin/qc_fetch.py "+" -QC_SUITE_DIR "+"\\\'"+QC_SUITE_DIR+"\\\'"
  print comando
  subprocess.call(comando,shell=True)


#prepare for the parser and parse each opslog file
if skip_prepare == 'F':
   comando = QC_SUITE_DIR+"installation/bin/qc_prepare.py -QC_SUITE_DIR "+"\\\'"+QC_SUITE_DIR+"\\\'"
   print comando
   subprocess.call(comando,shell=True)


   #creating a single file for the plots using qc_parser for every qc file
   files = os.listdir(QC_SUITE_DIR+'logs')
   files.sort()
   for filename in files:
     comando=QC_SUITE_DIR+"installation/bin/qc_parser.py -QC_SUITE_DIR "+"\\\'"+QC_SUITE_DIR+"\\\'"+ \
		" -instrument \\\'"+instrument+"\\\'"+" \'"+qcfilefolder+"/"+filename+"\'"
     print comando
     subprocess.call(comando, shell=True)

# creating the qc plots
#
for counter in range(1,nplots+1):
  if plotnum > 0 and counter != plotnum:
     continue
  print "plotting "+str(counter)+" of "+str(nplots)
  phstring=QC_SUITE_DIR+"installation/bin/qc_plotter.py -QC_SUITE_DIR "+"\\\'"+QC_SUITE_DIR+"\\\'"+ \
		            " -optfile \'"+QC_SUITE_DIR+"plotter/plotopt_"+instrument+str(counter)+".dat\' "
  print phstring
  subprocess.call(phstring, shell=True)

# sending the qc plots to a server
#
for counter in range(1,nplots+1):
  if plotnum > 0 and counter != plotnum:
     continue
  pushstr=QC_SUITE_DIR+"installation/bin/qc_push.py -QC_SUITE_DIR "+QC_SUITE_DIR+ \
			" -filename \'"+"plot"+str(counter)+".png\'"
  subprocess.call(pushstr, shell=True)
 
 
# now we sync the health check pages with Garching
#
print "synchronizing with Garching"
#synchronize with Garching
# get pathes for data from filestr
targetfolder=filestr.split('\n')[15]
hostname= filestr.split('\n')[16]
usn=filestr.split('\n')[17]
pw=filestr.split('\n')[18]
   
   #connect to server and pushing
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(hostname, username=usn, password=pw)
for counter in range(1,nplots+1):
  if plotnum > 0 and counter != plotnum:
     continue
  plotstr="plot"+str(counter)+".png"
  print 'executing: cd '+targetfolder+' ; webcp '+plotstr
  (stdin, stdout, stderr) = ssh.exec_command('cd '+targetfolder+' ; webcp '+plotstr)
  for line in stdout.readlines():
     print line
ssh.close

    
print "running the qc suite is completed"
print "------------------------------------------------" 

# --- If this line is here, the source code will be complete. ---
