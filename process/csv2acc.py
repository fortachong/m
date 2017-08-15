"""
Generates a final csv with all the raw acceleration data and respective labels
Dont calculate features for acceleration. It is just a raw labeled file with the
acceleration points in it

Parameters
--ifile : input csv file with the acceleration values
--l : the labels file

"""

import getopt
import sys
import pandas as pd


def usage():
    print('python csv2acc.py --ifile <input_file> --l <labels_file>')
    print()
    print('Example:')
    print('python csv2acc.py --ifile data/ACC_capture.csv --l datasets/labels.csv')


if __name__ == "__main__":
    inputfile = ''
    labelsfile = ''

    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:l", ["ifile=", "l="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-l", "--l"):
            labelsfile = arg
    if inputfile == '':
        print('No input file provided')
        usage()
        sys.exit(2)
    if labelsfile == '':
        print('No labels file provided')
        usage()
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
            print("Alert: No data found between the specified timestamps in labels file")
        else:
            data['start_timestamp'] = label['start_timestamp']
            data['stop_timestamp'] = label['stop_timestamp']
            data['label'] = label['label']
            raw_dfs.append(data)
            # print(df_features.head())

    outputfile = inputfile + '.raw.csv'
    if len(raw_dfs):
        result = pd.concat(raw_dfs)
        result.to_csv(outputfile, sep=',', index=False)

