#!/home/astro/qc_suite/installation/bin/python2.7
#
#------------------------------------------------------------------------
#|--------------------- qc_prepare.py ----------------------------------|
#|									|
#|	This program makes the necessary preparation for qc_parser.	|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	This program looks reads the system time and writes it into	|
#|	a file or sets up a preselected time intervall. In addition	|
#|	to that, it deletes the qcdata file save the header.		|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	Written by Christoph Saulder and Fernando Selman for ESO	|
#|									|
#|      Last update by Christoph Saulder on the 6th of November 2012    |
#|									|
#|----------------------------------------------------------------------|
#

import time
import os
import sys
import datetime
from   sys import argv
from qc_suite_lib import *

def printHelpMessage():
   print """\n\n        GENERAL HELP:

        This routine prepare some files for qc_suite

        DEPENDENCIES:


        ALGORITHM:


        EXAMPLES:

                1. qc_prepare.py -QC_SUITE_DIR \'/diska/home/astro/qc_suite\'

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
todayslogfile.write(now+"program qc_prepare started\n")
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


# read data from configuration file
configfile = open(QC_SUITE_DIR+"config.dat")
configfile.seek(0)
filestr = configfile.read()
configfile.close()

manuell=filestr.split('\n')[8]
instrument=filestr.split('\n')[20]


timedata=[]

if manuell != '1': # if the time intervalls are manuelly defined, simply write them to the time file
  
  timedata.append(filestr.split('\n')[8]+'\n')
  timedata.append(filestr.split('\n')[9]+'\n')
  timedata.append(filestr.split('\n')[10]+'\n')
  
 
else: # if they are not, get the current time and and write it and the predefined intervall to the time file
  timespan=filestr.split('\n')[9]
  datetime=time.strftime("%Y %m %d %H %M %S", time.localtime())

  timedata.append(manuell+'\n')
  timedata.append(timespan+'\n')
  timedata.append(datetime+'\n')
  
# do the actual writing to the time file
timefile = open(QC_SUITE_DIR+"time.dat", 'w')
timefile.writelines(timedata)
timefile.close()

# remove the old qcdata file
qcdata_filename=filestr.split('\n')[11]
deletefilecommand="rm  %s" %(QC_SUITE_DIR+qcdata_filename)
tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
todayslogfile = open(tlfname, 'a' )
now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
todayslogfile.write(now+deletefilecommand+"\n")
todayslogfile.close()
os.system(deletefilecommand)


# getting the right header for the instrument in use
tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
todayslogfile = open(tlfname, 'a' )
now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
todayslogfile.write(now+"reading "+QC_SUITE_DIR+'instrument/'+instrument+'2.dat'+"\n")
todayslogfile.close()
headerfile= open(QC_SUITE_DIR+'instrument/'+instrument+'2.dat')
headerfile.seek(0)
instrumentinformation = headerfile.read()
headerfile.close()

iistring=instrumentinformation.split('\n')
for i in range(1,len(iistring)):
   iistring[i] = iistring[i].replace(' ', '.')

newstring=''
for i in range(1,(len(iistring)-1)):
   newstring=newstring+' '+iistring[i]

headerstr='# nRecord zTime'+newstring+' QC.PARAM.NAME QC.PARAM.VALUE QC.PARAM.COMMENT\n'

#create a new one with the proper header
qcdatafile = open(QC_SUITE_DIR+qcdata_filename, 'w')
qcdatafile.writelines(headerstr)
qcdatafile.close()


tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
todayslogfile = open(tlfname, 'a' )
now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
todayslogfile.write(now+"program qc_prepare terminated\n")
todayslogfile.write(now+"------------------------------------------------\n")
todayslogfile.close()



# --- If this line is here, the source code will be complete. ---
