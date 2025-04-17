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
#|	Last update by Christoph Saulder on the 27th of September 2012|
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
import os
import datetime
from time import gmtime, strftime

import matplotlib
import matplotlib.pyplot as plt

from qc_suite_lib import *

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
    QC_SUITE_DIR = './'

    varlistNames = ['qc_par', 'xfield', 'filter', 'yrange', 'instrument',
                    'selectpar', 'selectval', 'filtpar1', 'filtval1', 'mjdmin', 'mjdmax', 'upthld',
                    'lowthld', 'medplot', 'outfile', 'QC_SUITE_DIR']

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

    # here we assign values to the options passed directly
    # in the command line. These could be modified below
    # by the option file. We need this to call qc_plotter
    # with common options for all the plots. It will be
    # used for mjdmin and mjdmax.
    #
    for i in range(len(varlistNames)):
       thekey = '-' + varlistNames[i]
       if lineargs.has_key(thekey):
             exec(varlistNames[i] + " = " + str(lineargs[thekey]))

      
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
       lineargs = getopts(splitted)     


    # now we fill the rest of the variables in the
    # command line
    #
    for i in range(len(varlistNames)):
       thekey = '-' + varlistNames[i]
       if lineargs.has_key(thekey):
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
        instrumentfile = open(QC_SUITE_DIR+'instrument/'+instrument+".dat")
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
    infileName = QC_SUITE_DIR+instrument+"_qcdata.dat"

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
    icount=0

    # we prepare some variables to estimate the data range
    data_min_date = 10000000000
    data_max_date = -1
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
		icount=icount+1
                x_list[zchip].append(float(zfields[index_xfield]))
		num_date = matplotlib.dates.date2num(caldate( float(zfields[index_xfield]) ))
		date_list[zchip].append(num_date)
		#print date_list[zchip]
                y_list[zchip].append(float(zfields[index_zparvalue]))
		if num_date > data_max_date:
		   data_max_date = num_date
		if num_date < data_min_date:
		   data_min_date = num_date

    # we prepare the data range label for the graph
    #
    print "Data range: %f - %f\n" % (data_min_date, data_max_date,)  
    data_min_date_str = "%s" % (matplotlib.dates.num2date(data_min_date),)
    data_max_date_str = "%s" % (matplotlib.dates.num2date(data_max_date),)
    data_range_label = "Data range: %s -> %s" % (data_min_date_str[0:19],data_max_date_str[0:19],)
    print "%s" % (data_range_label,)
               
    
     
    ignorefileishere=0
    if os.path.isfile(QC_SUITE_DIR+"plotted_data/"+outfile+"_ignored.dat") :
       ignorefileishere=1
       ignorefile = open(QC_SUITE_DIR+"plotted_data/"+outfile+"_ignored.dat")
       ignorefile.seek(0)
       filestr_ign=[]
       filestr_ign = ignorefile.readlines()
       ignorefile.close()
       #print filestr_ign
       for i in range(len(filestr_ign)):
          filestr_ign[i] = filestr_ign[i].replace('\n','')
          #filestr_ign[i] = filestr_ign[i].replace('[','')
          #filestr_ign[i] = filestr_ign[i].replace(']','')
       #print filestr_ign
       ignorlist_a={}
       for i in range(len(filestr_ign)):
          exec('ignorlist_a['+str(i)+']='+filestr_ign[i])
       #print ignorlist_a[0][0][1]
       #print ignorlist_a[i][0]
     
    if icount > 0 :
       print "plotting data for "+qc_par
       matplotlib.rc("font", family="serif")
       matplotlib.rc("font", size=9)
       fig = plt.figure()
       fig.text(0.5,0.975,instrument+': '+qc_par+' vs '+xfield+' ('+filter+') ',
	 	  horizontalalignment='center',verticalalignment='top',fontsize='large',fontweight='bold')

       if index_xfield == index_mjdobs:
	   years    = matplotlib.dates.YearLocator()
	   months   = matplotlib.dates.MonthLocator()
	   weeks    = matplotlib.dates.WeekdayLocator()
	   yearsFmt = matplotlib.dates.DateFormatter('%Y-%m-%d')

       # here we prepare the plotting range
       if index_xfield == index_mjdobs:
          jd_start, jd_stop = getTimeIntervalMJD(QC_SUITE_DIR+"time.dat")
	  # matplotlib counts from year 1
	  date_start = jd_start - julian_date('1','1','1','0','0','0')
          date_stop  = jd_stop - julian_date('1','1','1','0','0','0')

       # we prepare the label to contain the plotting range
       #
       plot_date_start_str = "%s" % (matplotlib.dates.num2date(date_start),)
       plot_date_stop_str = "%s" % (matplotlib.dates.num2date(date_stop),)
       plot_range_label = "Plot range: %s -> %s" % (plot_date_start_str[0:10],plot_date_stop_str[0:10],)
       print "%s" % (plot_range_label,)

       fig.text(0.05,0.05,data_range_label+"\n"+plot_range_label,
                  horizontalalignment='left',verticalalignment='top',fontsize='small',fontweight='bold')

       # here we prepare the labe containing the time the plotting program was run

       plotter_timestamp_str = getVersion()+" executed: "+strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
       print plotter_timestamp_str
       fig.text(0.9,0.05,"     | \n"+plotter_timestamp_str,
                  horizontalalignment='right',verticalalignment='top',fontsize='small',fontweight='bold')


       saveplotted=[]
       saveoutliers=[]
       for i in range(NCHIPS):

	      
	   yvar = y_list[i]
 	   if index_xfield == index_mjdobs:
	      xvar  = date_list[i]
	   else:
	      xvar = x_list[i]
	   plot_tuple=zip(xvar, yvar) 
	   saveplotted.append(plot_tuple)
 	   ax = fig.add_subplot(zcodes[i][0], zcodes[i][1], zcodes[i][2])
	   if yrange != "":
	      ax.set_ylim(yrange[i])
	   ylimits=ax.get_ylim()

	   if yrange != "":
	      percentageforplot=(yrange[i][1]-yrange[i][0])*2.5/100
	      ycondition1 = numpy.greater_equal(yvar,yrange[i][1])
	      outofplot_up_indices = numpy.nonzero(numpy.select([ycondition1], [yvar]))
	      outofplot_up_x = numpy.take(xvar, outofplot_up_indices)[0]
	      outofplot_up_y = [(yrange[i][1]-percentageforplot)]*len(outofplot_up_x)
		 


	      ycondition2 = numpy.less_equal(yvar,yrange[i][0])
	      outofplot_down_indices = numpy.nonzero(numpy.select([ycondition2], [yvar]))
	      outofplot_down_x = numpy.take(xvar, outofplot_down_indices)[0]
      	      outofplot_down_y = [(yrange[i][0]+percentageforplot)]*len(outofplot_down_x)
		 
	   if ignorefileishere==1:
	      ignorlist_chip=ignorlist_a[i]
	      #print ignorlist_chip
	      ignore_x=[]
	      ignore_y=[]
	      ignore_y_true=[]
	      for ii in range(len(ignorlist_chip)):
		 ignore_x.append(ignorlist_chip[ii][0])
		 y_help=ignorlist_chip[ii][1]
		 if y_help > yrange[i][1] :
		    y_help = (yrange[i][1]-percentageforplot)		
	         if y_help < yrange[i][0] :
		    y_help = (yrange[i][0]+percentageforplot)	
		 ignore_y.append(y_help)
		 ignore_y_true.append(ignorlist_chip[ii][1])
	      #print ignore_x 
	      
	  # We plot here the data
	   if index_xfield == index_mjdobs:
	      line, = ax.plot_date(xvar,yvar,'.',color='#0000FF',picker=5) # blue points
              ax.set_xlim((date_start,date_stop))
	      if yrange != "":
	         if len(outofplot_up_x) > 0:
		    ax.plot_date(outofplot_up_x,outofplot_up_y,'^',color='#FF0000',picker=5) # red triangles
		    #print "up"
		    #print outofplot_up_x,outofplot_up_y
	         if len(outofplot_down_x) > 0:
	            ax.plot_date(outofplot_down_x,outofplot_down_y,'v',color='#FF0000',picker=5) # red triangles
	            
	         if ignorefileishere==1:
		    if len(ignore_x) > 0: 
		       ax.plot_date(ignore_x,ignore_y,'x',color='#000000',markersize=8,markeredgewidth=1) # black crosses
	            #print "down"
	            #print outofplot_down_x,outofplot_down_y
	      #for ii in range(len(yvar)) :
		 #if yvar[ii] < yrange[i][0] :
		    #ax.plot_date(xvar[ii],yrange[i][0],'v',picker=5)
		    #print str(xvar[ii])+" x "+str(yrange[i][0])+" / "+str(yvar[ii])
	         #if yvar[ii] > yrange[i][1] :
		    #ax.plot_date(xvar[ii],yrange[i][1],'^',picker=5)
		    #print str(xvar[ii])+" x "+str(yrange[i][1])+" / "+str(yvar[ii])
	     #  if yvar < yrange[0] :
	#	  line, = ax.plot_date(xvar,yrange[0],'v',picker=5)
	 #      else :
	#	  if yvar > yrange[1] :
	#	     line, = ax.plot_date(xvar,yrange[1],'^',picker=5)
	#	  else :
		     
	   else:
	      line, = ax.plot(xvar,yvar,'.',color='#0000FF',picker=5) # blue points
	      if yrange != "":
	         if len(outofplot_up_x) > 0:
	            ax.plot(outofplot_up_x,outofplot_up_y,'^',color='#FF0000',picker=5) # red triangles
	         if len(outofplot_down_x) > 0:
	            ax.plot(outofplot_down_x,outofplot_down_y,'v',color='#FF0000',picker=5) # red triangles
	            
	         if ignorefileishere==1:
		    if len(ignore_x) > 0: 
		       ax.plot(ignore_x,ignore_y,'x',color='#000000',markersize=8,markeredgewidth=1) # black crosses
	      #for ii in range(len(yvar)) :
		 #if yvar[ii] < yrange[i][0] :
		    #ax.plot_date(xvar[ii],yrange[i][0],'v',picker=5)
	         #if yvar[ii] > yrange[i][1] :
		    #ax.plot_date(xvar[ii],yrange[i][1],'^',picker=5)
	#       if yvar < yrange[0] :
	#	  line, = ax.plot(xvar,yrange[0],'v',picker=5)
	 #      else :
	#	  if yvar > yrange[1] :
	#	     line, = ax.plot(xvar,yrange[1],'^',picker=5)
	#	  else :
		     
	      
	   
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
	          if ignorefileishere==1:
		     if len(ignore_x) > 0: 	
		        ignoredoutlier=[0]*len(hioutliers_x)
                        for ii in range(len(hioutliers_x)):	
                           for iii in range(len(ignore_x)):
                              if round(hioutliers_x[ii],6) == round(ignore_x[iii],6) and round(hioutliers_y[ii],6) == round(ignore_y_true[iii],6):
				  ignoredoutlier[ii]=1
			for ii in range(len(hioutliers_x)):	
			   if ignoredoutlier[ii] == 0:
			      print "HIGH OUTLIERS in chip %s" % (find_key(chipIndex,i)[0],)
		              print hioutliers_x[ii], hioutliers_y[ii]
		              hicolor = 'pink'
                     else :
		        print "HIGH OUTLIERS in chip %s" % (find_key(chipIndex,i)[0],)
		        print hioutliers_x, hioutliers_y
		        hicolor = 'pink'
	       lowcolor = 'lightgreen'
	       condition2 = numpy.less_equal(yvar,lowthld[i])
	       lowoutliers_indices = numpy.nonzero(numpy.select([condition2], [yvar]))
	       lowoutliers_y = numpy.take(yvar, lowoutliers_indices)[0]
	       lowoutliers_x = numpy.take(xvar, lowoutliers_indices)[0]
	       if len(lowoutliers_x) > 0:
	          if ignorefileishere==1:
		     if len(ignore_x) > 0: 	
		        ignoredoutlier=[0]*len(lowoutliers_x)
                        for ii in range(len(lowoutliers_x)):	
                           for iii in range(len(ignore_x)):
                              if round(lowoutliers_x[ii],6) == round(ignore_x[iii],6) and round(lowoutliers_y[ii],6) == round(ignore_y_true[iii],6):
				  ignoredoutlier[ii]=1
			for ii in range(len(lowoutliers_x)):	
			   if ignoredoutlier[ii] == 0:
			      print "LOW OUTLIERS in chip %s" % (find_key(chipIndex,i)[0],)
		              print lowoutliers_x[ii], lowoutliers_y[ii]
		              lowcolor = 'pink'
                     else :
		        print "LOW OUTLIERS in chip %s" % (find_key(chipIndex,i)[0],)
		        print lowoutliers_x, lowoutliers_y
		        lowcolor = 'pink' 
	       # cannot add lists if one of them is empty, therefore just checking
	       if len(lowoutliers_x) > 0 and len(hioutliers_x) > 0:
	          alloutliers_x=hioutliers_x+lowoutliers_x
	          alloutliers_y=hioutliers_y+lowoutliers_y
                  out_tuple=zip(alloutliers_x, alloutliers_y)
               if len(lowoutliers_x) == 0 and len(hioutliers_x) > 0:
	          alloutliers_x=hioutliers_x
	          alloutliers_y=hioutliers_y
	          out_tuple=zip(alloutliers_x, alloutliers_y)
	       if len(lowoutliers_x) > 0 and len(hioutliers_x) == 0:
	          alloutliers_x=lowoutliers_x
	          alloutliers_y=lowoutliers_y
                  out_tuple=zip(alloutliers_x, alloutliers_y)
	       if len(lowoutliers_x) == 0 and len(hioutliers_x) == 0:  
	          alloutliers_x=hioutliers_x+lowoutliers_x
	          alloutliers_y=hioutliers_y+lowoutliers_y
	          out_tuple=zip(alloutliers_x, alloutliers_y)
	       saveoutliers.append(out_tuple)
        # we shadow the allowed area. Note that here we are shadowing green
        # the area outside the allowed region bounded by the thresholds.
        # For simplicity at the operation stage it will be useful to
        # shade ligh red/ping the areas where there are unaccounted for
        # outliers.
        #
	   if lowthld != "" and upthld != "":
	       dummyx = numpy.array((xlimits[0], xlimits[1]))
	       upper_bound = numpy.arange(len(dummyx))*0.0 + ylimits[1]
	       #print dummyx, upper_bound
	       lower_bound = numpy.arange(len(dummyx))*0.0 + upthld[i]
	       ax.fill_between(dummyx, lower_bound, upper_bound, facecolor=hicolor, alpha=0.5, label='allowed region')
	       upper_bound = numpy.arange(len(dummyx))*0.0 +  lowthld[i]
	       lower_bound = numpy.arange(len(dummyx))*0.0 + ylimits[0]
	       ax.fill_between(dummyx, lower_bound, upper_bound, facecolor=lowcolor, alpha=0.5, label='allowed region')

        # Here we plot the median line if requested
           
	   if medplot == True:
	      if ignorefileishere==0:
	         medlevel = numpy.median(yvar)
	         ax.axhline(y=medlevel,color='black',linestyle='-')
	      else:
		if len(ignore_x) > 0: 	
		   ignoredpoints=[0]*len(yvar)
                   for ii in range(len(yvar)):	
                      for iii in range(len(ignore_x)):
                         if round(xvar[ii],6) == round(ignore_x[iii],6) and round(yvar[ii],6) == round(ignore_y_true[iii],6):
			     ignoredpoints[ii]=1	
		   yvar_median=[]
		   for ii in range(len(yvar)):	
		      if ignoredpoints[ii]==0:
		         yvar_median.append(yvar[ii])
		   medlevel = numpy.median(yvar_median)
		   ax.axhline(y=medlevel,color='black',linestyle='-')
		else: 
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
    
       plt.savefig(QC_SUITE_DIR+"/plots/"+outfile+".png",dpi=300, facecolor='w',edgecolor='w', orientation='portrait',papertype='A4')
       
       #save plotted data and outliers to files
       plottedfile = open(QC_SUITE_DIR+"plotted_data/"+outfile+"_plotted.dat", 'w')
       #plottedfile.write(saveplotted) 
       for t in saveplotted:
          line = ', '.join("("+str(round(x[0],6))+", "+str(round(x[1],6))+")" for x in t)
          #print line
          plottedfile.write('[ '+line + ' ] \n')
       plottedfile.close()

       outlierfile = open(QC_SUITE_DIR+"plotted_data/"+outfile+"_outliers.dat", 'w')
       for t in saveoutliers:
          line = ', '.join("("+str(round(x[0],6))+", "+str(round(x[1],6))+")" for x in t)
          #print line
          outlierfile.write('[ '+line + ' ] \n')
       outlierfile.close()
       
       
    # show the plot if the parameter in the configuration file isn't 1
       pcfile = open(QC_SUITE_DIR+"config.dat")
       pcfile.seek(0)
       helpstring2 = pcfile.read()
       pcfile.close()
       if helpstring2.split('\n')[13] != '1':
	  plt.show()
    else:
       print "not enough data points to plot "+qc_par
    
    print "program qc_plotter terminated"
    print "------------------------------------------------"
    sys.exit(0)


# --- If this line is here, the source code will be complete. ---
