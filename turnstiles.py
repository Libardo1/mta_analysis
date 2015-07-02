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
        if multiple:
            #print data
            key = random.choice(data[0].keys())
            terminals = []
            for d in data:
                terminals.append(d[key])
            self.plot_multiple_weeks(terminals, key)
        else:
            key = random.choice(data.keys())
            terminal = data[key]
            self.make_graph(terminal, key)

    #Challenge 4, 7
    def plot_specific(self, data, key, multiple=False):
        '''Plots a specific key from a dictionary. dict, key, multiple keys?'''
        
        if multiple:
            if key in data[0]:
                terminals = []
                for d in data:
                    terminals.append(d[key])
                self.plot_multiple_weeks(terminals, key)
            else:
                print "please input a different key"
        else:
            if key in data:
                terminal = data[key]
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
    
    def plot_multiple_weeks(self, terminals, key):
        dates = range(7)
        plt.figure(figsize=(10,3))
        for week in terminals:
            counts = []
            for item in week:
                counts.append(item[1])
            plt.plot(dates, counts)
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
        
    # Challenge 8
    def combine_weeks(self, dicts_list, entry_in=5):
        startends = self.datetime_entries(self.starts_ends)
        startends = self.day_entries(startends)
        startends = self.day_only(startends)
        startends = self.combine_terminals(startends, True)
        startends = self.combine_terminals(startends, False)
        for d in dicts_list:
            index = self.day_index(d)
            if index != -1:
                for key in d:
                    d[key][index].append(startends[key][index])
            else:
                print "\noh no!!!!\n"
        return dicts_list

    def day_index(self, d):
        key = random.choice(self.starts_ends.keys())
        if key not in d:
            return -1
        else:
            for dates in d[key]:
                for start_end_index in range(len(self.starts_ends[key])):
                    if dates[0] == self.starts_ends[key][start_end_index][0]:
                        return start_end_index
        return -1
        
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
        dicts = []
        final_dicts = []
        for f in files:
            d = self.read_csv(f)
            dicts.append(d)
        for d in dicts:
            d = self.datetime_entries(d)
            c3 = self.challenge_3(d)
            c5 = self.combine_terminals(c3, True)
            c6 = self.combine_terminals(c5, False)
            final_dicts.append(c6)
        full_dicts = self.combine_weeks(final_dicts)
        for next_dict in full_dicts:
            c8 = self.day_entries(next_dict)
            final_dicts.append(c8)
        self.challenge_7(final_dicts, multiple=True)
        #return dicts

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
        self.challenge_8()

        

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
