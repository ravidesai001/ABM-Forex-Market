from datetime import datetime
import pandas as pd
import time
from sklearn.linear_model import LinearRegression

class DataReader:
    def __init__(self, filename) -> None:
        self.file = filename
        self.data = None
        # millisecond precision tick data "./data/december_2021_tick_data.csv"
        self.data = pd.read_csv(self.file, usecols=[0,1,2], converters={'date': self.convert_date})
    
    def convert_date(self, x):
        dt = x.split(" ")
        return datetime(year=int(dt[0][0:4]), month=int(dt[0][4:6]), day=int(dt[0][6:8]), hour=int(dt[1][0:2]), minute=int(dt[1][2:4]))

    def get_minute_data(self):
        return self.data.groupby('date').mean()

    def get_hour_data(self):
        return self.data.groupby(by=[self.data.date.map(lambda x: datetime(year=x.year, month=x.month, day=x.day, hour=x.hour))]).mean()
        
    def get_data(self):
        return self.data

class Writer:
    def __init__(self, filename) -> None:
        self.data = DataReader(filename).get_data()

    def get_spread_data(self): # spread in pips
        return [abs(row[1] - row[2]) / 0.0001 for row in self.data.itertuples(index=False)]

    def write_probability_data(self):
        spread_data = self.get_spread_data()
        max_spread = max(spread_data)
        f = open("./data/probabilities.csv", "w")
        for spread in spread_data:
            f.writelines(str(spread) + ", " + str(spread / max_spread) + "\n")
        f.close()
    

    

def main():
    start = time.process_time()
    data = pd.read_csv("./data/probabilities.csv", dtype=(float, float))
    X, y = [], []
    for row in data.itertuples(index=False):
        X.append([row[0]])
        y.append([row[1]])
    # Writer("./data/december_2021_tick_data.csv").write_probability_data()
    # print(X[:5], y[:5])
    reg = LinearRegression(fit_intercept=False).fit(X, y)
    print(reg.coef_, reg.intercept_)
    end = time.process_time()
    print("time taken: " + str(end - start))
    

if __name__ == "__main__":
    main()
