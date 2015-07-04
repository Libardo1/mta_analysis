from __future__ import division
import csv
import pycurl
import matplotlib.pyplot as plt
import datetime

class LateNight:
    #week: mon, tues, wed
    #weekend: fri, sat
    #time: 16----00----04
    #       0    v1    v2
    #Time Cutoffs:
    AM = 4
    PM = 20
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    FRIDAY = 4
    SATURDAY = 5

    def __init__(self):
        self.morning = datetime.time(self.AM, 0)
        self.evening = datetime.time(self.PM, 0)
        self.mondays = {}
        self.tuesdays = {}
        self.wednesdays = {}
        self.fridays = {}
        self.saturdays = {}

    def read_csv(self, filename):
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

    #Challenge 2 
    def combine_datetime(self, data, entry_in=2):
        '''takes dictionary, data, converts to datetime, and get count deltas'''
        #csv format: [,,06/20/2015, 00:00:00,,entries,]
        date_time = {}
        outlier = False
        time_outlier = False
        for key in data:
            temp = data[key]
            temp.sort()
            for x in range(len(temp)):
                d_t_string = " ".join(temp[x][:2])
                d_t = datetime.datetime.strptime(d_t_string,"%m/%d/%Y %H:%M:%S")
                #d_t = self.adjust_night(d_t)
                #time_outlier = self.filter_timespan(d_t)
                if x > 0:
                    count = int(temp[x][entry_in]) - int(temp[x-1][entry_in])
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
            
    def filter_timespan(self, date_time):
        if date_time.time() <= self.morning or datetime.time() > self.evening :
            time_outlier = False
        else:
            time_outlier = True
        return time_outlier
    
    def adjust_night(self, date_time):
        """adjust 0-4 times to belong to the previous day"""
        if date_time.time() <= self.morning:
            date_time -= datetime.timedelta(days=1)
        return date_time
        
    def day_only(self, data):
        '''takes dictionary, data, and turnes datetimes into dates'''
        for key in data:
            vals = data[key]
            for v in range(len(vals)):
                vals[v][0] = vals[v][0].date()
            data[key] = vals
        return data
    '''
    def combine_days(self, data):
        day_entries = {}
        for key in data:
            vals = data[key]
            vals.sort()
            date = None
            entries = 0
            for v in range(len(vals)):
                nextdate = vals[v][0]
                if date is not None:
                    current = vals[v-1]
                    entries += current[1]
                    if date != nextdate:
                        val = [current[0], entries]
                        entries = 0
                        if key not in day_entries:
                            day_entries[key] = [val]
                        else:
                            day_entries[key].append(val)
                    if v == len(vals) - 1:
                        entries += vals[v][1]
                        val = [vals[v][0], entries]
                        entries = 0
                        if key not in day_entries:
                            day_entries[key] = [val]
                        else:
                            day_entries[key].append(val)
                date = nextdate
        return day_entries
    '''

    def combine_days(self, data, date_bool=False):
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

    def combine_terminals(self, data):
        all_terminals = {}
        for key, value in data.items():
            new_key = key[1]
            if new_key in all_terminals:
                all_terminals[new_key] = all_terminals[new_key] + value
            else:
                all_terminals[new_key] = value
        all_terminals = self.combine_days(all_terminals, True)
        return all_terminals
        
    def separate_weekday(self, data):
        weekdays = {}
        weekends = {}
        for key in data:
            for night in data[key]:
                if night[0].weekday() <= self.WEDNESDAY:
                    if key in weekdays:
                        weekdays[key].append(night)
                    else:
                        weekdays[key] = [night]
                elif (night[0].weekday() == self.FRIDAY or 
                      night[0].weekday() == self.SATURDAY):
                    if key in weekends:
                        weekends[key].append(night)
                    else:
                        weekends[key] = [night]
        return weekdays, weekends
    
    def separate_day(self, data):
        for key in data:
            for night in data[key]:
                other = False
                if night[0].weekday() == self.MONDAY:
                    day = self.mondays
                elif night[0].weekday() == self.TUESDAY:
                    day = self.tuesdays
                elif night[0].weekday() == self.WEDNESDAY:
                    day = self.wednesdays
                elif night[0].weekday() == self.FRIDAY:
                    day = self.fridays
                elif night[0].weekday() == self.SATURDAY:
                    day = self.saturdays
                else:
                    other = True
                if key in day and not other:
                    day[key].append(night)
                elif not other:
                    day[key] = [night]

    def num_day(self, d_of_w, station):
        '''takes a day of week dictionary and station key, 
           and returns number of days'''
        if station in d_of_w:
            day_num = len(d_of_w[station])
        else:
            day_num = 0
        return day_num

    def sum_day(self, d_of_w, station):
        counts = 0
        if station in d_of_w:
            for val in d_of_w[station]:
                counts += val[1]
        return counts

    def weekend_num(self, station):
        fri_num = self.num_day(self.fridays, station)
        sat_num = self.num_day(self.saturdays, station)
        nums = sat_num + fri_num
        return nums

    def weekend_count(self, station):
        sat_count = self.sum_day(self.saturdays, station)  
        fri_count = self.sum_day(self.fridays, station)
        counts = sat_count + fri_count
        return counts

    def weekend_mean(self, station):
        nums = self.weekend_num(station)
        counts = self.weekend_count(station)
        if nums != 0:
            mean = counts / nums
        else:
            mean = 0
        return mean

    def weekday_num(self, station):
        mon_num = self.num_day(self.mondays, station)
        tues_num = self.num_day(self.tuesdays, station)
        wed_num = self.num_day(self.wednesdays, station)        
        nums = mon_num + tues_num + wed_num
        print nums
        return nums

    def weekday_count(self, station):
        mon_count = self.sum_day(self.mondays, station)
        tues_count = self.sum_day(self.tuesdays, station)
        wed_count = self.sum_day(self.wednesdays, station)
        counts = mon_count + tues_count + wed_count
        return counts

    def weekday_mean(self, station):
        nums = self.weekday_num(station)
        counts = self.weekday_count(station)
        if nums != 0:
            mean = counts / nums
        else:
            mean = 0
        return mean

    def weekend_means(self, data):
        mean_list = []
        for key in data:
            mean_list.append((key, self.weekend_mean(key)))
        mean_list.sort(key=lambda x: x[1], reverse=True)
        return mean_list        
        
    def weekday_means(self, data):
        mean_list = []
        for key in data:
            mean_list.append((key, self.weekday_mean(key)))
        mean_list.sort(key=lambda x: x[1], reverse=True)
        return mean_list

    def delta_weekday(self, data):
        delta_list = []
        for key in data:
            
            delta_list.append((key, self.weekend_mean(key) - self.weekday_mean(key)))
        delta_list.sort(key=lambda x: x[1], reverse=True)
        return delta_list

    # Combine several week's data
    def combine_weeks(self, files):
        d = {}
        dictlist = []
        for f in files:
            di = self.read_csv(f)
            dictlist.append(di)
        for dl in dictlist:
            for key in dl:
                if key in d:
                    d[key] += dl[key]
                else:
                    d[key] = dl[key]
        return d

    # Download data from MTA website
    def download_data(self, m, day1, maxday):
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
    
    # Generate all MTA data file names
    def filelist(self):
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

if __name__ == "__main__":
    l = LateNight()
    filenames = l.filelist()
    d = l.combine_weeks(filenames)
    d = l.combine_datetime(d)
    #d = l.day_only(d)
    d = l.combine_days(d)
    d = l.combine_terminals(d)
    #d = l.combine_terminls(d, False)
    print d
    #wdays, wends = l.separate_weekday(d)
    l.separate_day(d)
    print l.weekend_mean('34 ST-PENN STA')
    print l.weekend_mean('34 ST-HERALD SQ')
    print l.weekend_mean('PARKSIDE AVE')
    #print "wdays: ", wdays
    #print "wends: ", wends
    #print l.saturdays
    #print d["BROADWAY"]
    print l.weekend_means(d)[:10]
    print l.weekday_means(d)[:10]
    #print l.delta_weekday(d)[:10]
