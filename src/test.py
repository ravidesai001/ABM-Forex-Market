from datetime import datetime
from model import *
import matplotlib.pyplot as plt
import pandas as pd
import time
from multiprocessing import Pool, cpu_count
from utils import progressBar


start = time.process_time()

def run_model(model):
    for i in progressBar(list(range(model.max_steps - 1)), prefix = 'Progress:', suffix = 'Complete', length = 50):
        model.step()
        # print(i)
    return model

cpus = cpu_count()
m = [FXModel(5, 50) for i in range(cpus)]
models = []
start = datetime.now()
with Pool(cpus) as p:
    models = p.map(run_model, m)
print("models run time: " + str(datetime.now()- start))

data = [model.datacollector.get_model_vars_dataframe() for model in models]
fig, axs = plt.subplots(4, sharex=True)
fig.suptitle('Spread vs Number of Trades per Hour and Volumes Traded per Hour')
df = pd.concat(data).drop(labels=['Bid', 'Offer'], axis=1)
df = df.groupby(df.index).mean()
# print(df.head())
axs[0].plot(df.index.tolist(), df['Spread'].tolist())
axs[0].title.set_text("Spread")
axs[1].plot(df.index.tolist(), df['Trades'].tolist())
axs[1].title.set_text("Trades")
axs[2].plot(df.index.tolist(), df['USD Volume'].tolist())
axs[2].title.set_text("USD Total Traded Volume")
axs[3].plot(df.index.tolist(), df['EUR Volume'].tolist())
axs[3].title.set_text("EUR Total Traded Volume")
print(df.corr(method="pearson"))

plt.show()


# start = time.process_time()
# models = [FXModel(5, 50) for i in range(5)]
# for i in range(models[0].max_steps - 1):
#     for model in models:
#         model.step()
#     print(i)
# end = time.process_time()
# print("models run time: " + str(end - start) + " seconds")