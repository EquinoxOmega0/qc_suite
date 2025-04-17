#!/usr/bin/python2.7
#
#------------------------------------------------------------------------
#|--------------------- qc_parser.py -----------------------------------|
#|									|
#|	This program creates output for easy plotting.			|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	It reads data from a file and writes the information which	|
#|	is required for the plotting into file. Furthermore, it only	|
#|	uses data within a given time intervall. 			|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	Written by Fernando Selman and Christoph Saulder for ESO	|
#|									|
#|	Last update by Christoph Saulder on the 6th of November 2012    |
#|									|
#|----------------------------------------------------------------------|
#

import string
import sys
from   sys          import argv
import os.path
import time
import datetime
import matplotlib.dates as mpdate
import datetime
from qc_suite_lib import *

if __name__ == "__main__":

    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write(now+"------------------------------------------------\n")
    todayslogfile.write(now+"program qc_parser started\n")
    todayslogfile.close()


    instrument = 'wfi'
    QC_SUITE_DIR = './'
    varlistNames = ['instrument','QC_SUITE_DIR']

    # if there is a -help option we just print the general help message
    # notice that this is the only no-argument option allowed.
    #
    # if we are creating a fake dataset we do that and exit
    #
    for token in argv:
       if token == '-help':
         printHelpMessage()
         sys.exit(0)

    # parsing options
    lineargs = getopts(argv)

    # if there is an optfile we read the variable values from it
    #
    
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
             #print thekey + ' = ' + lineargs[thekey]
             exec(varlistNames[i] + " = " + str(lineargs[thekey]))

    # now we strip all the commands and their arguments and
    # whatever is left will be considered to be the list
    # of input files
    #
    parsedFileList =  getFileList(argv)

    if len(parsedFileList) != 1:
    #   printUsageMessage()
       sys.exit(0)
    infile  = QC_SUITE_DIR+parsedFileList[0]

    
     # read from an instrument configuration file
    try:
        tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
        todayslogfile = open(tlfname, 'a' )
        now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
        todayslogfile.write(now+"Reading from %s\n" % (QC_SUITE_DIR+"instrument/"+instrument+"2.dat",))
        todayslogfile.close()
        instrumentfile = open(QC_SUITE_DIR+"instrument/"+instrument+"2.dat")
	instrumentfile.seek(0)
	readstring=instrumentfile.read()
	helpstring= readstring.split('\n')
	instrumentfile.close()
	tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
        todayslogfile = open(tlfname, 'a' )
        now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
        todayslogfile.write(now+"done\n")
        todayslogfile.close()
    except Exception, ee:
     print "unknown instrument (error: %s)" % (ee)
     tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
     todayslogfile = open(tlfname, 'a' )
     now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
     todayslogfile.write(now+"unknown instrument (error: %s)\n" % (ee))
     todayslogfile.close()
     sys.exit(0)
    
    fields_string = helpstring[0]
    fields_list = fields_string.split()
    length_rs = len(helpstring)
    ident_list = []
    for i in range(1,length_rs):
	    ident_list.append(helpstring[i])
    
    o = QClog(infile,instrument,fields_list,ident_list,QC_SUITE_DIR)

    # !!! ENHANCE: we should modify this so that if the file does not
    # !!! ENHANCE: exists it creates it with a proper heading
    # !!! ENHANCE: If it exists it checks that it has the proper heading.
    # !!! ENHANCE: For now just a straight opening for appending.
    # !!! ENHANCE: It should also be instrument independent
    # -------------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Isn't already done here ????????????????????????
    
    outfileName = QC_SUITE_DIR+instrument + '_qcdata.dat'
    try:
      if os.path.isfile(outfileName):
	 outfile = open(outfileName, "r")
 	 zlines = outfile.readlines()
	 if zlines[0][0] != '#':
	    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
            todayslogfile = open(tlfname, 'a' )
            now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
            todayslogfile.write(now+"%s does not have a proper header\n" % (outfile,))
            todayslogfile.close()
	    print "%s does not have a proper header" % (outfile,)
	    outfile.close()
	    sys.exit(0)
	 else:
	    headerList = zlines[0][1:-1]

	 outfile.close()
         outfile = open(outfileName, "a")
      else:
	 tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
         todayslogfile = open(tlfname, 'a' )
         now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
         todayslogfile.write(now+"File %s does not exist. Creating it with proper headers.\n" % (outfileName,))
         todayslogfile.close()
	 outfile = open(outfileName, "a")
	 print >>outfile, '# nRecord '+ o.fields
	 tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
         todayslogfile = open(tlfname, 'a' )
         now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
         todayslogfile.write(now+'# '+ o.fields+"\n")
         todayslogfile.close()
    except:
      print "-Problem reading %s" % outfileName
      tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
      todayslogfile = open(tlfname, 'a' )
      now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
      todayslogfile.write(now+"-Problem reading %s\n" % outfileName)
      todayslogfile.close()
      sys.exit(0)

    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write(now+"writing to %s\n" % (outfileName))
    todayslogfile.close()
    number_of_fields = len(o.fields.split())
    #print "Writing %d fields per line" % (number_of_fields,)
    zindex = 1
    zstring = "(zkey, o.record[zkey][1], o.record[zkey][0], "
    zformat_string = '"%s %s %s '
    for afield in o.fields.split()[2:-3]:
	zindex += 1
	zstring = zstring + 'o.record[zkey][' + str(zindex)+'], '
	zformat_string += "%s "

    zstring = zstring + "o.record[zkey]["+str(zindex+1)+"][i].lstrip().rstrip().replace(' ','.'), o.record[zkey]["+str(zindex+2)+"][i],)"
    zformat_string += '%s %s"'
  
    for zkey in o.record.keys():
	for i in range(len(o.record[zkey][zindex+1])):
	  
	   # !!! ENHANCE: here we should filter the data previously writen by comparing
	   # !!! ENHANCE: with a dictionary build using the wfi_data file
	   #
	   # old: (zDATE, zTime, zMJD, zExtension, zFilter, zParam, zValue, zComment, zTPLID, zARCFILE)
 	   #       0      1      2     3           4        5       6       7         8       9
	   # new: (zTime, zDATE, zMJD, zExtension, zFilter, zTPLID, zARCFILE, zParam, zValue, zComment)
	   #       0      1      2     3           4        5       6         7       8       9
	   ##exec('print '+ zformat_string + ' % ' + zstring)
	   # !!!!!!!!!!!!!! NOW UNNECESSARY, isn't it?????????????????????????????????????????????????
	   
	   exec('print >>outfile, '+ zformat_string + ' % ' + zstring)
    outfile.close()
    
    tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
    todayslogfile = open(tlfname, 'a' )
    now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
    todayslogfile.write(now+"program qc_parser terminated\n")
    todayslogfile.write(now+"------------------------------------------------\n")
    todayslogfile.close()

    sys.exit(0)



# --- If this line is here, the source code will be complete. ---
