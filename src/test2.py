from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument( "-b", "--bank", type=int, help= "The number of banks in a model")
parser.add_argument("-t", "--trader", type=int, help= "The number of traders per bank in a model")
parser.add_argument("-n", "--runs", type=int,  
    help= "The number of times to run the model. Does a concurrent batch run using all processing threads.")

args = parser.parse_args()

print(args.bank, args.trader, args.runs)
