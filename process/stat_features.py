import getopt
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import scipy.stats as stats


if __name__ == "__main__":
    inputfile = ''
    outputfile = inputfile + '.frames'
    deviceid = ''
    start = 0
    stop = 0
    # Default values for sampling rate and windows size
    ws = 1

    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:st:w:stp:d", ["ifile=", "ws=", "start=", "stop=", "deviceid="])
    except getopt.GetoptError:
        print('csv2frames.py -i <inputfile> -s <sampling_rate> -w <window_size>')
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print('csv2frames.py -i <inputfile> -s <sampling_rate> -w <window_size>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-st", "--start"):
            start = arg
        elif opt in ("-stp", "--stop"):
            stop = arg
        elif opt in ("-w", "--ws"):
            ws = arg
        elif opt in ("-d", "--deviceid"):
            deviceid = arg
    if inputfile == '':
        print('No input file provided')
        sys.exit(2)
    if deviceid == '':
        print('No device id provided')
        sys.exit(2)

    # If start and stop are not provided default values are extracted from the dataframe
    df = pd.read_csv(inputfile)
    if start == 0 and stop == 0:
        acc_data = df[df.device_id == deviceid].sort_values(by=['timestamp'])
        start = acc_data.timestamp[0]
    else:
        acc_data = df[(df.device_id == deviceid) & (df.timestamp >= start) & (df.timestamp <= stop)].sort_values(by=['timestamp'])

    ws = int(ws)
    window_acceleration = []
    window_delta = []
    it_acc = acc_data.iterrows()
    frame = 0
    curr_start = start
    curr_stop = curr_start + (ws * 1000)
    while True:
        try:
            idx, current_acc = next(it_acc)
        except StopIteration:
            break

        if (current_acc['timestamp'] >= curr_start) and (current_acc['timestamp'] < curr_stop):
            window_acceleration.append(np.linalg.norm([current_acc['x'], current_acc['y'], current_acc['z']]))
            window_delta.append(np.linalg.norm([current_acc['deltaX'], current_acc['deltaY'], current_acc['deltaZ']]))
        else:
            curr_start = curr_stop
            curr_stop = curr_start + (ws * 1000)
            print(window_acceleration)
            window_acceleration = []
            window_delta = []
            window_acceleration.append(np.linalg.norm([current_acc['x'], current_acc['y'], current_acc['z']]))
            window_delta.append(np.linalg.norm([current_acc['deltaX'], current_acc['deltaY'], current_acc['deltaZ']]))
            frame += 1


    print("Frames: ", frame)
