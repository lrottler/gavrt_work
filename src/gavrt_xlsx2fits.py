#!/home/lrottler/anaconda2/bin/python
##########!/usr/bin/python###########

import sys
import os, os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import table


arg_list = sys.argv
datafile = arg_list[1]

# This section reads original large Excel file and splits it into individual
# scans and writes the scans to disk as seperate Excel files in .xlsx fromat

dataframe = pd.read_excel(datafile)
col_headers = list(dataframe.columns.values)

def utc2secs(utc):
    utcsecs = []
    for time in utc:
        time = str(time)
        hrs = int(time[0:2])
        min = int(time[3:5])
        sec = int(time[6:8])
        utcsecs.append(hrs*3600 + min*60 + sec)
    return utcsecs

utc_1 = dataframe['utc.1']
utc_2 = dataframe['utc.2']

utc1 = utc2secs(utc_1)
utc2 = utc2secs(utc_2)
utcdiff = np.subtract(utc2, utc1)

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
    for index in range(len(index_array)+1):
        if index < len(index_array) - 1:
            bgnscan = index_array[index]
            endscan = index_array[index+1]
            scan_name = 'scans_xlsx/df_scan_' + str(index) + '.xlsx'
        elif index == len(index_array):
            bgnscan = index_array[index-1]
            endscan = len(dataframe)
            scan_name = 'scans_xlsx/df_scan_' + str(index - 1) + '.xlsx'
                                                                                                                    
        df_scan = dataframe[bgnscan:endscan]
        df_scan.to_excel(scan_name)
                                                                                                                                        
    print "Seperate scans written to disk as Excel files. "

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
    scan_name = 'scans_fits/df_scan_' + str(file_num) + '.fits'
    thdulist.writeto(scan_name, clobber = True)

path = './scans_xlsx'
num_files = len([f for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))])

for num in range(num_files):
    scan = pd.read_excel('scans_xlsx/df_scan_' + str(num) + '.xlsx')
    scan_xlsx2fits(scan, num)
                
print "scans in Excel xlsx format converted and written to disk as a Fits files. "

