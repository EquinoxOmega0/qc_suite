#!/home/astro/qc_suite/installation/bin/python2.7

#------------------------------------------------------------------------
#|--------------------- qc_suite_lib.py -----------------------------------|
#|                                                                      |
#|      Library of needed procedures for qc_suite                       |
#|                                                                      |
#|----------------------------------------------------------------------|
#|                                                                      |
#|                                                                      |
#|----------------------------------------------------------------------|
#|                                                                      |
#|      Written by Fernando Selman and Christoph Saulder for ESO        |
#|                                                                      |
#|      Last update by Christoph Saulder on the 6th of November 2012    |
#|                                                                      |
#|----------------------------------------------------------------------|
#
import datetime
import time
import string

def getVersion():
  return "qc_suite v1.0 "

def getTimeIntervalMJD(zfile):
    # get time intervall from file
    timefile = open(zfile)
    timefile.seek(0)
    tf_read_str = timefile.read()
    timefile.close()
    timemode=tf_read_str.split('\n')[0]

    if timemode != '1': # see if it is a predefined intervall of two dates
       help_starttime=tf_read_str.split('\n')[1]
       help_stoptime=tf_read_str.split('\n')[2]
       starttime=help_starttime.split()
       stoptime=help_stoptime.split()
       jd_start=julian_date(starttime[0],starttime[1],starttime[2],starttime[3],starttime[4],starttime[5])
       jd_stop=julian_date(stoptime[0],stoptime[1],stoptime[2],stoptime[3],stoptime[4],stoptime[5])
    else: # if not, use the time from the file (which should be now) and the time spane given there to calculate the intervall
       help_starttime=tf_read_str.split('\n')[1]
       help_stoptime=tf_read_str.split('\n')[2]
       stoptime=help_stoptime.split()
       jd_stop=julian_date(stoptime[0],stoptime[1],stoptime[2],stoptime[3],stoptime[4],stoptime[5])
       jd_start=jd_stop-float(help_starttime)
    return jd_start, jd_stop

class QClog(object):
   """Class to read and handle QC1 log files"""
   def __init__(self,fileName,instrument, fields_list,ident_list,QC_SUITE_DIR):
        "Initialize the class by reading the QC log file"
        self.infile = fileName
        tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
	todayslogfile = open(tlfname, 'a' )
	now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
	todayslogfile.write(now+"QClog instance reading from %s\n" % self.infile)
	todayslogfile.close()

        try:
          infile = open(fileName, "r")
        except:
	  tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
	  todayslogfile = open(tlfname, 'a' )
	  now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
	  todayslogfile.write(now+"Problem reading %s\n" % self.infile)
	  todayslogfile.close()
          print "Problem reading %s" % self.infile
          sys.exit(0)
        linesList = infile.readlines()
        infile.close
        self.nlines = len(linesList)

	self.fields = "zTime " + " ".join(["%s" % el.replace(' ','.') for el in ident_list]) + ' QC.PARAM.NAME QC.PARAM.VALUE QC.PARAM.COMMENT '
	
	jd_start, jd_stop = getTimeIntervalMJD(QC_SUITE_DIR+"time.dat")
	
        #
	inGroup = "F"
	nRecords = 0
	zRecord = {}
	# notice that here we have to split the list with parameters with . in them
	# and only then we can replace in wach element of the list the dots by spaces.
	#
        zfield_str = ''
        for i in range(len(fields_list)):
            zfield_str = zfield_str + fields_list[i] + ','
	records_string = '(zTime, '+ zfield_str +' zParam, zValue, zComment)'
        for zLine in linesList:

	   if string.find(zLine[:-1],"START GROUP") != -1:
	     inGroup = "T"
	     nRecords += 1
	     for i in range(len(fields_list)):
		exec(fields_list[i] + " = '-' " )
             zParam = []
             zValue = []
             zComment = []
	     continue
	   # get observation date and transform it to Julian date
	   indexnumber=string.find(zLine[:-1],"DATE-OBS")
	   if indexnumber != -1:
	     observation_date=zLine[indexnumber+12:indexnumber+35]
	     d_year=observation_date[0:4]
	     d_month=observation_date[5:7]
	     d_day=observation_date[8:10]
	     d_hour=observation_date[11:13]
	     d_minute=observation_date[14:16]
	     d_second=observation_date[17:23]
	     date_jd=julian_date(d_year,d_month,d_day,d_hour,d_minute,d_second)

	   
           if string.find(zLine[:-1],"STOP GROUP") != -1:
             inGroup = "F"
	     # note that the following statement has been designed as zTime + <configurable fields> + QC parameter fields
	     # this will make it easier in the future to configure for any instrument
	     #
	     # only add data to the plotfile if it is in between the desired dates
	     if (date_jd > jd_start and  
	        date_jd < jd_stop):
	           exec('zRecord[nRecords] = ' + records_string)
	           continue 
	     else:
	           nRecords=nRecords-1
             
	   if inGroup == "T":
	     i1 = string.find(zLine[:-1],'>')
	     zTime = zLine[0:i1]
	     if       ( string.find(zLine[:-1],'>') != -1 and
                        string.find(zLine[:-1],'=') != -1 and
                        string.rfind(zLine[:-1],'/') != -1 ):
	        i2 = string.find(zLine[:-1],'=')
	        i3 = string.find(zLine[:-1],' ',i2+2)
                # here we process the QC parameters
                if string.find(zLine[i1+1:i2],'QC') != -1:
                   zParam.append(zLine[i1+1:i2])
                   zValue.append(zLine[i2+1:i3])
                   zComment.append(zLine[i3+1:-1])
		   continue
		# here we process the non QC parameters
		for i in range(len(fields_list)):
		   if string.find(zLine[i1+1:i2], ident_list[i].replace('.',' ')) != -1:
		      exec(fields_list[i] + " = str(" + zLine[i2+1:i3]+')' )
		      continue
	self.record = zRecord

def getopts(argv):
   opts = {}
   while argv:
	#print argv
	if len(argv) > 1:
           if argv[0][0] == '-':
              opts[argv[0]] = argv[1]
              argv = argv[2:]
           else:
              argv = argv[1:]
	else:
	   return opts
   return opts

def getFileList(argv):
   """Read list of files from command line.

      After reading all valid options,
      we assume that the rest of the
      parameters are files.
   """
   fileList = []
   while argv:
      if argv[0][0] != '-':
        fileList.append(argv[0])
        argv = argv[1:]
      else:
        argv = argv[2:]
   fileList = fileList[1:]
   return fileList

def getoptsFromFile(fileName):
   """Read options from a file.

      Reads a set of options from a file instead
      of the command line. This should simplify
      execution of scripts in batch mode.
   """
   opts = {}
   try:
      optfile = open(fileName,'rb')
   except:
      print "could not open %s" % (fileName,)
      tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
      todayslogfile = open(tlfname, 'a' )
      now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
      todayslogfile.write(now+"could not open %s\n" % (fileName,))
      todayslogfile.close()
      sys.exit(0)
   inLines = optfile.readlines()
   for aLine in inLines:
      aLine = aLine[:-1] # strip new line character
      aList = string.split(aLine)
      if len(aList) != 2:
        print "inproper format line in file %s" % (fileName,)
        tlfname="QC_suite_"+time.strftime("%Y-%m-%d", time.localtime())+".log"
        todayslogfile = open(tlfname, 'a' )
        now=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" >>> "
        todayslogfile.write(now+"inproper format line in file %s\n" % (fileName,))
        todayslogfile.close()
        sys.exit(0)
      opts[aList[0]] = aList[1]
   return opts

# MJD routines
import math
MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours

def base60_to_decimal(xyz,delimiter=None):
  """Decimal value from numbers in sexagesimal system.

 The input value can be either a floating point number or a string
 such as "hh mm ss.ss" or "dd mm ss.ss". Delimiters other than " "
 can be specified using the keyword ``delimiter``.
 """
  divisors = [1,60.0,3600.0]
  xyzlist = str(xyz).split(delimiter)
  sign = -1 if xyzlist[0].find("-") != -1 else 1
  xyzlist = [abs(float(x)) for x in xyzlist]
  decimal_value = 0

  for i,j in zip(xyzlist,divisors): # if xyzlist has <3 values then
                                    # divisors gets clipped.
    decimal_value += i/j

  decimal_value = -decimal_value if sign == -1 else decimal_value
  return decimal_value

def decimal_to_base60(deci,precision=1e-8):
  """Converts decimal number into sexagesimal number parts.

 ``deci`` is the decimal number to be converted. ``precision`` is how
 close the multiple of 60 and 3600, for example minutes and seconds,
 are to 60.0 before they are rounded to the higher quantity, for
 example hours and minutes.
 """
  sign = "+" # simple putting sign back at end gives errors for small
             # deg. This is because -00 is 00 and hence ``format``,
             # that constructs the delimited string will not add '-'
             # sign. So, carry it as a character.
  if deci < 0:
    deci = abs(deci)
    sign = "-"

  frac1, num = math.modf(deci)
  num = int(num) # hours/degrees is integer valued but type is float
  frac2, frac1 = math.modf(frac1*60.0)
  frac1 = int(frac1) # minutes is integer valued but type is float
  frac2 *= 60.0 # number of seconds between 0 and 60

  # Keep seconds and minutes in [0 - 60.0000)
  if abs(frac2 - 60.0) < precision:
    frac2 = 0.0
    frac1 += 1
  if abs(frac1 - 60.0) < precision:
    frac1 = 0.0
    num += 1

  return (sign,num,frac1,frac2)

def julian_date(year,month,day,hour,minute,second):
  """Given year, month, day, hour, minute and second return JD.

 ``year``, ``month``, ``day``, ``hour`` and ``minute`` are integers,
 truncates fractional part; ``second`` is a floating point number.
 For BC year: use -(year-1). Example: 1 BC = 0, 1000 BC = -999.
 """
  MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours

  year, month, day, hour, minute =\
  int(year),int(month),int(day),int(hour),int(minute)

  if month <= 2:
    month +=12
    year -= 1

  modf = math.modf
  # Julian calendar on or before 1582 October 4 and Gregorian calendar
  # afterwards.
  if ((10000L*year+100L*month+day) <= 15821004L):
    b = -2 + int(modf((year+4716)/4)[1]) - 1179
  else:
    b = int(modf(year/400)[1])-int(modf(year/100)[1])+\
        int(modf(year/4)[1])

  mjdmidnight = 365L*year - 679004L + b + int(30.6001*(month+1)) + day

  fracofday = base60_to_decimal(\
    " ".join([str(hour),str(minute),str(second)])) / 24.0

  return MJD0 + mjdmidnight + fracofday

def caldate(mjd):
  """Given mjd return calendar date.

 Retrns a tuple (year,month,day,hour,minute,second). The last is a
 floating point number and others are integers. The precision in
 seconds is about 1e-4.

 To convert jd to mjd use jd - 2400000.5. In this module 2400000.5 is
 stored in MJD0.
 """
  MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours

  modf = math.modf
  a = int(mjd+MJD0+0.5)
  # Julian calendar on or before 1582 October 4 and Gregorian calendar
  # afterwards.
  if a < 2299161:
    b = 0
    c = a + 1524
  else:
    b = int((a-1867216.25)/36524.25)
    c = a+ b - int(modf(b/4)[1]) + 1525

  d = int((c-122.1)/365.25)
  e = 365*d + int(modf(d/4)[1])
  f = int((c-e)/30.6001)

  day = c - e - int(30.6001*f)
  month = f - 1 - 12*int(modf(f/14)[1])
  year = d - 4715 - int(modf((7+month)/10)[1])
  fracofday = mjd - math.floor(mjd)
  hours = fracofday * 24.0

  sign,hour,minute,second = decimal_to_base60(hours)
  usec = int((second - int(second))*1000000.0)

  return datetime.datetime(year,month,day,int(sign+str(hour)),minute,int(second),usec, None)

def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val]


# --- If this line is here, the source code will be complete. ---
