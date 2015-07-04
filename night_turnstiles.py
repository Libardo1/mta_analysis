# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from __future__ import division
import csv
import pycurl
import matplotlib.pyplot as plt
import datetime
from fractions import Fraction
from operator import itemgetter

%matplotlib inline

# <codecell>


#week: mon, tues, wed
#weekend: fri, sat
#time: 16----00----04
#       0    v1    v2

#Set initial variables
AM = 4
PM = 20
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
FRIDAY = 4
SATURDAY = 5

morning = datetime.time(AM, 0)
evening = datetime.time(PM, 0)

# <codecell>

'''
# Download data from MTA website
def download_data(m, day1, maxday):
    url = "http://web.mta.info/developers/"
    path = "data/nyct/turnstile/"
    month = m
    day = day1
    response = urllib2.urlopen(url).read()
    while day <= maxday:
        filename = month+ "%02d.txt" %day
        with open(filename, "wb") as f:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url+path+filename)
            curl.setopt(pycurl.WRITEDATA, f)
            curl.perform()
            curl.close()
        day += 7
'''

# <codecell>

# Generate all MTA data file names
def filelist():
    month_list = ["turnstile_1504", "turnstile_1505", "turnstile_1506"]
    start_list = [4, 2, 6]
    end_list = [30, 31, 30]
    file_list = []
    for m in range(len(month_list)):
        day = start_list[m]
        while day <= end_list[m]:
            filename = month_list[m] + "%02d.txt" %day
            file_list.append(filename)
            day += 7
    return file_list

# <codecell>

filelist()

# <codecell>

def read_csv(filename):
    '''takes name of csv file, including extension'''
    #C/A,UNIT,SCP,STATION,LINENAME,DIVISION,DATE,TIME,DESC,ENTRIES,EXITS
    data = {}
    with open(filename) as f:
        reader = csv.reader(f, skipinitialspace=True, delimiter=",")
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0) #return to top
        incsv = csv.reader(f)
        if has_header:
            next(incsv)
            for row in reader:
                row = [' '.join(x.split()) for x in row] 
                key = tuple(row[2:4]) #SCP and Station
                val = [row[6], row[7], row[10]] #date, time, exits
                if key not in data:
                    data[key] = [val]
                else:
                    data[key].append(val)
    return data

# <codecell>

# Combine several week's data
def combine_weeks(files):
    d = {}
    dictlist = []
    for f in files:
        di = read_csv(f)
        dictlist.append(di)
    for dl in dictlist:
        for key in dl:
            if key in d:
                d[key] += dl[key]
            else:
                d[key] = dl[key]
    return d

full_dict = combine_weeks(filelist())

# <codecell>

full_dict.items()[0]

# <codecell>

morning

# <codecell>

evening

# <codecell>

def filter_timespan(date_time):
    if date_time.time() <= morning or datetime.time() > evening :
        time_outlier = False
    else:
        time_outlier = True
    return time_outlier

# <codecell>

def adjust_night(date_time):
    """adjust 0-4 times to belong to the previous day"""
    if date_time.time() <= morning:
        date_time -= datetime.timedelta(days=1)
    return date_time

# <codecell>

#Challenge 2 
def combine_datetime(data, count_in=2):
    '''takes dictionary, data, converts to datetime, and get count deltas'''
    #csv format: [,,06/20/2015, 00:00:00,,entries,]
    date_time = {}
    outlier = False
    for key in data:
        temp = data[key]
        temp.sort()
        for x in range(len(temp)):
            d_t_string = " ".join(temp[x][:2])
            d_t = datetime.datetime.strptime(d_t_string,"%m/%d/%Y %H:%M:%S")
            d_t = adjust_night(d_t)
            time_outlier = filter_timespan(d_t)
            if x > 0:
                count = int(temp[x][count_in]) - int(temp[x-1][count_in])
                val = [d_t, count]
                if count < 0 or count > 5000:
                    outlier = True
            else:
                 val = [d_t, 0]
            # clean data
            if not outlier and not time_outlier:
                if key not in date_time:
                    date_time[key] = [val]
                else:
                    date_time[key].append(val)
            outlier = False
    return date_time

cleaned_dict = combine_datetime(full_dict)

# <codecell>

cleaned_dict['02-00-00','LEXINGTON AVE']

# <codecell>

def combine_days(data, date_bool=False):
    day_counts = {}
    for turnstile, rows in data.items():
        by_day = {}
        for time, count in rows:
            if date_bool:
                day = time
            else:
                day = time.date()
            by_day[day] = by_day.get(day, 0) + count
        day_counts[turnstile] = sorted(by_day.items())
    return day_counts

night_counts = combine_days(cleaned_dict)

# <codecell>

night_counts['02-00-00','LEXINGTON AVE']

# <codecell>

def combine_terminals(data):
    all_terminals = {}
    for key, value in data.items():
        new_key = key[1]
        if new_key in all_terminals:
            all_terminals[new_key] = all_terminals[new_key] + value
        else:
            all_terminals[new_key] = value
    all_terminals = combine_days(all_terminals, True)
    return all_terminals

stations_only = combine_terminals(night_counts)

# <codecell>

stations_only['LEXINGTON AVE']

# <codecell>

def separate_weekday(data):
        weekday_weekend = {}
        for key in data:
            weekday_num = 0
            weekend_num = 0
            weekday_count = 0
            weekend_count = 0
            for night in data[key]:
                if night[0].weekday() <= WEDNESDAY:
                    weekday_num += 1
                    weekday_count += night[1]
                elif (night[0].weekday() == FRIDAY or 
                      night[0].weekday() == SATURDAY):
                    weekend_num += 1
                    weekend_count += night[1]
            val = [(weekday_num, weekday_count), (weekend_num, weekend_count)]
            weekday_weekend[key] = val
        return weekday_weekend

separate_weekday_weekend = separate_weekday(stations_only)

# <codecell>

separate_weekday_weekend['LEXINGTON AVE']

# <codecell>

separate_weekday_weekend

# <codecell>

def weekend_mean(data, station):
    nums = data[station][1][0]
    counts = data[station][1][1]
    if nums != 0:
        mean = counts / nums
    else:
        mean = 0
    return mean

# <codecell>

weekend_mean(separate_weekday_weekend, 'LEXINGTON AVE')

# <codecell>

def weekday_mean(data, station):
    nums = data[station][0][0]
    counts = data[station][0][1]
    if nums != 0:
        mean = counts / nums
    else:
        mean = 0
    return mean

# <codecell>

weekday_mean(separate_weekday_weekend, 'LEXINGTON AVE')

# <codecell>

def weekend_means(data):
    mean_list = []
    for key in data:
        mean_list.append((key, weekend_mean(data, key)))
    mean_list.sort(key=lambda x: x[1], reverse=True)
    return mean_list 

# <codecell>

weekend_means(separate_weekday_weekend)[:10]

# <codecell>

def weekday_means(data):
    mean_list = []
    for key in data:
        mean_list.append((key, weekday_mean(data, key)))
    mean_list.sort(key=lambda x: x[1], reverse=True)
    return mean_list

# <codecell>

weekday_means(separate_weekday_weekend)[:10]

# <codecell>

def weekend_minus_weekday(data):
    delta_list = []
    for station in data:
        wday_nums = data[station][0][0]
        wday_counts = data[station][0][1]
        
        wend_nums = data[station][1][0]
        wend_counts = data[station][1][1]
        if wday_nums != 0 and wend_nums != 0:
            delta_list.append((station, float(Fraction(wend_counts, wend_nums) - Fraction(wday_counts, wday_nums))))
    
    minus_list = sorted(delta_list, key=lambda x: x[1], reverse=True)
    return minus_list

# <codecell>

weekend_minus_weekday(separate_weekday_weekend)[:10]

# <codecell>

def weekend_over_weekday(data):
    delta_list = []
    for station in data:
        wday_nums = data[station][0][0]
        wday_counts = data[station][0][1] 
        wend_nums = data[station][1][0]
        wend_counts = data[station][1][1]
        if wday_nums!= 0:
            wday_mean = Fraction(wday_counts, wday_nums)
            if wday_mean!= 0 and wend_nums != 0:
                delta_list.append((station, float(Fraction(wend_counts, wend_nums) / wday_mean)))
    delta_list.sort(key=lambda x: x[1], reverse=True)
    return delta_list

# <codecell>

weekend_over_weekday(separate_weekday_weekend)[:10]

# <codecell>


