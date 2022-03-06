from model import *
import matplotlib.pyplot as plt
import pandas as pd
import time

# # single model run
# start = time.process_time()
# model = FXModel(5, 20)
# print(model.max_steps)
# for i in range(1000):
#     model.step()
# end = time.process_time()
# print("model run time: " + str(end - start) + " seconds")

# data = model.datacollector.get_model_vars_dataframe()
# fig, axs = plt.subplots(2)
# fig.suptitle('Spread and number of trades')
# df = data[['Spread', 'Trades']].copy()
# axs[0].plot(data.index.tolist(), data['Spread'].tolist())
# axs[1].plot(data.index.tolist(), data['Trades'].tolist())
# print(df.corr(method="pearson"))

# plt.show()

start = time.process_time()
models = [FXModel(5, 20) for i in range(1)]
for i in range(models[0].max_steps - 1):
    for model in models:
        model.step()
    print(i)
end = time.process_time()
print("models run time: " + str(end - start) + " seconds")

data = [model.datacollector.get_model_vars_dataframe() for model in models]
fig, axs = plt.subplots(2)
fig.suptitle('Spread and Average number of trades')
df = pd.concat(data).drop(labels=['Bid', 'Offer'], axis=1)
df = df.groupby(df.index).mean()

axs[0].plot(df.index.tolist(), df['Spread'].tolist())
axs[1].plot(df.index.tolist(), df['Trades'].tolist())
print(df.corr(method="pearson"))

plt.show()