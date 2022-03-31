from model import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from multiprocessing import Pool, RLock
from tqdm import tqdm
from regression import generate_linear_model_params

def run_model(pid, model):
    tqdm_text = "#" + "{}".format(pid).zfill(3)
    n = model.max_steps - 1
    with tqdm(total=n, desc=tqdm_text, position=pid+1) as pbar:
        for i in range(n):
            model.step()
            pbar.update(1)
    return model


def batch_run(num_banks, num_traders, num_runs, training_data, running_data):
    num_processes = num_runs
    pool = Pool(processes=num_processes, initargs=(RLock(),), initializer=tqdm.set_lock)
    print("Initialising models...")
    linear_params = generate_linear_model_params(training_data)
    models = [FXModel(num_banks, num_traders, linear_params, running_data) for i in range(num_processes)]
    jobs = [pool.apply_async(run_model, args=(i, m)) for i, m in enumerate(models)]
    pool.close()
    result_list = [job.get() for job in jobs]

    print("\n" * (len(models) + 1))
    return result_list


def hyperparameter_tune_banks(num_banks, num_traders, num_runs, training_data, running_data):
    trades, euros, dollars = [], [], []
    for i in range(4, num_banks + 1, 4):
        result_list = batch_run(i, num_traders, num_runs, training_data, running_data)
        data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
        df = pd.concat(data)
        df = df.groupby(df.index).mean()
        corr_matrix = df.corr(method="pearson")
        trades.append(round(corr_matrix.iloc[3]["Spread"], 3))
        euros.append(round(corr_matrix.iloc[4]["Spread"], 3))
        dollars.append(round(corr_matrix.iloc[5]["Spread"], 3))
    
    plt.plot([i for i in range(4, num_banks + 1, 4)], trades, label="Number of Trades")
    plt.plot([i for i in range(4, num_banks + 1, 4)], euros, label="Euro Traded Volume")
    plt.plot([i for i in range(4, num_banks + 1, 4)], dollars, label="Dollar Traded Volume")
    plt.xlabel("Number of Banks")
    plt.ylabel("Correlation with Spread")
    
    plt.show()

def hyperparameter_tune_traders(num_banks, num_traders, num_runs, training_data, running_data):
    trades, euros, dollars = [], [], []
    for i in range(20, num_traders + 1, 20):
        result_list = batch_run(num_banks, i, num_runs, training_data, running_data)
        data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
        df = pd.concat(data)
        df = df.groupby(df.index).mean()
        corr_matrix = df.corr(method="pearson")
        trades.append(round(corr_matrix.iloc[3]["Spread"], 3))
        euros.append(round(corr_matrix.iloc[4]["Spread"], 3))
        dollars.append(round(corr_matrix.iloc[5]["Spread"], 3))
    
    plt.plot([i for i in range(20, num_traders + 1, 20)], trades, label="Number of Trades")
    plt.plot([i for i in range(20, num_traders + 1, 20)], euros, label="Euro Traded Volume")
    plt.plot([i for i in range(20, num_traders + 1, 20)], dollars, label="Dollar Traded Volume")
    plt.xlabel("Number of Traders")
    plt.ylabel("Correlation with Spread")
    
    plt.show()


if __name__ == "__main__":
    training_path = "./data/year_2020_tick_data.csv"; run_path = "./data/year_2021_tick_data.csv"
    hyperparameter_tune_banks(10, 50, 10, training_path, run_path)
    # hyperparameter_tune_traders(10, traders, runs, training_path, run_path)