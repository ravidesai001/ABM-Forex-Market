from datetime import datetime
import pandas as pd

class DataReader:
    def __init__(self, filename):
        self.file = filename
        self.data = None
        # millisecond precision tick data "./data/december_2021_tick_data.csv"
        f = lambda x : datetime(year=int(x.split(" ")[0][0:4]), month=int(x.split(" ")[0][4:6]), day=int(x.split(" ")[0][6:8]), hour=int(x.split(" ")[1][0:2]), minute=int(x.split(" ")[1][2:4]))
        self.data = pd.read_csv(self.file, usecols=[0,1,2], converters={'date': f})

    def get_minute_data(self):
        return self.data.groupby('date').mean()
        
    def get_data(self):
        return self.data
    



