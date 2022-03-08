import random
import time

def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()



start = time.process_time_ns()
items = list(range(0, 57))
x = 0
# A Nicer, Single-Call Usage
for item in progressBar(items, prefix = 'Progress:', suffix = 'Complete', length = 50):
    # Do stuff...
    x = 0.7 * 50000000
    time.sleep(0.1)

# x = 0
# for i in range(10000000):
#     # x = random.choice([1,2])
#     # x = random.normalvariate(500, 50)
#     x = 0.7 * 50000000
end = time.process_time_ns()

print(str((end - start)/1000000000))