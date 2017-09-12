"""
Generates a final ACC_capture.csv with all the data and respective labels
for acceleration, and generates and .features file
Added FFT calculations

Parameters
--ifile : input csv file with the acceleration values
--ws : a windows size
--sr : the sampling rate for the signal
--label : the labels file

"""

import getopt
import sys
import pandas as pd
import numpy as np
from numpy.linalg import norm
from scipy.interpolate import interp1d
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import scipy.stats as stats


# find a value of the frequency
def find_frequency(frequency, frequency_array):
    n = len(frequency_array)
    begin = 0
    end = n - 1
    mid = 0
    while True:
        if begin > end:
            break
        mid = int((begin + end) / 2)
        if frequency == frequency_array[mid]:
            return mid
        else:
            if frequency < frequency_array[mid]:
                end = mid - 1
            else:
                begin = mid + 1
    return mid


# abs of the fft transform at a specific frequency
# xs: numpy array with the data in the window
# sampling_rate: rate of sampling in Hz
# f: the frequency at which we want to extract the value
def fft_abs_at_f(xs, sampling_rate, f):
    n = len(xs)
    s = fft(xs)
    f_interval = 1 / sampling_rate
    fs = fftfreq(n, f_interval)
    if n % 2 == 1:
        l = (n - 1) / 2
    else:
        l = n / 2 - 1
    # print(l)
    freqs = fs[:int(l)+1]
    # print(s)
    # print(s[0])
    # print(abs(s))
    # print(fs)
    f_idx = find_frequency(f, freqs)
    return abs(s[f_idx])


# Calculate statistical features and returns a dictionary with all the frames
def st_features_frames(data_frame, data_frame_speed, window_size, sampling_rate):
    time_interval = (1.0 / sampling_rate) * 1000
    ws = window_size * 1000

    # Starting timestamp
    t_start = data_frame['timestamp'].iloc[0]
    # Normalize the timestamp timeline to start from zero
    time_data = data_frame.timestamp - t_start
    # End timestamp
    # time_data.count() contains the number of captured points
    t_last = time_data.iloc[time_data.count() - 1]
    # Number of time points according to the sampling rate
    number_of_points = round((t_last - 1) / time_interval)
    # Time line generated according to the time interval (sampling rate)
    # and the last timestamp
    time_line = np.linspace(0, t_last, number_of_points, endpoint=True)

    # process speed timeline for interpolation
    if not data_frame_speed.empty:
        t_start_sp = data_frame_speed['timestamp'].iloc[0]
        time_data_sp = data_frame_speed.timestamp - t_start_sp

        lin_function_speed = interp1d(time_data_sp, data_frame_speed.speed, kind='nearest')
        speed_values = lin_function_speed(time_line)

    # print(time_line)

    # Interpolate linearly x, y, z, and deltaX, deltaY, deltaZ
    lin_function_x = interp1d(time_data, data_frame.x, kind='linear')
    x_values = lin_function_x(time_line)
    lin_function_y = interp1d(time_data, data_frame.y, kind='linear')
    y_values = lin_function_y(time_line)
    lin_function_z = interp1d(time_data, data_frame.z, kind='linear')
    z_values = lin_function_z(time_line)
    lin_function_delta_x = interp1d(time_data, data_frame.deltaX, kind='linear')
    deltax_values = lin_function_x(time_line)
    lin_function_delta_y = interp1d(time_data, data_frame.deltaY, kind='linear')
    deltay_values = lin_function_delta_y(time_line)
    lin_function_delta_z = interp1d(time_data, data_frame.deltaZ, kind='linear')
    deltaz_values = lin_function_delta_z(time_line)
    # Calculate the values of the norms of x, y, z and deltaX, deltaY, deltaZ
    vs = len(x_values)
    v = np.concatenate((x_values, y_values, z_values))
    v = v.reshape((3, vs))
    norm_acceleration = norm(v, axis=0)

    vs = len(deltax_values)
    v = np.concatenate((deltax_values, deltay_values, deltaz_values))
    v = v.reshape((3, vs))
    norm_delta = norm(v, axis=0)

    # Creates the frames structure
    frames = {}
    first = 0
    index = 0
    frame_number = 0
    for index, time_point in enumerate(time_line):
        if time_point > first + ws:
            frames[frame_number] = index
            frame_number += 1
            first = time_point

    frames[frame_number] = index + 1
    # All the features to be calculated:
    # Features on acceleration
    f1_mean_x = []
    f1_mean_y = []
    f1_mean_z = []
    f1_mean_acc = []
    f1_std_x = []
    f1_std_y = []
    f1_std_z = []
    f1_std_acc = []
    f1_median_x = []
    f1_median_y = []
    f1_median_z = []
    f1_median_acc = []
    f1_min_x = []
    f1_min_y = []
    f1_min_z = []
    f1_min_acc = []
    f1_max_x = []
    f1_max_y = []
    f1_max_z = []
    f1_max_acc = []
    f1_range_x = []
    f1_range_y = []
    f1_range_z = []
    f1_range_acc = []
    f1_iqr_x = []
    f1_iqr_y = []
    f1_iqr_z = []
    f1_iqr_acc = []
    f1_kurtosis_x = []
    f1_kurtosis_y = []
    f1_kurtosis_z = []
    f1_kurtosis_acc = []
    f1_skew_x = []
    f1_skew_y = []
    f1_skew_z = []
    f1_skew_acc = []
    # Features on delta acceleration
    f2_mean_dx = []
    f2_mean_dy = []
    f2_mean_dz = []
    f2_mean_dacc = []
    f2_std_dx = []
    f2_std_dy = []
    f2_std_dz = []
    f2_std_dacc = []
    f2_median_dx = []
    f2_median_dy = []
    f2_median_dz = []
    f2_median_dacc = []
    f2_min_dx = []
    f2_min_dy = []
    f2_min_dz = []
    f2_min_dacc = []
    f2_max_dx = []
    f2_max_dy = []
    f2_max_dz = []
    f2_max_dacc = []
    f2_range_dx = []
    f2_range_dy = []
    f2_range_dz = []
    f2_range_dacc = []
    f2_iqr_dx = []
    f2_iqr_dy = []
    f2_iqr_dz = []
    f2_iqr_dacc = []
    f2_kurtosis_dx = []
    f2_kurtosis_dy = []
    f2_kurtosis_dz = []
    f2_kurtosis_dacc = []
    f2_skew_dx = []
    f2_skew_dy = []
    f2_skew_dz = []
    f2_skew_dacc = []
    # FFT based features
    f3_abs_fft_1hz = []
    f3_abs_fft_2hz = []
    f3_abs_fft_3hz = []
    # Speed from gps capture
    f4_speed = []

    # Slice data to calculate aggregates over frames:
    initial = 0
    frame_numbers = []
    for frame_number, stop in frames.items():
        x = x_values[initial:stop]
        y = y_values[initial:stop]
        z = z_values[initial:stop]
        acc = norm_acceleration[initial:stop]
        if not data_frame_speed.empty:
            sp = speed_values[initial:stop]


        dx = deltax_values[initial:stop]
        dy = deltay_values[initial:stop]
        dz = deltaz_values[initial:stop]
        dacc = norm_delta[initial:stop]

        frame_numbers.append(frame_number)

        # f1 type features
        f1_mean_x.append(np.mean(x))
        f1_mean_y.append(np.mean(y))
        f1_mean_z.append(np.mean(z))
        f1_mean_acc.append(np.mean(acc))
        f1_std_x.append(np.std(x))
        f1_std_y.append(np.std(y))
        f1_std_z.append(np.std(z))
        f1_std_acc.append(np.std(acc))
        f1_median_x.append(np.median(x))
        f1_median_y.append(np.median(y))
        f1_median_z.append(np.median(z))
        f1_median_acc.append(np.median(acc))
        f1_min_x.append(np.min(x))
        f1_min_y.append(np.min(y))
        f1_min_z.append(np.min(z))
        f1_min_acc.append(np.min(acc))
        f1_max_x.append(np.max(x))
        f1_max_y.append(np.max(y))
        f1_max_z.append(np.max(z))
        f1_max_acc.append(np.max(acc))
        f1_range_x.append(np.ptp(x))
        f1_range_y.append(np.ptp(y))
        f1_range_z.append(np.ptp(z))
        f1_range_acc.append(np.ptp(acc))
        f1_iqr_x.append(stats.iqr(x))
        f1_iqr_y.append(stats.iqr(y))
        f1_iqr_z.append(stats.iqr(z))
        f1_iqr_acc.append(stats.iqr(acc))
        f1_kurtosis_x.append(stats.kurtosis(x))
        f1_kurtosis_y.append(stats.kurtosis(y))
        f1_kurtosis_z.append(stats.kurtosis(z))
        f1_kurtosis_acc.append(stats.kurtosis(acc))
        f1_skew_x.append(stats.skew(x))
        f1_skew_y.append(stats.skew(y))
        f1_skew_z.append(stats.skew(z))
        f1_skew_acc.append(stats.skew(acc))
        # f2 type features
        f2_mean_dx.append(np.mean(dx))
        f2_mean_dy.append(np.mean(dy))
        f2_mean_dz.append(np.mean(dz))
        f2_mean_dacc.append(np.mean(dacc))
        f2_std_dx.append(np.std(dx))
        f2_std_dy.append(np.std(dy))
        f2_std_dz.append(np.std(dz))
        f2_std_dacc.append(np.std(dacc))
        f2_median_dx.append(np.median(dx))
        f2_median_dy.append(np.median(dy))
        f2_median_dz.append(np.median(dz))
        f2_median_dacc.append(np.median(dacc))
        f2_min_dx.append(np.min(dx))
        f2_min_dy.append(np.min(dy))
        f2_min_dz.append(np.min(dz))
        f2_min_dacc.append(np.min(dacc))
        f2_max_dx.append(np.max(dx))
        f2_max_dy.append(np.max(dy))
        f2_max_dz.append(np.max(dz))
        f2_max_dacc.append(np.max(dacc))
        f2_range_dx.append(np.ptp(dx))
        f2_range_dy.append(np.ptp(dy))
        f2_range_dz.append(np.ptp(dz))
        f2_range_dacc.append(np.ptp(dacc))
        f2_iqr_dx.append(stats.iqr(dx))
        f2_iqr_dy.append(stats.iqr(dy))
        f2_iqr_dz.append(stats.iqr(dz))
        f2_iqr_dacc.append(stats.iqr(dacc))
        f2_kurtosis_dx.append(stats.kurtosis(dx))
        f2_kurtosis_dy.append(stats.kurtosis(dy))
        f2_kurtosis_dz.append(stats.kurtosis(dz))
        f2_kurtosis_dacc.append(stats.kurtosis(dacc))
        f2_skew_dx.append(stats.skew(dx))
        f2_skew_dy.append(stats.skew(dy))
        f2_skew_dz.append(stats.skew(dz))
        f2_skew_dacc.append(stats.skew(dacc))

        # FFT 1, 2, 3 Hz on magnitude of Acceleration vector
        f3_abs_fft_1hz.append(fft_abs_at_f(acc, sampling_rate, 1))
        f3_abs_fft_2hz.append(fft_abs_at_f(acc, sampling_rate, 2))
        f3_abs_fft_3hz.append(fft_abs_at_f(acc, sampling_rate, 3))

        # Speed from gps
        if data_frame_speed.empty:
            f4_speed.append(0)
        else:
            f4_speed.append(np.mean(sp))

        initial = stop

    features = {'frame': frame_numbers,
                'f1_mean_x': f1_mean_x,
                'f1_mean_y': f1_mean_y,
                'f1_mean_z': f1_mean_z,
                'f1_mean_acc': f1_mean_acc,
                'f1_std_x': f1_std_x,
                'f1_std_y': f1_std_y,
                'f1_std_z': f1_std_z,
                'f1_std_acc': f1_std_acc,
                'f1_median_x': f1_median_x,
                'f1_median_y': f1_median_y,
                'f1_median_z': f1_median_z,
                'f1_median_acc': f1_median_acc,
                'f1_min_x': f1_min_x,
                'f1_min_y': f1_min_y,
                'f1_min_z': f1_min_z,
                'f1_min_acc': f1_min_acc,
                'f1_max_x': f1_max_x,
                'f1_max_y': f1_max_y,
                'f1_max_z': f1_max_z,
                'f1_max_acc': f1_max_acc,
                'f1_range_x': f1_range_x,
                'f1_range_y': f1_range_y,
                'f1_range_z': f1_range_z,
                'f1_range_acc': f1_range_acc,
                'f1_iqr_x': f1_iqr_x,
                'f1_iqr_y': f1_iqr_y,
                'f1_iqr_z': f1_iqr_z,
                'f1_iqr_acc': f1_iqr_acc,
                'f1_kurtosis_x': f1_kurtosis_x,
                'f1_kurtosis_y': f1_kurtosis_y,
                'f1_kurtosis_z': f1_kurtosis_z,
                'f1_kurtosis_acc': f1_kurtosis_acc,
                'f1_skew_x': f1_skew_x,
                'f1_skew_y': f1_skew_y,
                'f1_skew_z': f1_skew_z,
                'f1_skew_acc': f1_skew_acc,
                'f2_mean_dx': f2_mean_dx,
                'f2_mean_dy': f2_mean_dy,
                'f2_mean_dz': f2_mean_dz,
                'f2_mean_dacc': f2_mean_dacc,
                'f2_std_dx': f2_std_dx,
                'f2_std_dy': f2_std_dy,
                'f2_std_dz': f2_std_dz,
                'f2_std_dacc': f2_std_dacc,
                'f2_median_dx': f2_median_dx,
                'f2_median_dy': f2_median_dy,
                'f2_median_dz': f2_median_dz,
                'f2_median_dacc': f2_median_dacc,
                'f2_min_dx': f2_min_dx,
                'f2_min_dy': f2_min_dy,
                'f2_min_dz': f2_min_dz,
                'f2_min_dacc': f2_min_dacc,
                'f2_max_dx': f2_max_dx,
                'f2_max_dy': f2_max_dy,
                'f2_max_dz': f2_max_dz,
                'f2_max_dacc': f2_max_dacc,
                'f2_range_dx': f2_range_dx,
                'f2_range_dy': f2_range_dy,
                'f2_range_dz': f2_range_dz,
                'f2_range_dacc': f2_range_dacc,
                'f2_iqr_dx': f2_iqr_dx,
                'f2_iqr_dy': f2_iqr_dy,
                'f2_iqr_dz': f2_iqr_dz,
                'f2_iqr_dacc': f2_iqr_dacc,
                'f2_kurtosis_dx': f2_kurtosis_dx,
                'f2_kurtosis_dy': f2_kurtosis_dy,
                'f2_kurtosis_dz': f2_kurtosis_dz,
                'f2_kurtosis_dacc': f2_kurtosis_dacc,
                'f2_skew_dx': f2_skew_dx,
                'f2_skew_dy': f2_skew_dy,
                'f2_skew_dz': f2_skew_dz,
                'f2_skew_dacc': f2_skew_dacc,
                'f3_abs_fft_1hz': f3_abs_fft_1hz,
                'f3_abs_fft_2hz': f3_abs_fft_2hz,
                'f3_abs_fft_3hz': f3_abs_fft_3hz,
                'f4_speed': f4_speed
                }
    return features

########################################################################################################################


def usage():
    print('python csv2acc_speed_fft_dataset.py --afile <acc_file> --sfile <speed_file> --sr <sampling_rate> --w <window_size> --l <labels_file>')
    print()
    print('Example:')
    print('python csv2acc_speed_fft_dataset.py --afile data/ACC_capture.csv --sfile data/GPS_capture.csv --sr 30 --w 2 --l datasets/labels.csv')

if __name__ == "__main__":
    acc_file = ''
    speed_file = ''
    labelsfile = ''

    # Default values for sampling rate and windows size
    sr = 35
    ws = 1

    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "ha:v:s:w:l", ["afile=", "sfile=", "sr=", "ws=", "labels="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in options:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-a", "--afile"):
            acc_file = arg
        elif opt in ("-v", "--sfile"):
            speed_file = arg
        elif opt in ("-s", "--sr"):
            sr = arg
        elif opt in ("-w", "--ws"):
            ws = arg
        elif opt in ("-l", "--labels"):
            labelsfile = arg

    if acc_file == '':
        print('No acceleration file provided')
        usage()
        sys.exit(2)
    if speed_file == '':
        print('No speed file provided')
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

    # Sample rate and window size
    outputfile = acc_file + '.' + sr + '.' + ws + '.speed.features.csv'
    sr = float(sr)
    ws = float(ws)
    print("Using acceleration file: {}".format(acc_file))
    print("Using speed file: {}".format(speed_file))
    print("Using sample rate: {0:.2f} hz".format(sr))
    print("Using windows size: {0:.2f} sec".format(ws))
    print("Using labels file: {}".format(labelsfile))
    print("Output file will be generated in: {}".format(outputfile))

    ## exit(0)
    # Labels file
    df_labels = pd.read_csv(labelsfile)
    n_records = df_labels.shape[0]
    n = 1
    # Data file
    df = pd.read_csv(acc_file)
    df_speed = pd.read_csv(speed_file)


    # Iterate through all the labels:
    features_dfs = []
    for index, label in df_labels.iterrows():
        pct = float(n) / n_records
        print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(pct * 50), pct * 100), end="", flush=True)

        # Select those rows from df with device_id,
        # and timestamp between start_timestamp and stop_timestamp
        mask = (df['device_id'] == label['device_id']) & (df['timestamp'] >= label['start_timestamp']) \
               & (df['timestamp'] <= label['stop_timestamp'])
        data = df.loc[mask].sort_values(by=['timestamp'])
        # print(label['device_id'], label['start_timestamp'], label['stop_timestamp'])


        mask_speed = (df_speed['device_id'] == label['device_id']) & (df_speed['timestamp'] >= label['start_timestamp']) \
               & (df_speed['timestamp'] <= label['stop_timestamp'])
        data_speed = df_speed.loc[mask_speed].sort_values(by=['timestamp'])

        #print(label['device_id'])
        #print(label['start_timestamp'])
        #print(label['stop_timestamp'])

        #print(data_speed.head)
        #exit()

        if data.empty:
            print("\nAlert: No data found between the specified timestamps {} and {}".format(label['start_timestamp'],
                                                                                           label['stop_timestamp']))
        else:
            features = st_features_frames(data, data_speed, ws, sr)
            df_features = pd.DataFrame(features)
            df_features['device_id'] = label['device_id']
            df_features['start_timestamp'] = label['start_timestamp']
            df_features['stop_timestamp'] = label['stop_timestamp']
            df_features['label'] = label['label']
            features_dfs.append(df_features)

        n += 1

    if len(features_dfs):
        result = pd.concat(features_dfs)
        result.to_csv(outputfile, sep=',', index=False)
        print("\nFile generated")