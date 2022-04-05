#!/bin/bash

sudo apt -y update && sudo apt -y install python3.9 python3-tk python3.9-venv git
mkdir src/data/
git clone git@github.com:ravidesai001/ABM-Forex-Market-Datasets.git && cp ABM-Forex-Market-Datasets/*.csv src/data/
rm -rf ABM-Forex-Market-Datasets
mkdir env && cd env/ && python3 -m venv . && cd ..
source env/bin/activate
pip3 install mesa scikit-learn numpy pandas matplotlib

