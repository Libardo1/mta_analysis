import csv
import datetime
import random
import matplotlib.pyplot as plt

class TurnStiles:
    
    def __init__(self):
        self.stations = []

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
                    self.stations.append(row[3]) #keep list of stations
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
            for x in range(len(temp)):
                d_t_string = " ".join(temp[x][2:4])
                d_t = datetime.datetime.strptime(d_t_string, "%m/%d/%Y %H:%M:%S")
                if x > 0:
                    #if temp[x-1] != temp[-1]: # not first element of list
                    val = [d_t, int(temp[x][5]) - int(temp[x-1][5])]
                else:
                    val = [d_t, 0]
                if key not in date_time:
                    date_time[key] = [val]
                else:
                    date_time[key].append(val)
            
        data = None
        return date_time
            

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
            
    def plot_random(self, data):
        key = random.choice(data.keys())
        terminal = data[key]
        self.make_graph(terminal, key)

    def plot_specific(self, data, key):
        '''Plots the values of a specific key from a dictionary. dict, key'''
        if key in data:
            terminal = data[key]
            self.make_graph(terminal, key)
        else:
            print "please input a valid key"

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
            #all_terminals[new_key].append(tuple([datetime.datetime(2015, 1, 1, 1, 1), 10000000]))
        #print all_terminals
        all_terminals = self.day_entries(all_terminals)
        if clear:
            data = None
        return all_terminals

    def run_all(self):
        #d = t.read_csv("testdata2.txt")
        d = t.read_csv("turnstile_150613.txt")
        #print "d\n\n", d
        d_t = t.datetime_entries(d)
        #print d_t
        #print d_t
        #print "\n\n\n"
        d_e = t.day_entries(d_t)
        #print d_e
        t.plot_random(d_e)
        keys = [("A002","R051","02-03-03","LEXINGTON AVE"), ("A002","R051","02-03-01","LEXINGTON AVE")]
        for key in keys:
            t.plot_specific(d_e, key)
        #print "\n"
        ac = t.combine_terminals(d_e, True)
        print ac
        #print "#6:"
        ter = t.combine_terminals(ac, False)
        t.plot_random(ter)
        stations = ["LEXINGTON AVE", "5 AVE-59 ST", "57 ST-7 AVE", "34 ST-HERALD SQ", "28 ST-BROADWAY"]
        for place in stations:
            t.plot_specific(ter, place)


if __name__ == "__main__":
    t = TurnStiles()
    t.run_all()

    ##TODO linter emacs
    
