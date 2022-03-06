from model import *
import matplotlib.pyplot as plt
import pandas as pd

model = FXModel(5, 50)
for i in range(model.max_steps - 1):
    model.step()

data = model.datacollector.get_model_vars_dataframe()
plt.scatter(data.index.tolist(), data['Spread'].tolist())
plt.show()