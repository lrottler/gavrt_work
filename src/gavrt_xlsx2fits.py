#!/home/lrottler/anaconda2/bin/python
##########!/usr/bin/python###########

#Program to convert raw data Excel files delivered from GAVRT (Goldstone Apple
#Valley Radio Telescope) into both Excel and Fits files, one each per scan.

#The code is run from the command line with 2 arguments
#Author: Lee Rottler
#Delivered: August 4, 2016
#Release Date: TBD

#program name: gavrt_xlsx2fits.py
#arg1 - relative (or absolute) path to file concatenated with data filemame
#arg2 - path name to desired output directory.

#Execution: ./gavrt_xlsx2fits.py arg1 arg2  (assumes code is in folder gavrt_work/src)
#Example execution: ./gavrt_xlsx2fits.py ../data/data_107_2016.xlsx ../data

import sys
import os, os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import table


arg_list = sys.argv
datafile = arg_list[1]
out_path = arg_list[2]

# This section reads original large Excel file and splits it into individual
# scans and writes the scans to disk as seperate Excel files in .xlsx fromat

dataframe = pd.read_excel(datafile)
col_headers = list(dataframe.columns.values)

def utc2secs(utc):
    '''
       Convert utc in hrs:min:sec format to seconds
       input: time in "hrs:min:sec"
        output: funcution returns time in seconds
    '''

    utcsecs = []
    for time in utc:
        time = str(time)
        hrs = int(time[0:2])
        min = int(time[3:5])
        sec = int(time[6:8])
        utcsecs.append(hrs*3600 + min*60 + sec)
    return utcsecs

utc_1 = dataframe['utc.1']     #Begin scan time vector
utc_2 = dataframe['utc.2']     #End scan time vector

utc1 = utc2secs(utc_1)
utc2 = utc2secs(utc_2)
utcdiff = np.subtract(utc2, utc1)

#Creat list of begin scan timepoints
cnt = 0
btime = utcdiff[0]
timepoints = [cnt]
for dtime in utcdiff:
    if dtime - btime > 1:
        timepoints.append(cnt)
        btime = dtime
    elif dtime - btime < 0:
        timepoints.append(cnt)
        btime = dtime
    else:
        btime += 1
    cnt += 1

def maindf2scans(dataframe, index_array):
    '''
       Split dataframe read from Excel file on scan boundaries and write
       out each subframe, corresponding to a separate scan, into its own
       Excel file.
       Inputs: dataframe and index_array (eg. array of begin and end timepoints)
       Output: Write out each scan subarray into it's own Excel file
       function return: None
    '''

    for index in range(len(index_array)+1):
    	#Define beginning and end of each scan and create output filename
        if index < len(index_array) - 1:
            bgnscan = index_array[index]
            endscan = index_array[index+1]
            scan_name = out_path + '/scans_xlsx/df_scan_' + str(index) + '.xlsx'
        elif index == len(index_array):
            bgnscan = index_array[index-1]
            endscan = len(dataframe)
            scan_name = out_path + '/scans_xlsx/df_scan_' + str(index - 1) + '.xlsx'
                                                                                                                    
        #Set df_scan to ramge for a given scan, relative to the master dataframe
        df_scan = dataframe[bgnscan:endscan]
        #write out given scan as an Excel file
        df_scan.to_excel(scan_name)
                                                                                                                                        
    print "Seperate scans written to disk as Excel files. "

directory = out_path + '/scans_xlsx'
if not os.path.exists(directory):
        os.makedirs(directory)

maindf2scans(dataframe, timepoints)

# This part reads in the seperate Excel scan files, converts them to fits
# and writes each scan out as an individual fits file.

def scan_xlsx2fits(dataframe,file_num):
    col_headers = list(dataframe.columns.values)
    frmts = ['J','J','J','10A','J','J','J','5A','5A','5A','5A','J','5A','J','J','J','J','J','J','J','10A','J','5A','J','J','J','J','J','J','10A','E','E','E','E','E','E','E']
                
    cols = []
    for col_num in range(len(col_headers)):
        col_name = col_headers[col_num]
        col_array = np.array(dataframe[col_name])
        cn = fits.Column(name=str(col_name), format=frmts[col_num], array=col_array)
        cols.append(cn)
                                                                
    coldefs = fits.ColDefs(cols)
    tbhdu = fits.BinTableHDU.from_columns(cols)
                                                                            
    prihdr = fits.Header()
    prihdr['OBSERVER'] = 'Area High School Astronomy Clubs'
    prihdr['COMMENT'] = "This is one scan of the calibration object"
    prihdu = fits.PrimaryHDU(header=prihdr)
    thdulist = fits.HDUList([prihdu, tbhdu])
    scan_name = out_path + '/scans_fits/df_scan_' + str(file_num) + '.fits'
    thdulist.writeto(scan_name, clobber = True)

path = out_path + '/scans_xlsx'
num_files = len([f for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))])

directory = out_path + '/scans_fits'
if not os.path.exists(directory):
        os.makedirs(directory)


for num in range(num_files):
    scan = pd.read_excel(out_path + '/scans_xlsx/df_scan_' + str(num) + '.xlsx')
    scan_xlsx2fits(scan, num)
                
print "scans in Excel xlsx format converted and written to disk as Fits files. "

