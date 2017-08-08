"""
Reads lines in .json file
Outputs another .json file for displaying in a javascript page

Execute in this order (if not previously execute)
#bash sed 's/{"metadata":/\n{"metadata":/g' original.json > data.json
To produce a json file with each metadata in a new line,
then use this script

"""

import json
import sys
import getopt
import codecs
import collections


def usage():
    print('python json2json.py --ifile <input_file> --odir <output_directory>')
    print()
    print('Example:')
    print('python json2json.py --ifile data.json --odir data')


########################################################################################################################

if __name__ == "__main__":
    inputfile = ''
    output_dir = 'data'
    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            ussage()
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

    output_file = 'data_2.json'
    # output_f = open(output_dir + '/' + output_file, 'w')
    data_json = {}

    gps_records = {}
    wifi_records = {}
    acceleration_records = {}
    acceleration_repeated_records = {}
    acceleration_timestamps = {}
    line_number = 1
    with codecs.open(inputfile, 'r', encoding='utf-8', errors='replace') as fd:
        for line in fd:
            print("Processing line", line_number)
            line_number += 1
            line = line.strip()
            if line == "":
                continue

            data = json.loads(line)
            device_id = data["header"]["id"]
            header_timestamp = data["header"]["ts"]

            for element in data["body"]:
                # GPS records
                if "gps" in element:
                    onLocationChanged = element["gps"]
                    record = {'tid': tid,
                              'point_id': point_id,
                              'accuracy': onLocationChanged["accuracy"],
                              'altitude': onLocationChanged["altitude"],
                              'bearing': onLocationChanged["bearing"],
                              'latitude': onLocationChanged["latitude"],
                              'longitude': onLocationChanged["longitude"],
                              'mode': onLocationChanged["mode"],
                              'source': onLocationChanged["source"],
                              'speed': onLocationChanged["speed"],
                              'timestamp': onLocationChanged["timestamp"],
                              'supportedSeeds': onLocationChanged["supportedSeeds"],
                              'recordDate': element["recordDate"]
                              }

                    # Add to the gps_records dictionary indexed by device_id
                    if device_id in gps_records:
                        gps_records[device_id].append(record)
                    else:
                        gps_records[device_id] = []
                        gps_records[device_id].append(record)
                    point_id += 1
                # WIFI record
                elif "authentication" in element:
                    WIFI_ssid = element["ssid"]
                    WIFI_ssid = WIFI_ssid.replace(',', '_')
                    record = {'tid': tid,
                              'point_id': point_id,
                              'wifi_id': wifi_id,
                              'authentication': element["authentication"],
                              'bssid': element["bssid"],
                              'frequency': element["frequency"],
                              'rssi': element["rssi"],
                              'ssid': WIFI_ssid,
                              'timestamp': element["timestamp"],
                              'suportedSeeds': element["supportedSeeds"],
                              'recordDate': element["recordDate"]
                              }
                    # Add to the wifi_records dictionary indexed by device_id
                    if device_id in wifi_records:
                        wifi_records[device_id].append(record)
                    else:
                        wifi_records[device_id] = []
                        wifi_records[device_id].append(record)
                    wifi_id += 1
                # WIFI record new version
                elif "wifiScan" in element:
                    wifiScan = element["wifiScan"]
                    WIFI_ssid = wifiScan["ssid"]
                    WIFI_ssid = WIFI_ssid.replace(',', '_')
                    record ={'tid': tid,
                             'point_id': point_id,
                             'wifi_id': wifi_id,
                             'authentication': wifiScan["authentication"],
                             'bssid': wifiScan["bssid"],
                             'frequency': wifiScan["frequency"],
                             'rssi': wifiScan["rssi"],
                             'ssid': WIFI_ssid,
                             'timestamp': wifiScan["timestamp"],
                             'supportedSeeds': wifiScan["supportedSeeds"],
                             'recordDate': element["recordDate"]
                             }
                    # Add to the wifi_records dictionary indexed by device_id
                    if device_id in wifi_records:
                        wifi_records[device_id].append(record)
                    else:
                        wifi_records[device_id] = []
                        wifi_records[device_id].append(record)
                    wifi_id += 1
                # In Accelerometer data record repeated in another dictionary
                elif "accelerometer" in element:
                    accelerometer = element["accelerometer"]
                    if "accuracy" in accelerometer:
                        ACC_accuracy = accelerometer["accuracy"]
                    else:
                        ACC_accuracy = 'NONE'
                    record = {'tid': tid,
                              'acc_id': acc_id,
                              'accuracy': ACC_accuracy,
                              'deltaX': accelerometer["deltaX"],
                              'deltaY': accelerometer["deltaY"],
                              'deltaZ': accelerometer["deltaZ"],
                              'minDelay': accelerometer["minDelay"],
                              'model': accelerometer["model"],
                              'vendor': accelerometer["vendor"],
                              'version': accelerometer["version"],
                              'x': accelerometer["x"],
                              'y': accelerometer["y"],
                              'z': accelerometer["z"],
                              'supportedSeeds': accelerometer["supportedSeeds"],
                              'timestamp': accelerometer["timestamp"],
                              'recordDate': element["recordDate"]
                              }
                    if device_id not in acceleration_timestamps:
                        acceleration_timestamps[device_id] = {accelerometer["timestamp"]: 1}
                        if device_id in acceleration_records:
                            acceleration_records[device_id].append(record)
                        else:
                            acceleration_records[device_id] = []
                            acceleration_records[device_id].append(record)
                    elif accelerometer["timestamp"] not in acceleration_timestamps[device_id]:
                        acceleration_timestamps[device_id][accelerometer["timestamp"]] = 1
                        if device_id in acceleration_records:
                            acceleration_records[device_id].append(record)
                        else:
                            acceleration_records[device_id] = []
                            acceleration_records[device_id].append(record)
                    else:
                        acceleration_timestamps[device_id][accelerometer["timestamp"]] += 1
                        if device_id in acceleration_repeated_records:
                            acceleration_repeated_records[device_id].append(record)
                        else:
                            acceleration_repeated_records[device_id] = []
                            acceleration_repeated_records[device_id].append(record)
                    acc_id += 1

    data_json['gps'] = gps_records
    data_json['wifi'] = wifi_records
    data_json['acceleration'] = acceleration_records
    data_json['repeated_acceleration'] = acceleration_repeated_records

    # Build an index for timestamps
    data_json['gps_timestamps'] = {}

    for device_id, records in gps_records.items():
        gps_timestamps = {}
        for idx, record in enumerate(records):
            gps_timestamps[record["timestamp"]] = idx
        gps_timestamps = collections.OrderedDict(sorted(gps_timestamps.items(), key=lambda t:t[0]))
        print(gps_timestamps)
        data_json['gps_timestamps'][device_id] = gps_timestamps

    print("Writing json file...")
    with open(output_dir + '/' + output_file, 'w', encoding='utf-8', errors='replace') as output_f:
        json.dump(data_json, output_f, indent=4, ensure_ascii=True)

