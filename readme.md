# Project Mobicampus

## Directory Structure
```console
.
+-- m
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


## Process
### Preprocessing .json file
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

### Generating .csv files from a .json file
With the proper .json file we generate .csv files for further analysis and processing of raw data using R or python
pandas dataframes or machine learning tasks using scikit-learn toolkit. Execute:

```console
python json2csv --ifile data.json --odir data
```

The convention is to put all raw .csv files in the `data` directory. This will generate 4 .csv files: `GPS_capture.csv`,
`WIFI_capture.csv`, `ACC_capture.csv`, `ACC_repeated_capture.csv`.

#### GPS traces raw file
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


#### Wifi traces raw file
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


#### Acceleration raw file
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


### Acceleration sensors feature extraction



###

### Learning


#### Output file format
The input file is the raw input csv generated from the json extraction process. It is
a csv file with 18 columns:

Column | Description
-------|------------
tid |
header_timestamp |
device_id |
acc_id |
accuracy |
deltaX |
deltaY |
deltaZ |
minDelay |
model |
vendor |
version |
x |
y |
z |
supportedSeeds |
timestamp |
recordDate |




#### Labels file format


$