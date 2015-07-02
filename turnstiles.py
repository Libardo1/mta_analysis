import csv
import datetime
import random
import urllib2
import pycurl
import matplotlib.pyplot as plt
from collections import defaultdict

class TurnStiles:
    
    def __init__(self):
        #self.stations = []
        self.starts = {}
        self.ends = {}
        self.starts_ends = {}

    #Challenge 1
    def read_csv(self, filename):
        '''takes name of csv file, including extension'''
        #C/A,UNIT,SCP,STATION,LINENAME,DIVISION,DATE,TIME,DESC,ENTRIES,EXITS
        data = {}
        with open(filename, 'rb') as csvfile:
            filereader = csv.reader(csvfile, skipinitialspace=True, delimiter=",")
            has_header = csv.Sniffer().has_header(csvfile.read(1024))
            csvfile.seek(0)  # rewind
            incsv = csv.reader(csvfile)
            if has_header:
                next(incsv)
                for row in filereader:
                    row = [' '.join(x.split()) for x in row]
                    key = tuple(row[:4])
                    if key not in data:
                        data[key] = [row[4:]]
                    else:
                        data[key].append(row[4:])
        return data

    #Challenge 2 
    def datetime_entries(self, data, entry_in=5):
        '''takes dictionary, data, converts to datetime, and get count deltas'''
        #csv format: [,,06/20/2015, 00:00:00,,entries,]
        date_time = {}
        outlier = False
        for key in data:
            temp = data[key]
            temp.sort()
            for x in range(len(temp)):
                d_t_string = " ".join(temp[x][2:4])
                d_t = datetime.datetime.strptime(d_t_string,"%m/%d/%Y %H:%M:%S")
                if x > 0:
                    count = int(temp[x][entry_in]) - int(temp[x-1][entry_in])
                    val = [d_t, count ]
                    if count < 0 or count > 5000:
                        outlier = True
                else:
                    val = [d_t, 0] #could cause problems later
    
                if not outlier:
                    if x == (len(temp) -1) or x == 0:
                        if key not in self.starts_ends:
                            self.starts_ends[key] = [temp[x]]
                        else:
                            self.starts_ends[key].append(temp[x])
                    if key not in date_time:
                        date_time[key] = [val]
                    else:
                        date_time[key].append(val)
                outlier = False
        return date_time
            
    #Challenge 3, 5, 6
    def day_entries(self, data):
        '''takes dictionary, data, and combines counts in same date'''
        day_entries = {}
        for key in data:
            vals = data[key]
            vals.sort()
            date = None
            entries = 0
            #print key
            for v in range(len(vals)):
                isdatetime = vals[v][0]
                if hasattr(isdatetime, 'hour'):
                    nextdate = vals[v][0].date()
                else:
                    nextdate = isdatetime
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

    #Challenge 3.5
    def day_only(self, data):
        '''takes dictionary, data, and turnes datetimes into dates'''
        for key in data:
            vals = data[key]
            for v in range(len(vals)):
                vals[v][0] = vals[v][0].date()
            data[key] = vals
        return data

    #Challenge 4, 7
    def plot_random(self, data, multiple=False):
        #print data
        key = random.choice(data.keys())
        terminal = data[key]
        if multiple:
            self.plot_multiple_weeks(terminal, key)
        else:
            self.make_graph(terminal, key)

    #Challenge 4, 7
    def plot_specific(self, data, key, multiple=False):
        '''Plots a specific key from a dictionary. dict, key, multiple keys?'''
        if key in data:
                terminal = data[key]
                if multiple:
                    self.plot_multiple_weeks(terminal, key)
                else:
                    self.make_graph(terminal, key)
        else:
            print "please input a valid key"

    #Challenge 4, 7
    def make_graph(self, terminal, key):
        '''Takes a list and a title'''
        dates = []
        counts = []
        for item in terminal:
            dates.append(item[0])
            counts.append(item[1])
        plt.figure(figsize=(10,3))
        plt.plot(dates,counts)
        plt.title(key)
        plt.show()
    
    #Challenge 8
    def plot_multiple_weeks(self, terminal, key):
        dates = range(7)
        weeks = []
        week = []
        for day in terminal:
            if day[0].weekday() == 5: #is saturday
                if week:
                    weeks.append(week)
                    week = []
            week.append(day[1])
        weeks.append(week)
        plt.figure(figsize=(10,3))
        for item in weeks:
            plt.plot(dates, item)
        plt.title(key)
        plt.show()

    #Challenge 5, 6
    def combine_terminals(self, data, key_bool):
        all_terminals = {}
        for key, value in data.items():
            if key_bool == True:
                key_args = [key[0], key[1], key[3]]
                new_key = tuple(key_args)
            else:
                new_key = key[2]
            
            if new_key in all_terminals:
                all_terminals[new_key] = all_terminals[new_key] + value
            else:
                all_terminals[new_key] = value
        all_terminals = self.day_entries(all_terminals)
        return all_terminals

    # Challenge 8?
    def combine_weeks(self, files):
        d = {}
        dictlist = []
        for f in files:
            di = t.read_csv(f)
            dictlist.append(di)
        for dl in dictlist:
            for key in dl:
                #print key
                if key in d:
                    d[key] += dl[key]
                else:
                    d[key] = dl[key]
        return d
        
    #Challenge 9
    def week_ridership(self, data):
        stations = {}
        for key in data:
            total = 0
            for day in data[key]:
                if day[0].weekday() == 5: #is saturday
                    if total > 0:
                        if key in stations:
                            stations[key].append(total)
                        else:
                            stations[key] = [total]
                        total = 0
                total += day[1]
            stations[key].append(total)
        return self.total_ridership(stations)
        
    def total_ridership(self, data):
        riders = []
        for key in data:
            riders.append((key, sum(data[key])))
        riders.sort(key=lambda x: x[1])
        #print riders
        return riders

    #Challenge 10
    def plot_total_ridership(self, data_list):
        xs = []
        ys = []
        for dl in data_list:
            #xs.append(dl[0])
            ys.append(dl[1])
        #plt.hist(xs, ys)
        plt.hist(ys)
        plt.title("hist of total ridership for june")
        plt.yscale('log')
        plt.show()
        indices = range(len(ys))
        plt.bar(indices, ys)
        plt.yscale('log')
        plt.title("bar graph of total ridership for june")
        plt.show()
        
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
        
    def challenge_1(self, filename = "turnstile_150627.txt"):
        data = t.read_csv(filename)
        return data

    def challenge_3(self, data):
        d_e = self.day_entries(data)
        d_o = self.day_only(d_e)
        return d_o

    def challenge_4(self, data, multiple):
        self.plot_random(data, multiple=multiple)
        keys = [("A002","R051","02-03-03","LEXINGTON AVE"), ("A002","R051","02-03-01","LEXINGTON AVE")]
        for key in keys:
            self.plot_specific(data, key, multiple=multiple)

    def challenge_7(self, data, multiple):
        self.plot_random(data, multiple=multiple)
        stations = ["LEXINGTON AVE", "5 AVE-59 ST", "57 ST-7 AVE", "34 ST-HERALD SQ", "28 ST-BROADWAY"]
        for place in stations:
            self.plot_specific(data, place, multiple=multiple)

    def challenge_8(self):
        files = ["turnstile_150606.txt", "turnstile_150613.txt", "turnstile_150620.txt", "turnstile_150627.txt"]
        files.sort()
        d = self.combine_weeks(files)
        d = self.datetime_entries(d)
        c3 = self.challenge_3(d)
        c5 = self.combine_terminals(c3, True)
        c6 = self.combine_terminals(c5, False)
        self.challenge_7(c6, multiple=True)
        return c6

    def run_all(self, multiple=False):
        #self.download_data("turnstile_1504", 4, 30)
        #self.download_data("turnstile_1505", 2, 31)
        #d = self.challenge_1(multiple=multiple)
        #d_t = self.datetime_entries(d)
        #c3 = self.challenge_3(d_t)
        #self.challenge_4(c3, multiple=multiple)
        #c5 = self.combine_terminals(c3, True)
        #c6 = self.combine_terminals(c5, False)
        #self.challenge_7(c6, multiple=multiple)
        d = self.challenge_8()
        d = self.week_ridership(d)
        self.plot_total_ridership(d)

        

if __name__ == "__main__":
    t = TurnStiles()
    t.run_all(multiple=False)

    ##TODO linter emacs
    ##TODO eliminate 0 <= count <= 5000 in challenge 2
    ## daytime_counts = {turnstile: [(time, count) for (time, count, _)
    ##                                in rows if 0 <= count <= 5000]
    ##                  for turnstile, rows in datetime_count_times.items()}
    

    ## timeline values for project: 16----- 00 ------04
    ##                              0       d1       d2
