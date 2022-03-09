from model import *
import matplotlib.pyplot as plt
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
    num_processes = 10
    pool = Pool(processes=num_processes, initargs=(RLock(),), initializer=tqdm.set_lock)
    models = [FXModel(5, 100) for i in range(num_processes)]
    jobs = [pool.apply_async(run_model, args=(i, m)) for i, m in enumerate(models)]
    pool.close()
    result_list = [job.get() for job in jobs]

    print("\n" * (len(models) + 1))

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