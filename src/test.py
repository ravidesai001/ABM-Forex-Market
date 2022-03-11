from turtle import color
from model import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from multiprocessing import Pool, RLock
from tqdm import tqdm

def run_model(pid, model):
    tqdm_text = "#" + "{}".format(pid).zfill(3)
    n = model.max_steps - 1
    with tqdm(total=n, desc=tqdm_text, position=pid+1) as pbar:
        for i in range(n):
            model.step()
            pbar.update(1)
    return model

def main():
    num_processes = 1
    pool = Pool(processes=num_processes, initargs=(RLock(),), initializer=tqdm.set_lock)
    print("Initialising models...")
    models = [FXModel(5, 100) for i in range(num_processes)]
    jobs = [pool.apply_async(run_model, args=(i, m)) for i, m in enumerate(models)]
    pool.close()
    result_list = [job.get() for job in jobs]

    print("\n" * (len(models) + 1))

    model_agents = [model.schedule.agents for model in result_list]
    # split into bank and trader agent wealths
    # final_bank_euro_amounts = np.array([[agent.EUR for agent in agent_list if agent.unique_id.startswith("bank")] for agent_list in model_agents]).flatten()
    # final_bank_dollar_amounts = np.array([[agent.USD for agent in agent_list if agent.unique_id.startswith("bank")] for agent_list in model_agents]).flatten()
    final_trader_euro_amounts = np.array([[agent.EUR for agent in agent_list if agent.unique_id.startswith("trader")] for agent_list in model_agents]).flatten()
    final_trader_dollar_amounts = np.array([[agent.USD for agent in agent_list if agent.unique_id.startswith("trader")] for agent_list in model_agents]).flatten()
    # do histogram with number of agents on y axis and bins of wealth amounts on the x axis
    hist_fig, hist_axs = plt.subplots(2, sharex=True)
    hist_fig.set_size_inches(7, 7)
    hist_axs[0].hist(final_trader_euro_amounts, bins=100, color="green", label="Euros")
    hist_axs[1].hist(final_trader_dollar_amounts, bins=100, color="orange",label="Dollars")
    hist_fig.legend(loc="lower right")


    data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
    fig, axs = plt.subplots(4, sharex=True)
    fig.set_size_inches(11, 9)
    fig.suptitle('Spread vs Number of Trades per Hour and Volumes Traded per Hour')
    df = pd.concat(data).drop(labels=['Bid', 'Offer'], axis=1)
    df = df.groupby(df.index).mean()
    # print(df.head())
    axs[0].plot(df.index.tolist(), df['Spread'].tolist())
    axs[0].title.set_text("Spread")
    axs[1].plot(df.index.tolist(), df['Trades'].tolist())
    axs[1].title.set_text("Trades")
    axs[2].plot(df.index.tolist(), df['USD Volume'].tolist())
    axs[2].title.set_text("USD Hourly Traded Volume")
    axs[3].plot(df.index.tolist(), df['EUR Volume'].tolist())
    axs[3].title.set_text("EUR Hourly Traded Volume")
    print(df.corr(method="pearson"))

    plt.show()

if __name__ == "__main__":
    main()