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


def usage():
    print('python csv2gps_dataset.py --ifile <input_file> --l <labels_file>')
    print()
    print('Example:')
    print('python csv2gps_dataset.py --ifile data/ACC_capture.csv --l datasets/labels.csv')


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

    outputfile = inputfile + '.gps.csv'
    # Labels file
    df_labels = pd.read_csv(labelsfile)

    # Data file
    df = pd.read_csv(inputfile)

    print("Using input file: {}".format(inputfile))
    print("Using labels file: {}".format(labelsfile))
    print("Output file will be generated in: {}".format(outputfile))

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
    result.to_csv(outputfile, sep=',', index=False)
