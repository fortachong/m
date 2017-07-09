"""
Using the data in the table labels, generate a csv file associating
a point with the corresponding label
"""
import config
import time
import pandas

# Use the 10% of the dataset
fd = open(config.parameters['output_dir'] + '/' + config.parameters['out_traces_labels'], 'w')
fd.write('trace_id,label_id\n')

df = pandas.read_csv(config.parameters['output_dir'] + '/' + config.parameters['input_10_percent_file'])
df_labels = pandas.read_csv(config.parameters['output_dir'] + '/' + config.parameters['out_labels'])
users = df.userid.unique()
for user in users:
    # Get all the traces for that user
    traces = df[df.userid == user].sort_values(by=['timestamp'])
    # Get all the labels for taht user
    labels = df_labels[df_labels.userid == user].sort_values(by=['start_timestamp'])

    it_traces = traces.iterrows()
    it_labels = labels.iterrows()

    # First Label
    try:
        idx_l, current_label = next(it_labels)
    except StopIteration:
        exit(0)

    # First Trace
    try:
        idx_t, current_trace = next(it_traces)
    except StopIteration:
        exit(0)

    while True:
        # Alternatives:
        # tr.t < l.start_t -> advance the trace
        # tr.t >= l.start_t and tr.t <= l.stop_t -> advance the trace
        # tr.t > l.stop_t -> advance the label
        if current_trace['timestamp'] < current_label['start_timestamp']:
            try:
                idx_t, current_trace = next(it_traces)
            except StopIteration:
                break
        elif (current_trace['timestamp'] >= current_label['start_timestamp']) and (current_trace['timestamp'] <= current_label['stop_timestamp']):
            # print(current_trace['id'], current_trace['timestamp'], current_label['id'], current_label['start_timestamp'], current_label['stop_timestamp'])
            fd.write('{},{}\n'.format(current_trace['id'], current_label['id']))
            try:
                idx_t, current_trace = next(it_traces)
            except StopIteration:
                break
        elif current_trace['timestamp'] > current_label['stop_timestamp']:
            try:
                idx_l, current_label = next(it_labels)
            except StopIteration:
                break
        else:
            break



