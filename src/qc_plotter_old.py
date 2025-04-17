#!/home/astro/qc_suite/installation/bin/python2.7
#
#------------------------------------------------------------------------
#|--------------------- qc_plotter.py ----------------------------------|
#|									|
#|	This program simply plots the data.				|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	The values for each chip are plotted seperately. The 		|
#|	plotting features can be given as options.			|
#|						 			|
#|									|
#|----------------------------------------------------------------------|
#|									|
#|	Written by Fernando Selman and Christoph Saulder for ESO	|
#|									|
#|	Last update by Christoph Saulder on the 23rd of March 2012	|
#|									|
#|----------------------------------------------------------------------|
#


import sys
import operator
import string
import glob
import copy
from   sys          import argv
import numpy
import getopt


import matplotlib
import matplotlib.pyplot as plt

from qc_parser import *

def printUsageMessage():
   print"""\n\n USAGE: qc_plotter.py <options> <zpPrepare-output-file>
        where options can be any, all, or none of:

                -help                              # print general help message
                -qc_par         <s> [QC.ZEROPOINT] # parameter to plot
                -xfield        <s> [MJDOBS]       # name of x_variable to plot against
                -filter        <s> []             # name of filter to choose
                -yrange         <s> [[(23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5)]]       # yranges tuple
		-selectpar	<s> []		# name of parameters to select data from
		-selectval	<s> []		# value of selectpar to choose
                -instrument     <s> [wfi]       # instrument
                -filtpar1       <s> []          # parameter to use for filtering data
                -filtval1       <s> []          # value of filtpar1 parameter for data to be included 
                -mjdmin         <s> [-1]        # minimum MJD-OBS for data to be included
                -mjdmax         <s> [1000000]   # max MJD-OBS
                -upthld         <list> []       # list of upper threshold values
                -lowthld        <list> []       # list of low threshold values
                -medplot       <bool> [False}   # should the median line be plotted
                -outfile 	<s> [plot.png]  # name of the output file of the plot

['qc_par', 'xfield', 'filter', 'yrange', 'instrument',
                    'selectpar', 'selectval', 'filtpar1', 'filtval1', 'mjdmin',
'mjdmax', 'upthld',
                    'lowthld', 'medplot']
        The numbers in the square brackets are the default values. For further
        help call the program with the option -help.\n\n
        """
   return

def printHelpMessage():
   print """\n\n	GENERAL HELP:

	This routine is used to plot selected QC parameters
	that have been previously extracted using qc_parser.py
	from an QC ops log file. The current version is
	coded with WFI in mind but attempting to do it
	as general as possible

	DEPENDENCIES:

		qc_parser.py	# script used to parse opslog files

	ALGORITHM:


	EXAMPLES:

		1. qc_plotter.py -qc_par "QC.ZEROPOINT" -xfield "MJDOBS" -filter "BB#I/203_ESO879" -yrange "[(23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5), (23.5,24.5)]"

		\n\n
	"""
   return

if __name__ == "__main__":

    print "------------------------------------------------"
    print "program qc_plotter started"
    instrument = 'wfi'
    qc_par  = "QC.ZEROPOINT"
    xfield = "MJD-OBS"
    filter = ""
    yrange = ""
    selectpar = ""
    selectval = ""
    filtpar1 = ""
    filtval1 = ""
    mjdmin = "-1.0"
    mjdmax = "100000000.0"
    upthld = ""
    lowthld = ""
    medplot = False
    outfile = "plot.png"

    varlistNames = ['qc_par', 'xfield', 'filter', 'yrange', 'instrument',
                    'selectpar', 'selectval', 'filtpar1', 'filtval1', 'mjdmin', 'mjdmax', 'upthld',
                    'lowthld', 'medplot', 'outfile']

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
       print splitted
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


 # read from an instrument configuration file
    try:
        instrumentfile = open('instrument/'+instrument+".dat")
	instrumentfile.seek(0)
	readstring=instrumentfile.read()
	helpstring= readstring.split('\n')
	instrumentfile.close()
    except Exception, ee:
     print "unknown instrument (error: %s)" % (ee)
     sys.exit(0)
     
    NCHIPS = int(helpstring[1])
    
    chipIndex = {}
    
    for i in range(0,NCHIPS):
       iii=i+3
       chipIndex[helpstring[iii]] = i
       
    zcodes = [[0 for col in range(3)] for row in range(NCHIPS)]
    for i in range(0,NCHIPS):
       iii=NCHIPS+4+i*4
       zcodes[i][0]=int(helpstring[iii])
       zcodes[i][1]=int(helpstring[iii+1]) 
       zcodes[i][2]=int(helpstring[iii+2])
       
    i=NCHIPS*5+4
    xtick_codes = map(int,helpstring[i].split())
    i=i+2
    ytick_codes = map(int,helpstring[i].split())
    

    # here we read the wfi_data.dat file
    infileName = instrument+"_qcdata.dat"
    try:
       infile = open(infileName, "r")
    except:
       print "Problem reading %s" % infile
       sys.exit(0)
    linesList = infile.readlines()
    infile.close
    nlines = len(linesList)

    x_list    = {}
    y_list    = {}
    date_list = {}
    for i in range(NCHIPS):
       x_list[i]    = []
       date_list[i] = []
       y_list[i]    = []

    if linesList[0][0] != '#':
	print "File %s does not contain a header line." % (infileName,)
    else:
        zfieldList = linesList[0][1:-1].split()

    # here we fill the vectors containing the plot
    if instrument == 'vimos':
       index_zchip     = zfieldList.index('OCS.CON.QUAD')
    elif instrument == 'wfi':
       index_zchip     = zfieldList.index('EXTNAME')
    elif instrument == 'vircam':
       index_zchip     = zfieldList.index('EXTNAME')
    elif instrument == 'ocam':
       index_zchip     = zfieldList.index('EXTNAME')
    index_xfield      = zfieldList.index(xfield)
    index_zparname  = zfieldList.index('QC.PARAM.NAME')
    index_zparvalue = zfieldList.index('QC.PARAM.VALUE')
    index_filter   = zfieldList.index('INS.FILT1.NAME')
    index_mjdobs    = zfieldList.index('MJD-OBS')
    if filtpar1 != "":
        index_filtpar1  =  zfieldList.index(filtpar1)
    if (selectpar != '' and selectval != ''):
        index_selectpar = zfieldList.index(selectpar)
    for zline in linesList:
       if zline[0] != '#':
          zfields=zline[:-1].split()
          zchip = chipIndex[zfields[index_zchip]]

	  # we check whether it has the proper filter
	  if  string.find(zfields[index_filter],filter) == -1 :
		continue

	  # here we filter by mjdobs
	  if  float(zfields[index_mjdobs]) < float(mjdmin) or \
	      float(zfields[index_mjdobs]) > float(mjdmax)  :
		continue

	  # here we check whether filpar1 is ok
	  if filtpar1 != "" and string.find(zfields[index_filtpar1],filtval1) == -1:
		continue

	  # here we check the selectpar, selectval pair
	  if selectpar != '' and selectval != '' and string.find(zfields[index_selectpar],selectval) == -1 :
		continue

	  if ( zfields[index_zparname] == qc_par ):
                x_list[zchip].append(float(zfields[index_xfield]))
		date_list[zchip].append(matplotlib.dates.date2num(caldate( float(zfields[index_xfield]) )))
		#print date_list[zchip]
                y_list[zchip].append(float(zfields[index_zparvalue]))

                
                
    # !!! ENHANCE: here we should have a filtering procedure, such as 3sigma
    # !!! ENHANCE: we should also plot the threshold lines and have a mechanism
    # !!! ENHANCE: to detect when a measurement is violating the threshold and we
    # !!! ENHANCE: should indicate this with a red or green warning light.
    
    # !!!!!!!!!!!!! How exactely??????????????????????????????????  
    

    matplotlib.rc("font", family="serif")
    matplotlib.rc("font", size=9)
    fig = plt.figure()
    fig.text(0.5,0.975,instrument+': '+qc_par+' vs '+xfield+' ('+filter+') ',
                 horizontalalignment='center',verticalalignment='top')

    if index_xfield == index_mjdobs:
        years    = matplotlib.dates.YearLocator()
        months   = matplotlib.dates.MonthLocator()
        weeks    = matplotlib.dates.WeekdayLocator()
        yearsFmt = matplotlib.dates.DateFormatter('%Y-%m-%d')

    for i in range(NCHIPS):
        yvar = y_list[i]
        if index_xfield == index_mjdobs:
           xvar  = date_list[i]
	else:
	   xvar = x_list[i]

        ax = fig.add_subplot(zcodes[i][0], zcodes[i][1], zcodes[i][2])
	if yrange != "":
           ax.set_ylim(yrange[i])
        ylimits=ax.get_ylim()

	# We plot here the data
	if index_xfield == index_mjdobs:
            line, = ax.plot_date(xvar,yvar,'.',picker=5)
	else:
	    line, = ax.plot(xvar,yvar,'.',picker=5)
        xlimits=ax.get_xlim()

        # We plot here the thresholds, if any
        # upper threshold
        if upthld != "":

            ax.axhline(y=float(upthld[i]),color='blue',linestyle=':')
        #
	if lowthld != "":
            ax.axhline(y=float(lowthld[i]),color='blue',linestyle=':')

        # here we identify outliers
        #
        if lowthld != "" and upthld != "":
            hicolor = 'lightgreen'
            condition1 = numpy.greater_equal(yvar,upthld[i])
            hioutliers_indices = numpy.nonzero(numpy.select([condition1], [yvar]))
            hioutliers_y = numpy.take(yvar, hioutliers_indices)[0]
            hioutliers_x = numpy.take(xvar, hioutliers_indices)[0]
            if len(hioutliers_x) > 0:
                print "HIGH OUTLIERS in chip %s" % (find_key(chipIndex,i)[0],)
                print hioutliers_x, hioutliers_y
                hicolor = 'pink'

            lowcolor = 'lightgreen'
            condition2 = numpy.less_equal(yvar,lowthld[i])
            lowoutliers_indices = numpy.nonzero(numpy.select([condition2], [yvar]))
            lowoutliers_y = numpy.take(yvar, lowoutliers_indices)[0]
            lowoutliers_x = numpy.take(xvar, lowoutliers_indices)[0]
            if len(lowoutliers_x) > 0:
                print "LOW OUTLIERS in chip %s" % (find_key(chipIndex,i)[0],)
                print hioutliers_x, hioutliers_y
                lowcolor = 'pink'

        # we shadow the allowed area. Note that here we are shadowing green
        # the area outside the allowed region bounded by the thresholds.
        # For simplicity at the operation stage it will be useful to
        # shade ligh red/ping the areas where there are unaccounted for
        # outliers.
        #
        if lowthld != "" and upthld != "":
            dummyx = numpy.array((xlimits[0], xlimits[1]))
            upper_bound = numpy.arange(len(dummyx))*0.0 + ylimits[1]
            print dummyx, upper_bound
            lower_bound = numpy.arange(len(dummyx))*0.0 + upthld[i]
            ax.fill_between(dummyx, lower_bound, upper_bound, facecolor=hicolor, alpha=0.5, label='allowed region')
            upper_bound = numpy.arange(len(dummyx))*0.0 +  lowthld[i]
            lower_bound = numpy.arange(len(dummyx))*0.0 + ylimits[0]
            ax.fill_between(dummyx, lower_bound, upper_bound, facecolor=lowcolor, alpha=0.5, label='allowed region')

        # Here we plot the median line if requested
        #
        if medplot == True:
            medlevel = numpy.median(yvar)
            ax.axhline(y=medlevel,color='black',linestyle='-')

        # if we are plotting against MJD-OBS we create
        # easier to anderstand x axis labels
        #
	if index_xfield == index_mjdobs:
	   ax.xaxis.set_major_locator(months)
	   ax.xaxis.set_major_formatter(yearsFmt)
	   ax.xaxis.set_minor_locator(weeks)
	   ax.autoscale_view()
	   ax.xaxis.grid(True, 'minor')
	   #ax.grid(True)
	   fig.autofmt_xdate()
	ax.set_title(find_key(chipIndex,i)[0],fontsize=9)
        if xtick_codes[i] == 0:
           plt.setp(ax, xticklabels=[])
	if ytick_codes[i] == 0:
           plt.setp(ax, yticklabels=[])



    def onpick(event):
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        print 'onpick points:', zip(xdata[ind], ydata[ind])
    if index_xfield == index_mjdobs:
       fig.autofmt_xdate()
    fig.canvas.mpl_connect('pick_event', onpick)

    # we produce a graphic file.
    #
    plt.savefig(outfile,dpi=300, facecolor='w',edgecolor='w', orientation='portrait',papertype='A4')
    
    
    # show the plot if the parameter in the configuration file isn't 1
    pcfile = open("config.dat")
    pcfile.seek(0)
    helpstring2 = pcfile.read()
    pcfile.close()
    if helpstring2.split('\n')[13] != '1':
      plt.show()
    
    
    print "program qc_plotter terminated"
    print "------------------------------------------------"
    sys.exit(0)


# --- If this line is here, the source code will be complete. ---
