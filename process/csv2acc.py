"""
Generates a final csv with all the raw acceleration data and respective labels
Dont calculate features
For acceleration

Parameters
--ifile : input csv file with the acceleration values
--odir : output directory for the final dataset
--label : the labels file
--ws : a windows size
--sr : the sampling rate for the signal

"""

import getopt
import sys
import pandas as pd
import numpy as np
from numpy.linalg import norm
from scipy.interpolate import interp1d
import scipy.stats as stats

if __name__ == "__main__":
    inputfile = ''
    labelsfile = ''

    # Default values for sampling rate and windows size
    sr = 35
    ws = 1

    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:s:w:l", ["ifile=", "labels="])
    except getopt.GetoptError:
        print('csv2acc.py -i <inputfile> -l <labels_file>')
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print('csv2acc.py -i <inputfile> -l <labels_file>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-l", "--labels"):
            labelsfile = arg
    if inputfile == '':
        print('No input file provided')
        sys.exit(2)
    if labelsfile == '':
        print('No labels file provided')
        sys.exit(2)

    # Read the labels file
    # Labels file:
    # device_id, start_timestamp, stop_timestamp, label

    # Read the acceleration data file

    # For each segmented label
    # build a dataframe with the features defined by the
    # parameters ws, sr
    # The final dataframe is:
    # device_id, start_timestamp, stop_timestamp, frame, features, label

    # Labels file
    df_labels = pd.read_csv(labelsfile)

    # Data file
    df = pd.read_csv(inputfile)

    # Iterate through all the labels:
    raw_dfs = []
    for index, label in df_labels.iterrows():
        # Select those rows from df with device_id,
        # and timestamp between start_timestamp and stop_timestamp
        mask = (df['device_id'] == label['device_id']) & (df['timestamp'] >= label['start_timestamp']) \
               & (df['timestamp'] <= label['stop_timestamp'])
        data = df.loc[mask].sort_values(by=['timestamp'])
        # print(data)
        print(label['device_id'], label['start_timestamp'], label['stop_timestamp'])



        if data.empty:
            print("Alert: No data found between the specified timestamps")
        else:
            data['start_timestamp'] = label['start_timestamp']
            data['stop_timestamp'] = label['stop_timestamp']
            data['label'] = label['label']
            raw_dfs.append(data)
            # print(df_features.head())

    outputfile = inputfile + '.raw.csv'
    if len(raw_dfs):
        result = pd.concat(raw_dfs)
        result.to_csv(outputfile, sep=',')

