"""
Predict with a previously trained model

--ifile : input file
--m : trained model
--t : a flag 0 or 1. If present and set to 1 it won't use the input file and just
generates the predictions on the test file used for testing the original model

"""
import getopt
import sys
import pandas as pd
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix


# Generates a confusion matrix file and print a report of performance
def generates_report(model, Y, Y_hat, file):
    classes = model['label_encoder'].classes_
    print("Class encoding:")
    for idx, classname in enumerate(classes):
        print("{} : {}".format(str(idx), classname))
    # Perform the prediction on Test Set
    print("Classification Report on Testing Data:")
    print(classification_report(Y, Y_hat))
    print("Confusion Matrix:")
    cm = confusion_matrix(Y, Y_hat)
    cm_data = {'True labels': classes}
    for idx, classname in enumerate(classes):
        cm_data[classname] = cm[:, idx]
    print(cm)
    cm_result = pd.DataFrame(cm_data)
    cm_result.to_csv(file, sep=',', index=False)


def usage():
    print('python predict_acc.py --ifile <input_file> --m <model_file> [--t 1]')
    print()
    print('Example:')
    print('python predict_acc.py --ifile testing/ACC_capture.csv.30.2.features.csv --m models/ACC_capture.csv.30.2.csv.dt.model')
    print('or')
    print('python predict_acc.py --ifile testing/ACC_capture.csv.30.2.features.csv --m models/ACC_capture.csv.30.2.csv.dt.model --t 1')


if __name__ == "__main__":
    inputfile = ''
    modelfile = ''
    test = False
    test_ = 0
    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:m", ["ifile=", "m=", "t="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-m", "--m"):
            modelfile = arg
        elif opt in ("-t", "--t"):
            test_ = arg
    if inputfile == '':
        print('No input file provided')
        usage()
        sys.exit(2)
    if modelfile == '':
        print('No model file provided')
        usage()
        sys.exit(2)
    if test_ == '1':
        test = True

    outputfile = inputfile + '.prediction.csv'
    cmfile = inputfile + '.prediction.cm.csv'

    print("Using model file: {}".format(modelfile))
    print("Using input file: {}".format(inputfile))
    print("Predictions file will be generated in: {}".format(outputfile))
    print("Confusion matrix file will be generated in: {}".format(cmfile))

    # Read the data from inputfile
    df = pd.read_csv(inputfile)

    # Read the model
    model_f = open(modelfile, 'rb')
    model = pickle.load(model_f)

    # Select data
    features = model['features']
    X = df[features]
    search = model['search']

    # If you only want the data with the predicted labels
    # used in the original model:
    if test:
        y_predicted = model['predictions']
    else:
        y_predicted = search.predict(X)

    # Convert predictions to labels
    encoder = model['label_encoder']
    y_predicted_labels = encoder.inverse_transform(y_predicted)

    if test:
        df_x = pd.DataFrame(model['X_test'])
        df_x['label'] = encoder.inverse_transform(model['y_test'])
        df_x['predicted'] = y_predicted_labels
        df_x.to_csv('model.predicted', sep=',', index=False)
        generates_report(model, model['y_test'], y_predicted, cmfile)
    else:
        df['predicted'] = y_predicted_labels
        df.to_csv(outputfile, sep=',', index=False)
        y = encoder.transform(df['label'].values)
        generates_report(model, y, y_predicted, cmfile)
