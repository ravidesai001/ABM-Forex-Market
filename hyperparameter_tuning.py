from model import *
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Pool, RLock, cpu_count
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

def batch_run(num_banks, num_traders, num_runs, running_data, linear_params):
    num_processes = num_runs
    pool = Pool(processes=num_processes, initargs=(RLock(),), initializer=tqdm.set_lock)
    print("Initialising models...")
    models = [FXModel(num_banks, num_traders, linear_params, running_data) for i in range(num_processes)]
    jobs = [pool.apply_async(run_model, args=(i, m)) for i, m in enumerate(models)]
    pool.close()
    result_list = [job.get() for job in jobs]
    print("\n" * (len(models) + 1))
    return result_list

def batch_run_seqeuntial_batched(num_banks, num_traders, num_runs, running_data, linear_params):
    batches = int(num_runs / cpu_count())
    runs_left = num_runs
    result_lists = []
    for i in range(1, batches + 1):
        result_list = batch_run(num_banks, num_traders, cpu_count(), running_data, linear_params)
        result_lists.append(result_list)
        runs_left -= len(result_list)
        print("Runs left: " + str(runs_left))
    
    if runs_left > 0:
        result_lists.append(batch_run(num_banks, num_traders, runs_left, running_data, linear_params))

    results = [j for sub in result_lists for j in sub]
    print("\n" * (len(results) + 1))
    return results

def hyperparameter_tune_banks(num_banks, num_traders, num_runs, training_data, running_data):
    trades, euros, dollars = [], [], []
    step = int(num_banks / 5)
    linear_params = generate_linear_model_params(training_data)
    for i in range(step, num_banks + 1, step):
        result_list = batch_run(i, num_traders, num_runs, training_data, running_data, linear_params)
        data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
        df = pd.concat(data)
        df = df.groupby(df.index).mean()
        corr_matrix = df.corr(method="pearson")
        trades.append(round(corr_matrix.iloc[3]["Spread"], 3))
        euros.append(round(corr_matrix.iloc[4]["Spread"], 3))
        dollars.append(round(corr_matrix.iloc[5]["Spread"], 3))
    
    plt.plot([i for i in range(step, num_banks + 1, step)], trades, label="Number of Trades")
    plt.plot([i for i in range(step, num_banks + 1, step)], euros, label="Euro Traded Volume")
    plt.plot([i for i in range(step, num_banks + 1, step)], dollars, label="Dollar Traded Volume")
    plt.xlabel("Number of Banks")
    plt.ylabel("Correlation with Spread")
    plt.figlegend(loc="upper right")
    plt.show()

def hyperparameter_tune_traders(num_banks, num_traders, num_runs, training_data, running_data):
    trades, euros, dollars = [], [], []
    step = int(num_traders / 5)
    linear_params = generate_linear_model_params(training_data)
    for i in range(step, num_traders + 1, step):
        result_list = batch_run(num_banks, i, num_runs, training_data, running_data, linear_params)
        data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
        df = pd.concat(data)
        df = df.groupby(df.index).mean()
        corr_matrix = df.corr(method="pearson")
        trades.append(round(corr_matrix.iloc[3]["Spread"], 3))
        euros.append(round(corr_matrix.iloc[4]["Spread"], 3))
        dollars.append(round(corr_matrix.iloc[5]["Spread"], 3))
    
    plt.plot([i for i in range(step, num_traders + 1, step)], trades, label="Number of Trades")
    plt.plot([i for i in range(step, num_traders + 1, step)], euros, label="Euro Traded Volume")
    plt.plot([i for i in range(step, num_traders + 1, step)], dollars, label="Dollar Traded Volume")
    plt.xlabel("Number of Traders")
    plt.ylabel("Correlation with Spread")
    plt.figlegend(loc="upper right")
    plt.show()

def hyperparameter_tune_runs(num_banks, num_traders, num_runs, training_data, running_data):
    linear_params = generate_linear_model_params(training_data)
    result_list = batch_run_seqeuntial_batched(num_banks, num_traders, num_runs, training_data, running_data, linear_params)
    data = [model.datacollector.get_model_vars_dataframe() for model in result_list]
    trades, euros, dollars = [], [], []
    for i in range(1, len(data) + 1):
        df = pd.concat(data[0: i])
        df = df.groupby(df.index).mean()
        corr_matrix = df.corr(method="pearson")
        trades.append(corr_matrix.iloc[3]["Spread"])
        euros.append(corr_matrix.iloc[4]["Spread"])
        dollars.append(corr_matrix.iloc[5]["Spread"])

    print("Trade Corr range: " + str(abs(min(trades)) - abs(max(trades))))
    print("Euro Vol Corr range: " + str(abs(min(euros)) - abs(max(euros))))
    print("Dollar Vol Corr range: " + str(abs(min(dollars)) - abs(max(dollars))))

    plt.plot([i for i in range(1, num_runs + 1)], trades, label="Number of Trades")
    plt.plot([i for i in range(1, num_runs + 1)], euros, label="Euro Traded Volume")
    plt.plot([i for i in range(1, num_runs + 1)], dollars, label="Dollar Traded Volume")
    plt.xlabel("Number of Model Instances Run")
    plt.ylabel("Correlation with Spread")
    plt.figlegend(loc="upper right")
    plt.show()

if __name__ == "__main__":
    training_path = "./data/year_2020_tick_data.csv"; run_path = "./data/year_2021_tick_data.csv"
    # hyperparameter_tune_banks(30, 50, 10, training_path, run_path)
    # hyperparameter_tune_traders(10, 100, 10, training_path, run_path)
    hyperparameter_tune_runs(10, 5, 10, training_path, run_path)