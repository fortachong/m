import os
import time
import datetime
import config

# Read all the dirs in data_dir
# The dir name is the name of the user
fw2 = open('./' + config.parameters['output_dir'] + '/' + config.parameters['out_labels'], 'w')
fw2.write(config.parameters['label_headers'] + '\n')

id = 1
for dir_name in os.listdir(config.parameters['data_dir']):
    dir = './' + config.parameters['data_dir'] + '/' + dir_name
    if os.path.isdir(dir):
        userid = dir_name
        for sub in os.listdir(dir):
            f = './' + config.parameters['data_dir'] + '/' + dir_name + '/' + sub
            if os.path.isfile(f):
                # Verify is it a labels.txt file
                if sub == config.parameters['labels_filename']:
                    with open(f, 'r') as fl:
                        lines = fl.readlines()
                        first_line = True
                        for line in lines:
                            if not first_line:
                                line = line.replace('\r', '')
                                to_write = line.replace('\t', ',')
                                fields = to_write.split(',')
                                t1 = fields[0]
                                t2 = fields[1]
                                label = fields[2]
                                uid = int(userid)

                                tmst1 = round(time.mktime(datetime.datetime.strptime(t1, "%Y/%m/%d %H:%M:%S").timetuple()))
                                tmst2 = round(time.mktime(datetime.datetime.strptime(t2, "%Y/%m/%d %H:%M:%S").timetuple()))

                                to_write = str(id) + ',' + str(uid) + ',' + str(tmst1) + ',' + str(tmst2) + ',' + label
                                id += 1
                                print(to_write)
                                fw2.write(to_write)
                            first_line = False
fw2.close()
