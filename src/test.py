from model import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from multiprocessing import Pool, RLock
from tqdm import tqdm
from argparse import ArgumentParser

def run_model(pid, model):
    tqdm_text = "#" + "{}".format(pid).zfill(3)
    n = model.max_steps - 1
    with tqdm(total=n, desc=tqdm_text, position=pid+1) as pbar:
        for i in range(n):
            model.step()
            pbar.update(1)
    return model

def display_trader_wealth(model_agents):
    # print(len(model_agents[0]))
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
    hist_fig.legend(loc="upper right")
    print("Trader Euros Range: " + str(round(final_trader_euro_amounts.min() / 1000000)) + " million - " + str(round(final_trader_euro_amounts.max() / 1000000)) + " million")
    print("Trader Dollars Range: " + str(round(final_trader_dollar_amounts.min() / 1000000)) + " million - " + str(round(final_trader_dollar_amounts.max() / 1000000)) + " million")


def main(num_banks, num_traders, num_runs):
    num_processes = num_runs
    pool = Pool(processes=num_processes, initargs=(RLock(),), initializer=tqdm.set_lock)
    print("Initialising models...")
    models = [FXModel(num_banks, num_traders) for i in range(num_processes)]
    jobs = [pool.apply_async(run_model, args=(i, m)) for i, m in enumerate(models)]
    pool.close()
    result_list = [job.get() for job in jobs]

    print("\n" * (len(models) + 1))

    model_agents = [model.schedule.agents for model in result_list]
    
    if num_traders > 0:
        display_trader_wealth(model_agents)
    

    data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
    fig, axs = plt.subplots(6, sharex=True)
    fig.set_size_inches(11, 9)
    fig.suptitle('Spread vs Number of Trades per Hour and Volumes Traded per Hour')
    df = pd.concat(data)#.drop(labels=['Bid', 'Offer'], axis=1)
    df = df.groupby(df.index).mean()
    # print(df.head())
    axs[0].plot(df.index.tolist(), df['Bid'].tolist())
    axs[0].plot(df.index.tolist(), df['Offer'].tolist())
    axs[0].title.set_text("Bid and Offer")
    axs[1].plot(df.index.tolist(), df['Spread'].tolist())
    axs[1].title.set_text("Spread")
    axs[2].plot(df.index.tolist(), df['Trades'].tolist())
    axs[2].title.set_text("Trades")
    axs[3].plot(df.index.tolist(), df['USD Volume'].tolist())
    axs[3].title.set_text("USD Hourly Traded Volume")
    axs[4].plot(df.index.tolist(), df['EUR Volume'].tolist())
    axs[4].title.set_text("EUR Hourly Traded Volume")
    axs[5].plot(df.index.tolist(), df['Gini'].tolist())
    axs[5].title.set_text("Gini Coefficient")
    # axs[4].plot(df.index.tolist(), df['Efficiency'].tolist())
    # axs[4].title.set_text("CDA Efficiency")
    print(df.corr(method="pearson"))
    

    plt.show()

if __name__ == "__main__":
    # TODO
    # Add toggle for spread trading signal
    parser = ArgumentParser()
    parser.add_argument("-b", "--bank", type=int, help= "The number of banks in a model")
    parser.add_argument("-t", "--trader", type=int, help= "The number of traders per bank in a model")
    parser.add_argument("-n", "--runs", type=int,
        help= "The number of times to run the model. Does a concurrent batch run using all processing threads.")
    args = parser.parse_args()
    banks, traders, runs = args.bank, args.trader, args.runs
    if banks == None:
        banks = 10
    if traders == None:
        traders = 50
    if runs == None:
        runs = 1
    if banks < 1:
        print("Must have at least one bank")
    elif traders < 0:
        print("Must have positive number of traders")
    elif runs < 1:
        print("Must have at least 1 model run")
    else:
        main(banks, traders, runs)