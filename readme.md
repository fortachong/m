# Project Mobicampus data preprocessing and learning

## 1. Directory Structure
```console
.
+-- process
	+-- data
	+-- datasets
	+-- models
	+-- testing
	+-- csv2acc.py
	+-- csv2_dataset.py
	+-- csv2_fft_dataset.py
	+-- csv2gps_dataset.py
	+-- json2csv.py
	+-- json2json.py
	+-- predict_acc.py
	+-- prejson.py
	+-- train_dt_acc.py
	+-- train_rf_acc.py
	+-- train_svm_rbf_acc.py
```


## 2. Process
### 2.1. Preprocessing .json file
The file generated by the Apisense Bee application is a json representation of traces collected 
for a device. Each trace is represented by a json object in the form:

```json
{"metadata":{"device":"Android","timestamp":"2017-06-15T08:56:26+00:00"} ...
```

In the original .json file the metadata blocks are not separated by commas or a new line character,
and the next phase requires each metadata block to be in a separate line. Therefore before preprocessing
the .json file, we have to replace `{"metadata":` by `\n{"metadata":`. In linux we can use:

```console
sed 's/{"metadata":/\n{"metadata":/g' original.json > data.json
```

Where `original.json` is the raw file from the Apisense Bee application. The generated `data.json` will be 
used in the next steps

### 2.2. Generating .csv files from a .json file
With the proper .json file we generate .csv files for further analysis and processing of raw data using R or python
pandas dataframes or machine learning tasks using scikit-learn toolkit. Execute:

```console
python json2csv --ifile data.json --odir data
```

The convention is to put all raw .csv files in the `data` directory. This will generate 4 .csv files: `GPS_capture.csv`,
`WIFI_capture.csv`, `ACC_capture.csv`, `ACC_repeated_capture.csv`.

#### 2.2.1. GPS traces raw file
Each row of the file represents a single GPS point with latitude, longitude, altitude, bearing, speed and other data fields.

Column | Description
-------|------------
tid | Identifier of the metadata block (transaction)
header_timestamp | Timestamp of the header
device_id | Identifier of the device
point_id | Identifier of the gps point
accuracy | Estimated accuracy of this location in meters
altitude | Altitude in meters above the WGS84 reference ellipsoid
bearing | Bearing in degrees East of truth North
latitude | Latitude in degrees
longitude | Longitude in degrees
mode | Fix acquisition mode (ACTIVE, PASSIVE)
source | Source that generated the location fix (GPS, NETWORK, UNKNOWN)
speed | Speed in meters/sec over ground
timestamp | Timestamp of the operation
supportedSeeds | Supported seeds
recordDate | Time of the record


#### 2.2.2. Wifi traces raw file
Each row of the file represents a single Wifi access point capture.

Column | Description
-------|------------
tid | Identifier of the metadata block (transaction)
header_timestamp | Timestamp of the header
device_id | Identifier of the device
last_point_id | Identifier of the last gps point
wifi_id | Identifier of the wifi record
authentication | Type of wifi authentication
bssid | Basic service set identifier
frequency | Frequency of carrier
rssi | Received Signal Strength Indication
ssid | Service Set Identifier
timestamp | Timestamp of the operation
supportedSeeds | Supported seeds
recordDate | Time of record


#### 2.2.3. Acceleration raw file
Each row represents a capture of the instantaneous acceleration.

Column | Description
-------|------------
tid | Identifier of the metadata block (transaction)
header_timestamp | Timestamp of the header
device_id | Identifier of the device
acc_id | Identifier of the acceleration record
accuracy | Sensor's current accuracy
deltaX | Absolute difference between the two last traces on the x axis
deltaY | Absolute difference between the two last traces on the y axis
deltaZ | Absolute difference between the two last traces on the z axis
minDelay | Minimal time to wait between two events in microseconds
model | Sensor's model name
vendor | Sensor's vendor name
version | Version of the sensor
x | Instantaneous acceleration on the x axis
y | Instantaneous acceleration on the y axis
z | Instantaneous acceleration on the z axis
supportedSeeds | Supported seeds
timestamp | Timestamp of the operation
recordDate | Time of record


There are repeated records in the acceleration file, they are filtered out of the ACC_capture.csv
file and are recorded in ACC_repeated_capture.csv. The structure of this file is the same as the
acceleration capture file.


### 2.3. Acceleration sensors feature extraction
This process allows to generate a file suitable for training or testing using common machine learning
toolkits like scikit-learn. In order to generate the file we need the raw ACC_capture.csv file generated
in the previous step, a labels file which indicates the label (car, train, tranway, walk) given a start time
and a stop time for a specific device, and two parameters: sampling rate (in Hz) and windows size (in seconds). 
Common values used are windows of 2, 5, and 8 seconds and 30 Hz for sampling rate. 

The structure of the labels file is describe as follows:

Column | Description
-------|------------
device_id | Id of the device
start_timestamp | Start time of the segment labeled as 'label'
stop_timestamp | Stop time of the segment labeled as 'label'
label | Mode of transport (car, train, tramway, walk)

The process will use the labels file and for each row will extract the acceleration records, using a sliding
window of size specified will extract features and build the output file. For example:

```console
python csv2acc_fft_dataset.py --ifile data/ACC_capture.csv --sr 30 --w 2 --l datasets/labels.csv 
```

This will generate an output file in `data/ACC_capture.csv.30.2.features.csv`. This file can be use for training,
or prediction of future captures. For example if we want to predict the mode for new segments labeled:

```console
python csv2acc_fft_dataset.py --ifile data/ACC_capture_2.csv --sr 30 --w 2 --l testing/labels_for_testing.csv 
```

#### 2.3.1. Complete list of features

Feature | Description
--------|------------
f1_mean_x | Mean of acceleration component in x axis
f1_mean_y | Mean of acceleration component in y axis
f1_mean_z | Mean of acceleration component in z axis
f1_mean_acc | Mean of magnitude of acceleration vector
f1_std_x | Standard deviation of acceleration component in x axis
f1_std_y | Standard deviation of acceleration component in y axis
f1_std_z | Standard deviation of acceleration component in z axis
f1_std_acc | Standard deviation of magnitude of acceleration vector
f1_median_x | Median of acceleration component in x axis
f1_median_y | Median of acceleration component in y axis
f1_median_z | Median of acceleration component in z axis
f1_median_acc | Median of magnitude of acceleration vector
f1_min_x | Min of acceleration component in x axis
f1_min_y | Min of acceleration component in y axis
f1_min_z | Min of acceleration component in z axis
f1_min_acc | Min of magnitude of acceleration vector
f1_max_x | Max of acceleration component in x axis
f1_max_y | Max of acceleration component in y axis
f1_max_z | Max of acceleration component in z axis
f1_max_acc | Max of magnitude of acceleration vector
f1_range_x | Range of acceleration component in x axis
f1_range_y | Range of acceleration component in y axis
f1_range_z | Range of acceleration component in z axis
f1_range_acc | Range of magnitude of acceleration vector
f1_iqr_x | Interquartile range of acceleration component in x axis
f1_iqr_y | Interquartile range of acceleration component in y axis
f1_iqr_z | Interquartile range of acceleration component in z axis
f1_iqr_acc | Interquartile range of magnitude of acceleration vector
f1_kurtosis_x | Kurtosis of acceleration component in x axis
f1_kurtosis_y | Kurtosis of acceleration component in y axis
f1_kurtosis_z | Kurtosis of acceleration component in z axis
f1_kurtosis_acc | Kurtosis of magnitude of acceleration vector
f1_skew_x | Skewness of acceleration component in x axis
f1_skew_y | Skewness of acceleration component in y axis
f1_skew_z | Skewness of acceleration component in z axis
f1_skew_acc | Skewness of magnitude of acceleration vector
f2_mean_dx | Mean of delta component in x axis
f2_mean_dy | Mean of delta component in y axis
f2_mean_dz | Mean of delta component in z axis
f2_mean_dacc | Mean of magnitude of delta
f2_std_dx | Standard deviation of delta component in x axis
f2_std_dy | Standard deviation of delta component in y axis
f2_std_dz | Standard deviation of delta component in z axis
f2_std_dacc | Standard of magnitude of delta
f2_median_dx | Median of delta component in x axis
f2_median_dy | Median of delta component in y axis
f2_median_dz | Median of delta component in z axis
f2_median_dacc | Median of magnitude of delta
f2_min_dx | Min of delta component in x axis
f2_min_dy | Min of delta component in y axis
f2_min_dz | Min of delta component in z axis
f2_min_dacc | Min of magnitude of delta
f2_max_dx | Max of delta component in x axis
f2_max_dy | Max of delta component in y axis
f2_max_dz | Max of delta component in z axis
f2_max_dacc | Max of magnitude of delta
f2_range_dx | Range of delta component in x axis
f2_range_dy | Range of delta component in y axis
f2_range_dz | Range of delta component in z axis
f2_range_dacc | Range of magnitude of delta
f2_iqr_dx | Interquartile range of delta component in x axis
f2_iqr_dy | Interquartile range of delta component in y axis
f2_iqr_dz | Interquartile range of delta component in z axis
f2_iqr_dacc | Interquartile of magnitude of delta
f2_kurtosis_dx | Kurtosis of delta component in x axis
f2_kurtosis_dy | Kurtosis of delta component in y axis
f2_kurtosis_dz | Kurtosis of delta component in z axis
f2_kurtosis_dacc | Kurtosis of magnitude of delta
f2_skew_dx | Skewness of delta component in x axis
f2_skew_dy | Skewness of delta component in y axis
f2_skew_dz | Skewness of delta component in z axis
f2_skew_dacc | Skewness of magnitude of delta
f3_abs_fft_1hz | Magnitude of fft of magnitude of acceleration vector at at 1 Hz
f3_abs_fft_2hz | Magnitude of fft of magnitude of acceleration vector at at 2 Hz
f3_abs_fft_3hz | Magnitude of fft of magnitude of acceleration vector at 3 Hz


### 2.4. Learning Algorithms




## 3. Examples:




