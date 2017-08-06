"""
Generates a final csv with all the data and respective labels
For gps

Parameters
--ifile : input csv file with the acceleration values
--label : the labels file

"""
import getopt
import sys
import pandas as pd

if __name__ == "__main__":
    inputfile = ''
    labelsfile = ''
    outputfile = inputfile + '.gps'
    # Default values for sampling rate and windows size
    sr = 35
    ws = 1

    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:l", ["ifile=", "labels="])
    except getopt.GetoptError:
        print('csv2gps_dataset.py -i <inputfile> -l <labels_file>')
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print('csv2gps_dataset.py -i <inputfile> -l <labels_file>')
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

    # Labels file
    df_labels = pd.read_csv(labelsfile)

    # Data file
    df = pd.read_csv(inputfile)

    gps_data = []
    for index, label in df_labels.iterrows():
        # Select those rows from df with device_id,
        # and timestamp between start_timestamp and stop_timestamp
        mask = (df['device_id'] == label['device_id']) & (df['timestamp'] >= label['start_timestamp']) \
               & (df['timestamp'] <= label['stop_timestamp'])
        data = df.loc[mask].sort_values(by=['timestamp'])
        data['label'] = label['label']
        data['start_timestamp'] = label['start_timestamp']
        data['stop_timestamp'] = label['stop_timestamp']
        print(data.head())
        gps_data.append(data)

    result = pd.concat(gps_data)
    result.to_csv(inputfile + '.gps', sep=',')
