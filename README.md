# A Minimal Agent-Based Model for Simulating the Foreign Exchange Market

## Requirements

- Native Unix based desktop operating system. e.g: Ubuntu 20.04
- Python 3 with pip 3
- Python 3 venv package
- Python 3 tk package

## Dependencies used

- mesa
- scikit-learn
- numpy
- pandas
- matplotlib

## Instructions
To install the dependencies and generate an environment for the code you need to run the install.sh script in a bash terminal. You will be prompted to enter the root password to install the python package dependencies.

    ./install.sh

To run the model use the run.sh script with the additional flags to define hyperparameters and datasets. The dataset arguments can either be absolute or relative paths. The following are the flags available:

- -b : Number of Banks
- -t : Number of Traders
- -n : Number of Model Instances to batch run
- -d : Trade Signal Training Data
- -r : Model Run Time Data

This command uses the relative path from the directory of the project with training data defined in the flags.

    ./run.sh -b 10 -t 50 -n 10 -d ./data/year_2020_tick_data.csv -r ./data/year_2021_tick_data.csv

To run the model without a trade signal and hence no training data the command would be as follows:

    ./run.sh -b 10 -t 50 -n 10 -d none -r ./data/year_2021_tick_data.csv

You can find the graphical and numerical outputs saved in the results subdirectory.
