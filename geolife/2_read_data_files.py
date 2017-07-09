import os
import time
import datetime
import config

# Read all the dirs in data_dir
# The dir name is the name of the user
fw1 = open('./' + config.parameters['output_dir'] + '/' + config.parameters['out_file'], 'w')
fw1.write(config.parameters['data_headers'] + '\n')

id = 1
for dir_name in os.listdir(config.parameters['data_dir']):
    dir = './' + config.parameters['data_dir'] + '/' + dir_name
    if os.path.isdir(dir):
        userid = dir_name
        for sub in os.listdir(dir):
            f = './' + config.parameters['data_dir'] + '/' + dir_name + '/' + sub
            if os.path.isfile(f):
                pass
            else:
                # Read the Trajectory directory name
                for sub_plt in os.listdir(f):
                    plt_file = f + '/' + sub_plt
                    if os.path.isfile(plt_file):
                        with open(plt_file, 'r') as f_plt:
                            lines = f_plt.readlines()
                            line_number = 1
                            for line in lines:
                                if line_number >= 7:
                                    line = line.strip('\n')
                                    fields = line.split(',')
                                    uid = int(userid)
                                    t1 = fields[5]
                                    t2 = fields[6]

                                    ts = t1 + ' ' + t2
                                    tmst = round(
                                        time.mktime(datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timetuple()))

                                    to_write = str(id) + ',' + str(uid) \
                                               + ',' + fields[0] + ',' \
                                               + fields[1] + ',' + fields[3] \
                                               + ',' + str(tmst) + '\n'

                                    print(to_write)
                                    fw1.write(to_write)
                                    id += 1
                                line_number += 1

fw1.close()
