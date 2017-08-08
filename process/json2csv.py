"""
Reads lines in .json file
Outputs 4 separate csv files for GPS, WIFI and Acceleration for future processing
with usual data analysis tools like R and python

Execute in this order
#bash sed 's/{"metadata":/\n{"metadata":/g' original.json > data.json
To produce a json file with each metadata in a new line,
then use this script

Fields Description:

File: GPS_capture.csv
    tid:                Identifier of the metadata block (transaction)
    header_timestamp:   Timestamp of the header
    device_id:          Identifier of the device
    point_id:           Identifier of the gps point
    accuracy:           Estimated accuracy of this location in meters
    altitude:           Altitude in meters above the WGS84 reference ellipsoid
    bearing:            Bearing in degrees East of truth North
    latitude:           Latitude in degrees
    longitude:          Longitude in degrees
    mode:               Fix acquisition mode (ACTIVE, PASSIVE)
    source:             Source that generated the location fix (GPS, NETWORK, UNKNOWN)
    speed:              Speed in meters/sec over ground
    timestamp:          Timestamp of the operation
    supportedSeeds:     Supported seeds
    recordDate:         Time of record

File: WIFI_capture
    tid:                Identifier of the metadata block (transaction)
    header_timestamp:   Timestamp of the header
    device_id:          Identifier of the device
    last_point_id:      Identifier of the last gps point
    wifi_id:            Identifier of the wifi record
    authentication:     Type of wifi authentication
    bssid:              Basic service set identifier
    frequency:          Frequency of carrier
    rssi:               Received Signal Strength Indication
    ssid:               Service Set Identifier
    timestamp:          Timestamp of the operation
    supportedSeeds:     Supported seeds
    recordDate:         Time of record

File: ACC_capture.csv
    tid:                Identifier of the metadata block (transaction)
    header_timestamp:   Timestamp of the header
    device_id:          Identifier of the device
    acc_id:             Identifier of the acceleration record
    accuracy:           Sensor's current accuracy
    deltaX:             Absolute difference between the two last traces on the x axis
    deltaY:             Absolute difference between the two last traces on the y axis
    deltaZ:             Absolute difference between the two last traces on the z axis
    minDelay:           Minimal time to wait between two events in microseconds
    model:              Sensor's model name
    vendor:             Sensor's vendor name
    version:            Version of the sensor
    x:                  Instantaneous acceleration on the x axis
    y:                  Instantaneous acceleration on the y axis
    z:                  Instantaneous acceleration on the z axis
    supportedSeeds:     Supported seeds
    timestamp:          Timestamp of the operation
    recordDate:         Time of record

File: ACC_repeated_capture.csv
The format is the same as ACC_capture.csv.
There are many records with the same timestamp, that cause problems in extracting features,
therefore these records are filtered out


"""
import json
import sys
import getopt
import codecs


def usage():
    print('python json2csv.py --ifile <input_file> --odir <output_directory>')
    print()
    print('Example:')
    print('python json2csv.py --ifile data.json --odir data')


########################################################################################################################

if __name__ == "__main__":
    inputfile = ''
    output_dir = 'output'
    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--odir"):
            output_dir = arg
    if inputfile == '':
        print('No input file provided')
        sys.exit(2)

    # Read all lines of inputfile
    tid = 1
    point_id = 1
    wifi_id = 1
    acc_id = 1
    GPS_capture_file = 'GPS_capture.csv'
    WIFI_capture_file = 'WIFI_capture.csv'
    ACC_capture_file = 'ACC_capture.csv'
    ACC_rep_capture_file = 'ACC_repeated_capture.csv'
    GPS_f = open(output_dir + '/' + GPS_capture_file, 'w')
    WIFI_f = open(output_dir + '/' + WIFI_capture_file, 'wb')
    ACC_f = open(output_dir + '/' + ACC_capture_file, 'wb')
    ACC_rep_f = open(output_dir + '/' + ACC_rep_capture_file, 'wb')

    GPS_header = 'tid,header_timestamp,device_id,point_id,accuracy,altitude,bearing,latitude,longitude,mode,source,speed,timestamp,supportedSeeds,recordDate\n'
    WIFI_header = 'tid,header_timestamp,device_id,last_point_id,wifi_id,authentication,bssid,frequency,rssi,ssid,timestamp,supportedSeeds,recordDate\n'
    ACC_header = 'tid,header_timestamp,device_id,acc_id,accuracy,deltaX,deltaY,deltaZ,minDelay,model,vendor,version,x,y,z,supportedSeeds,timestamp,recordDate\n'
    ACC_rep_header = 'tid,header_timestamp,device_id,acc_id,accuracy,deltaX,deltaY,deltaZ,minDelay,model,vendor,version,x,y,z,supportedSeeds,timestamp,recordDate\n'
    GPS_f.write(GPS_header)
    WIFI_f.write(WIFI_header.encode('utf-8'))
    ACC_f.write(ACC_header.encode('utf-8'))
    ACC_rep_f.write(ACC_rep_header.encode('utf-8'))

    print("Generating .csv files")
    print("Using input file: {}".format(inputfile))
    print("Output files to be generated:")
    print(output_dir + '/' + GPS_capture_file)
    print(output_dir + '/' + WIFI_capture_file)
    print(output_dir + '/' + ACC_capture_file)
    print(output_dir + '/' + ACC_rep_capture_file)
    print()

    # with open(inputfile, "rb") as fd:
    line_number = 1

    acceleration_timestamps = {}
    with codecs.open(inputfile, 'r', encoding='utf-8', errors='replace') as fd:
        for line in fd:
            print("Processing line", line_number)
            line_number += 1
            if line == "":
                continue

            # line = line.decode("utf-8", "replace")
            data = json.loads(line)
            device_id = data["header"]["id"]
            header_timestamp = data["header"]["ts"]

            for element in data["body"]:
                # Test if onLocationChanged
                if "gps" in element:
                    onLocationChanged = element["gps"]
                    GPS_accuracy = onLocationChanged["accuracy"]
                    GPS_altitude = onLocationChanged["altitude"]
                    GPS_bearing = onLocationChanged["bearing"]
                    GPS_latitude = onLocationChanged["latitude"]
                    GPS_longitude = onLocationChanged["longitude"]
                    GPS_mode = onLocationChanged["mode"]
                    GPS_source = onLocationChanged["source"]
                    GPS_speed = onLocationChanged["speed"]
                    GPS_timestamp = onLocationChanged["timestamp"]
                    GPS_supportedSeeds = onLocationChanged["supportedSeeds"]
                    GPS_recordDate = element["recordDate"]

                    # Write Line to file
                    output_line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        tid,
                        header_timestamp,
                        device_id,
                        point_id,
                        GPS_accuracy,
                        GPS_altitude,
                        GPS_bearing,
                        GPS_latitude,
                        GPS_longitude,
                        GPS_mode,
                        GPS_source,
                        GPS_speed,
                        GPS_timestamp,
                        GPS_supportedSeeds,
                        GPS_recordDate
                    )
                    print(output_line)
                    GPS_f.write(output_line)
                    point_id += 1

                elif "authentication" in element:
                    WIFI_authentication = element["authentication"]
                    WIFI_bssid = element["bssid"]
                    WIFI_frequency = element["frequency"]
                    WIFI_rssi = element["rssi"]
                    WIFI_ssid_b = element["ssid"].encode('utf-8', errors='replace')
                    WIFI_ssid = element["ssid"]
                    WIFI_ssid = WIFI_ssid.replace(',', '_')
                    WIFI_timestamp = element["timestamp"]
                    WIFI_supportedSeeds = element["supportedSeeds"]
                    WIFI_recordDate = element["recordDate"]
                    # print(WIFI_ssid)
                    # print(WIFI_ssid.encode("utf-8")) # , errors='replace'))

                    # Write Line to file
                    output_line = "{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        tid,
                        header_timestamp,
                        device_id,
                        point_id,
                        wifi_id,
                        WIFI_authentication,
                        WIFI_bssid,
                        WIFI_frequency,
                        WIFI_rssi,
                        WIFI_ssid,
                        WIFI_timestamp,
                        WIFI_supportedSeeds,
                        WIFI_recordDate
                    )
                    # print(output_line)
                    WIFI_f.write(output_line.encode('utf-8', errors='replace'))
                    wifi_id += 1
                elif "wifiScan" in element:
                    wifiScan = element["wifiScan"]
                    WIFI_authentication = wifiScan["authentication"]
                    WIFI_bssid = wifiScan["bssid"]
                    WIFI_frequency = wifiScan["frequency"]
                    WIFI_rssi = wifiScan["rssi"]
                    WIFI_ssid_b = wifiScan["ssid"].encode('utf-8', errors='replace')
                    WIFI_ssid = wifiScan["ssid"]
                    WIFI_ssid = WIFI_ssid.replace(',', '_')
                    WIFI_timestamp = wifiScan["timestamp"]
                    WIFI_supportedSeeds = wifiScan["supportedSeeds"]
                    WIFI_recordDate = element["recordDate"]
                    output_line = "{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        tid,
                        header_timestamp,
                        device_id,
                        point_id,
                        wifi_id,
                        WIFI_authentication,
                        WIFI_bssid,
                        WIFI_frequency,
                        WIFI_rssi,
                        WIFI_ssid,
                        WIFI_timestamp,
                        WIFI_supportedSeeds,
                        WIFI_recordDate
                    )
                    # print(output_line)
                    WIFI_f.write(output_line.encode('utf-8', errors='replace'))
                    wifi_id += 1
                elif "accelerometer" in element:
                    accelerometer = element["accelerometer"]
                    if "accuracy" in accelerometer:
                        ACC_accuracy = accelerometer["accuracy"]
                    else:
                        ACC_accuracy = 'NONE'
                    ACC_deltaX = accelerometer["deltaX"]
                    ACC_deltaY = accelerometer["deltaY"]
                    ACC_deltaZ = accelerometer["deltaZ"]
                    ACC_minDelay = accelerometer["minDelay"]
                    ACC_model = accelerometer["model"]
                    ACC_vendor = accelerometer["vendor"]
                    ACC_version = accelerometer["version"]
                    ACC_x = accelerometer["x"]
                    ACC_y = accelerometer["y"]
                    ACC_z = accelerometer["z"]
                    ACC_supportedSeeds = accelerometer["supportedSeeds"]
                    ACC_timestamp = accelerometer["timestamp"]
                    ACC_recordDate = element["recordDate"]
                    output_line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        tid,
                        header_timestamp,
                        device_id,
                        acc_id,
                        ACC_accuracy,
                        ACC_deltaX,
                        ACC_deltaY,
                        ACC_deltaZ,
                        ACC_minDelay,
                        ACC_model,
                        ACC_vendor,
                        ACC_version,
                        ACC_x,
                        ACC_y,
                        ACC_z,
                        ACC_supportedSeeds,
                        ACC_timestamp,
                        ACC_recordDate
                    )
                    # print(output_line)
                    # Important verify repeated data for that timestamp
                    if device_id not in acceleration_timestamps:
                        acceleration_timestamps[device_id] = {accelerometer["timestamp"]: 1}
                        ACC_f.write(output_line.encode('utf-8', errors='replace'))
                    elif accelerometer["timestamp"] not in acceleration_timestamps[device_id]:
                        acceleration_timestamps[device_id][accelerometer["timestamp"]] = 1
                        ACC_f.write(output_line.encode('utf-8', errors='replace'))
                    else:
                        acceleration_timestamps[device_id][accelerometer["timestamp"]] += 1
                        ACC_rep_f.write(output_line.encode('utf-8', errors='replace'))
                    acc_id += 1
                else:
                    pass
            tid += 1