import csv
import datetime
import random
import matplotlib.pyplot as plt
from collections import defaultdict

class TurnStiles:
    
    def __init__(self):
        #self.stations = []
        self.starts = {}
        self.ends = {}

    #Challenge 1
    def read_csv(self, filename):
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
                    #self.stations.append(row[3]) #keep list of stations
                    key = tuple(row[:4])
                    if key not in data:
                        data[key] = [row[4:]]
                    else:
                        data[key].append(row[4:])
        
        return data

    #Challenge 2 
    def datetime_entries(self, data):
        #csv format: [,,06/20/2015, 00:00:00,,entries,]
        date_time = {}
        for key in data:
            temp = data[key]
            temp.sort()
            for x in range(len(temp)):
                #print temp[x]
                d_t_string = " ".join(temp[x][2:4])
                d_t = datetime.datetime.strptime(d_t_string, "%m/%d/%Y %H:%M:%S")
                if x > 0:
                    val = [d_t, int(temp[x][5]) - int(temp[x-1][5])]
                else:
                    val = [d_t, 0] #could cause problems later
                    self.starts[key] = temp[x]
                if x == len(temp) -1:
                    self.ends[key] = temp[x]
                if key not in date_time:
                    date_time[key] = [val]
                else:
                    date_time[key].append(val)        
        #print "starts:", self.starts, "ends:", self.ends
        data = None
        return date_time
            
    #Challenge 3, 5, 6
    def day_entries(self, data):
        day_entries = {}
        for key in data:
            vals = data[key]
            vals.sort()
            date = None
            entries = 0
            #print key
            for v in range(len(vals)):
                nextdate = vals[v][0].date()                
                #entries += vals[v][1]
                if date is not None:
                    current = vals[v-1]
                    entries += current[1]
                    if date != nextdate:
                        #print current, date
                        val = [current[0], entries]
                        entries = 0
                        if key not in day_entries:
                            day_entries[key] = [val]
                        else:
                            day_entries[key].append(val)
                    if v == len(vals) - 1:
                        entries += vals[v][1] ##added recently
                        val = [vals[v][0], entries]
                        #print entries
                        entries = 0
                        if key not in day_entries:
                            day_entries[key] = [val]
                        else:
                            day_entries[key].append(val)
                date = nextdate
        return day_entries

    #Challenge 4, 7
    def plot_random(self, data, multiple=False):
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
        #dates = ["Sat", "Sun", "Mon", "Tues", "Wed", "Thur", "Fri"]
        dates = [0, 1, 2, 3, 4, 5, 6]
        weeks = []
        start = terminal[0][0].day % 7 #day of week, usually Saturday
        temp = []
        for x in range(len(terminal)):
            if terminal[x][0].day % 7 == start:
                if temp:
                    weeks.append(temp)
                    temp = []
            temp.append(terminal[x][1])
        weeks.append(temp)
        plt.figure(figsize=(10,3))
        for w in weeks:
            plt.plot(dates,w)
        plt.title(key)
        plt.show()
                
                
            

    #Challenge 5, 6
    def combine_terminals(self, data, key_bool, clear=True):
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
        #print all_terminals
        all_terminals = self.day_entries(all_terminals)
        if clear:
            data = None
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

    def run_all(self, multiple=False):
        if multiple:
            files = ["turnstile_150606.txt", "turnstile_150613.txt", "turnstile_150620.txt", "turnstile_150627.txt"]
            d = self.combine_weeks(files)
        else:
            d = t.read_csv("testdata2.txt")
            #d = t.read_csv("turnstile_150627.txt")        
        d_t = self.datetime_entries(d)
        d_e = self.day_entries(d_t)
        self.plot_random(d_e, multiple=multiple)
        keys = [("A002","R051","02-03-03","LEXINGTON AVE"), ("A002","R051","02-03-01","LEXINGTON AVE")]
        for key in keys:
            self.plot_specific(d_e, key, multiple=multiple)
        #print "\n"
        ac = self.combine_terminals(d_e, True)
        #print ac
        #print "#6:"
        ter = self.combine_terminals(ac, False)
        self.plot_random(ter, multiple=multiple)
        stations = ["LEXINGTON AVE", "5 AVE-59 ST", "57 ST-7 AVE", "34 ST-HERALD SQ", "28 ST-BROADWAY"]
        for place in stations:
            self.plot_specific(ter, place, multiple=multiple)


if __name__ == "__main__":
    t = TurnStiles()
    t.run_all(multiple=True)

    ##TODO linter emacs
    ##TODO eliminate 0 <= count <= 5000 in challenge 2
    ## daytime_counts = {turnstile: [(time, count) for (time, count, _)
    ##                                in rows if 0 <= count <= 5000]
    ##                  for turnstile, rows in datetime_count_times.items()}
    

    ## timeline values for project: 16----- 00 ------04
    ##                              0       d1       d2
