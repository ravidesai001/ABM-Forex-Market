#!/bin/bash

while getopts b:t:n:d:r: flag
do
    case "${flag}" in
        b) banks=${OPTARG};;
        t) traders=${OPTARG};;
        n) runs=${OPTARG};;
        d) training_data=${OPTARG};;
        r) running_data=${OPTARG};;
    esac
done

source env/bin/activate
python3 test.py -b $banks -t $traders -n $runs -d $training_data -r $running_data
