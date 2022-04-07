from datetime import datetime
import pandas as pd

class DataReader:
    def __init__(self, filename) -> None:
        self.file = filename
        self.data = None
        # millisecond precision tick data on monthly data sets from HistData
        if "year" in self.file:
            self.data = pd.read_csv(self.file, usecols=[0,1,2], names=["date", "bid", "offer"], delimiter=";", converters={'date': self.convert_date})
        else: # month case
            self.data = pd.read_csv(self.file, usecols=[0,1,2], names=["date", "bid", "offer"], converters={'date': self.convert_date})
    
    def convert_date(self, x):
        dt = x.split(" ")
        return datetime(year=int(dt[0][0:4]), month=int(dt[0][4:6]), day=int(dt[0][6:8]), hour=int(dt[1][0:2]), minute=int(dt[1][2:4]))

    def get_minute_data(self):
        return self.data.groupby('date').mean()

    def get_hour_data(self):
        return self.data.groupby(by=[self.data.date.map(lambda x: datetime(year=x.year, month=x.month, day=x.day, hour=x.hour))]).mean()
    
    def get_six_hour_data(self):
        return self.data.groupby(by=[self.data.date.map(lambda x: datetime(year=x.year, month=x.month, day=x.day, hour=x.hour) if x.hour % 6 == 0 else None)]).mean()
        
    def get_data(self):
        return self.data
    
    def get_spread_data(self): # spread in pips
        return [(row[1] - row[0]) / 0.0001 for row in self.get_six_hour_data().itertuples(index=False) if (row[1] - row[0]) / 0.0001 < 20] # removes a few outliers at top end
    
    def get_probability_data(self):
        spread_data = self.get_spread_data()
        max_spread = max(spread_data)
        return [(spread, spread / max_spread) for spread in spread_data]
  

