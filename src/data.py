from datetime import datetime
import pandas as pd
import time
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class DataReader:
    def __init__(self, filename) -> None:
        self.file = filename
        self.data = None
        # millisecond precision tick data "./data/december_2021_tick_data.csv"
        if "december" in self.file:
            self.data = pd.read_csv(self.file, usecols=[0,1,2], converters={'date': self.convert_date})
        else: # year case
            self.data = pd.read_csv(self.file, usecols=[0,1,2], delimiter=";", converters={'date': self.convert_date})
    
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

class Writer:
    def __init__(self, filename) -> None:
        self.data = DataReader(filename).get_six_hour_data()

    def get_spread_data(self): # spread in pips
        return [(row[1] - row[0]) / 0.0001 for row in self.data.itertuples(index=False) if (row[1] - row[0]) / 0.0001 < 20] # removes a few outliers at top end

    def write_probability_data(self):
        spread_data = self.get_spread_data()
        max_spread = max(spread_data)
        f = open("./data/probabilities.csv", "w")
        for spread in spread_data:
            f.writelines(str(spread) + ", " + str(spread / max_spread) + "\n")
        f.close()
  
# generating linear regression model for spread to probability mapping.
def generate_linear_model():
    # data = DataReader("./data/year_2021_tick_data.csv").get_six_hour_data()
    # print(data.head())
    Writer("./data/year_2020_tick_data.csv").write_probability_data()
    data = pd.read_csv("./data/probabilities.csv", dtype=(float, float))
    X, y = [], []
    for row in data.itertuples(index=False):
        X.append([row[0]])
        y.append([row[1]])
    reg = LinearRegression(fit_intercept=False).fit(X, y)
    model_file = open("./data/model_params.txt", "w") # fitting function to max probability at 0 and -ve spread
    model_file.writelines(str(reg.coef_[0][0] * -1) + ", " + str(reg.intercept_ + 1))
    model_file.close()
    # plt.scatter(X, y)
    # plt.show()

def main():
    data = DataReader("./data/year_2021_tick_data.csv").get_six_hour_data()
    print(data.head())
    # Writer("./data/year_2021_tick_data.csv").write_probability_data()

if __name__ == "__main__":
    generate_linear_model()
    # main()
