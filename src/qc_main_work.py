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
#|	Last update by Christoph Saulder on the 23rd of March 2012	|
#|									|
#|----------------------------------------------------------------------|
#

#Initialization
import os
import sys
import subprocess
import string

print "------------------------------------------------"
print "start running the qc suite"


# load configuration file
configfile = open("config.dat")
configfile.seek(0)
filestr = configfile.read()
configfile.close()


#get the name of the instrument
instrument=filestr.split('\n')[20]
qcfilefolder=filestr.split('\n')[1]

#see if instrument is known and how many qc plots are required
if instrument == "wfi":
  nplots=3
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
subprocess.call("./qc_fetch.py")


#prepare for the parser
subprocess.call("./qc_prepare.py")


#creating a single file for the plots using qc_parser for every qc file
files = os.listdir("logs")
files.sort()
for filename in files:
  helpstring="./qc_parser.py \'"+qcfilefolder+"/"+filename+"\' -instrument \\\'"+instrument+"\\\'"
  subprocess.call(helpstring, shell=True)


# creating the qc plots
for counter in range(1,nplots+1):
  phstring="./qc_plotter.py -optfile \'plotter/plotopt_"+instrument+str(counter)+".dat\' "
  subprocess.call(phstring, shell=True)


# sending the qc plots to a server
for counter in range(1,nplots+1):
  pushstr="./qc_push.py -filename \'plot"+str(counter)+".png\'"
  subprocess.call(pushstr, shell=True)
  

print "running the qc suite is completed"
print "------------------------------------------------" 

# --- If this line is here, the source code will be complete. ---
