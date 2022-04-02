from model import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from multiprocessing import Pool, RLock
from tqdm import tqdm
from argparse import ArgumentParser
from regression import generate_linear_model_params
import os
from datetime import datetime

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
    final_trader_euro_amounts = np.array([[agent.EUR for agent in agent_list if agent.unique_id.startswith("trader")] for agent_list in model_agents]).flatten()
    final_trader_dollar_amounts = np.array([[agent.USD for agent in agent_list if agent.unique_id.startswith("trader")] for agent_list in model_agents]).flatten()
    # do histogram with number of agents on y axis and bins of wealth amounts on the x axis
    hist_fig, hist_axs = plt.subplots(2, sharex=True)
    hist_fig.set_size_inches(7, 7)
    hist_fig.text(0.5, 0.04, 'Currency Reserves', ha='center')
    hist_fig.text(0.04, 0.5, 'Number of Agents', va='center', rotation='vertical')
    hist_fig.suptitle("Trading Agent Currency Reserves")
    hist_axs[0].hist(final_trader_euro_amounts, bins=100, color="green", label="Euros")
    hist_axs[1].hist(final_trader_dollar_amounts, bins=100, color="orange",label="Dollars")
    hist_fig.legend(loc="upper right")
    hist_fig.savefig("./results/histogram" + str(banks) + "_" + str(traders) + "_" + str(runs) + "_" + training_path.split("/")[-1] + "_" + run_path.split("/")[-1] + ".png")
    trader_euro_range_string = "Trader Euros Range: " + str(round(final_trader_euro_amounts.min() / 1000000)) + " million - " + str(round(final_trader_euro_amounts.max() / 1000000)) + " million"
    trader_dollar_range_string = "Trader Dollars Range: " + str(round(final_trader_dollar_amounts.min() / 1000000)) + " million - " + str(round(final_trader_dollar_amounts.max() / 1000000)) + " million"
    print(trader_euro_range_string)
    print(trader_dollar_range_string)
    stats_file.write(trader_euro_range_string + '\n' + trader_dollar_range_string + '\n')


def main(num_banks, num_traders, num_runs, training_data, running_data):
    num_processes = num_runs
    pool = Pool(processes=num_processes, initargs=(RLock(),), initializer=tqdm.set_lock)
    print("Initialising models...")
    linear_params = generate_linear_model_params(training_data)
    models = [FXModel(num_banks, num_traders, linear_params, running_data) for i in range(num_processes)]
    jobs = [pool.apply_async(run_model, args=(i, m)) for i, m in enumerate(models)]
    pool.close()
    result_list = [job.get() for job in jobs]

    print("\n" * (len(models) + 1))

    model_agents = [model.schedule.agents for model in result_list]
    
    if num_traders > 0:
        display_trader_wealth(model_agents)

    final_bank_euro_amounts = np.array([[agent.EUR for agent in agent_list if agent.unique_id.startswith("bank")] for agent_list in model_agents]).flatten()
    final_bank_dollar_amounts = np.array([[agent.USD for agent in agent_list if agent.unique_id.startswith("bank")] for agent_list in model_agents]).flatten()
    bank_euro_range_string = "Bank Euros Range: " + str(round(final_bank_euro_amounts.min() / 1000000000, 4)) + " billion - " + str(round(final_bank_euro_amounts.max() / 1000000000, 4)) + " billion"
    bank_dollar_range_string = "Bank Dollars Range: " + str(round(final_bank_dollar_amounts.min() / 1000000000, 4)) + " billion - " + str(round(final_bank_dollar_amounts.max() / 1000000000, 4)) + " billion"    
    stats_file.write(bank_euro_range_string + '\n' + bank_dollar_range_string + '\n')
    print(bank_euro_range_string)
    print(bank_dollar_range_string)

    data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
    fig, axs = plt.subplots(5, sharex=True)
    fig.set_size_inches(11, 9)
    fig.suptitle('Spread vs Trade Activity')
    fig.text(0.5, 0.04, 'Model Step', ha='center')
    df = pd.concat(data)#.drop(labels=['Bid', 'Offer'], axis=1)
    df = df.groupby(df.index).mean()
    # print(df.head())
    axs[0].plot(df.index.tolist(), df['Bid'].tolist())
    axs[0].plot(df.index.tolist(), df['Offer'].tolist())
    axs[0].title.set_text("Bid and Offer")
    axs[0].set_ylabel("Exchange Rate")
    axs[1].plot(df.index.tolist(), df['Spread'].tolist())
    axs[1].title.set_text("Spread")
    axs[1].set_ylabel("Spread in Pips")
    axs[2].plot(df.index.tolist(), df['Trades'].tolist())
    axs[2].title.set_text("Trades")
    axs[2].set_ylabel("Number of Trades")
    axs[3].plot(df.index.tolist(), df['USD Volume'].tolist())
    axs[3].title.set_text("USD Hourly Traded Volume")
    axs[3].set_ylabel("Dollars")
    axs[4].plot(df.index.tolist(), df['EUR Volume'].tolist())
    axs[4].title.set_text("EUR Hourly Traded Volume")
    axs[4].set_ylabel("Euros")
    fig.savefig("./results/graphs" + str(banks) + "_" + str(traders) + "_" + str(runs) + "_" + training_path.split("/")[-1] + "_" + run_path.split("/")[-1] + ".png")
    # axs[5].plot(df.index.tolist(), df['Gini'].tolist())
    # axs[5].title.set_text("Gini Coefficient")
    corr_matrix = df.corr(method="pearson")
    spread_trades_corr = "Correlation Between Spread and Number of Trades: " + str(round(corr_matrix.iloc[3]["Spread"], 3))
    spread_euros_corr = "Correlation Between Spread and Euro Traded Volume: " + str(round(corr_matrix.iloc[4]["Spread"], 3))
    spread_dollars_corr = "Correlation Between Spread and Dollar Traded Volume: " + str(round(corr_matrix.iloc[5]["Spread"], 3))
    stats_file.write(spread_trades_corr + '\n' + spread_euros_corr + '\n' + spread_dollars_corr + '\n')
    print(spread_trades_corr)
    print(spread_euros_corr)
    print(spread_dollars_corr)
    plt.show()

if __name__ == "__main__":
    # TODO
    # Add toggle for spread trading signal
    # Add argument parsing for a training file and a run time file - DONE
    # Add result saving automatically in a subfolder
    parser = ArgumentParser()
    parser.add_argument("-b", "--bank", type=int, help= "The number of banks in a model")
    parser.add_argument("-t", "--trader", type=int, help= "The number of traders per bank in a model")
    parser.add_argument("-n", "--runs", type=int,
        help= "The number of times to run the model. Does a concurrent batch run using all processing threads.")
    parser.add_argument("-td", "--training", help= "The absolute path to the training data.")
    parser.add_argument("-rd", "--running", help= "The absolute path to the run time data.")
    args = parser.parse_args()
    if not os.path.exists("./results"):
        os.makedirs("./results")
    banks, traders, runs = args.bank, args.trader, args.runs
    training_path, run_path = args.training, args.running
    stats_file = open("./results/stats" + str(banks) + "_" + str(traders) + "_" + str(runs) + "_" + training_path.split("/")[-1] + "_" + run_path.split("/")[-1] + ".txt" , "w")
    if banks == None:
        banks = 10
    if traders == None:
        traders = 50
    if runs == None:
        runs = 1
    # if training_path == None:
    #     training_path = "./data/year_2020_tick_data.csv"
    if run_path == None:
        run_path = "./data/year_2021_tick_data.csv"
    if banks < 1:
        print("Must have at least one bank")
    elif traders < 0:
        print("Must have positive number of traders")
    elif runs < 1:
        print("Must have at least 1 model run")
    else:
        main(banks, traders, runs, training_path, run_path)
    stats_file.close()