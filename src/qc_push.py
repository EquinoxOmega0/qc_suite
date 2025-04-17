#!/home/astro/qc_suite/installation/bin/python2.7
#
#------------------------------------------------------------------------
#|--------------------- qc_push.py -------------------------------------|
#|									|
#|	This program sends the plot to a server.		|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	This program looks simply pushes a plot file, which was 	|
#|	created by qc_plotter, to a server using scp and to the	|
#|	plots folder.							|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	Written by Christoph Saulder and Fernando Selman for ESO	|
#|									|
#|	Last update by Christoph Saulder on the 27th of September 2012|
#|									|
#|----------------------------------------------------------------------|
#

import sys
import operator
import string
import copy
import shutil 
import os
import subprocess
from   sys          import argv
import numpy
import getopt
from qc_parser import *
import paramiko


if __name__ == "__main__":
 print "------------------------------------------------"
 print "program qc_push started"

    # parsing options
 try:
   lineargs = getopts(argv)
 except Exception, e:
    print "options not recognized (error: %s)" % (e)
    sys.exit(0)

# get the name of the file, which is to be sent to the server
 if lineargs.has_key('-filename'):
     movefilename=lineargs['-filename']

 if lineargs.has_key('-QC_SUITE_DIR'):
     QC_SUITE_DIR=lineargs['-QC_SUITE_DIR']

 if os.path.isfile(QC_SUITE_DIR+"plots/"+movefilename) : 
# load configuration file
    configfile = open(QC_SUITE_DIR+"config.dat")
    configfile.seek(0)
    filestr = configfile.read()
    configfile.close()
 
# get pathes for data from filestr
    targetfolder=filestr.split('\n')[15]
    hostname= filestr.split('\n')[16]
    usn=filestr.split('\n')[17]
    pw=filestr.split('\n')[18]


    print "copying file to: "
    print usn+'@'+hostname+':'+targetfolder+'/'+movefilename

#connecting to server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(hostname, username=usn, password=pw)


# do the actual pushing
    ftp = ssh.open_sftp()
    info_str = "copying %s to %s" % (QC_SUITE_DIR+"/plots/"+movefilename,targetfolder+'/'+movefilename,)
    print info_str
    ftp.put(QC_SUITE_DIR+"/plots/"+movefilename,targetfolder+'/'+movefilename)
    ftp.close()
 

# moves plot to folder plots
#    plotfoldercp_string='mv '+movefilename+" "+QC_SUITE_DIR+"plots/."
#    print plotfoldercp_string
#    subprocess.call(plotfoldercp_string, shell=True)
 
 else :
    print "file "+movefilename+"does not exist"


 print "program qc_push terminated"
 print "------------------------------------------------" 
 sys.exit(0)
 
 
 # --- If this line is here, the source code will be complete. ---
