"""
Train using the dataset using a Random Forest classification method
Toolkit used:
Scikit Learn

Parameters
--ifile : A labeled dataset
--odir : Output directory for the .model file

"""

import getopt
import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import pickle
import lib


def usage():
    print('python train_rf_acc.py --ifile <input_file> --f <features_file> --odir <output_directory>')
    print()
    print('Example:')
    print('python train_rf_acc.py --ifile datasets/ACC_capture.csv.30.2.features.csv --f models/features_1.txt --odir models')


# Reads the features file for training
def read_features(filename):
    features = []
    with open(filename) as f_feat:
        for line in f_feat:
            line = line.replace('\n', '')
            line = line.replace('\t', '')
            if line != '':
                features.append(line)
    return features

if __name__ == "__main__":
    inputfile = ''
    outputdir = ''
    featuresfile = ''

    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:f:o", ["ifile=", "f=", "odir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-f", "--f"):
            featuresfile = arg
        elif opt in ("-o", "--odir"):
            outputdir = arg

    if inputfile == '':
        print('No input file provided')
        usage()
        sys.exit(2)
    if featuresfile == '':
        print('No features file provided')
        usage()
        sys.exit(2)
    if outputdir == '':
        print('No output dir provided')
        usage()
        sys.exit(2)

    # Get the filename
    fname = ''
    elm = inputfile.split('/')
    fname = elm[-1]

    outputfile = fname + '.rf.model'
    # Confusion Matrix File Name
    cmfile = fname + '.rf.cm.eval.csv'

    print("Random Forest Model")
    print("Using input file: {}".format(inputfile))
    print("Using features file: {}".format(featuresfile))
    print("Model file will be generated in: {}/{}".format(outputdir, outputfile))
    print("Confusion matrix file will be generated in: {}/{}".format(outputdir, cmfile))

    df = pd.read_csv(inputfile)
    selected_features = lib.read_features(featuresfile)
    print("Features:")
    print(selected_features)

    X = df[selected_features]
    y_labels = df['label']
    label_encoder = LabelEncoder()
    label_encoder.fit(y_labels)
    y = label_encoder.transform(y_labels)
    classes = label_encoder.classes_

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.40, random_state=42)

    # Test later with a scaler to the mean (recommended in SVM)
    training_pipeline = Pipeline(
        [
            ('classifier', RandomForestClassifier(criterion='entropy'))
        ]
    )
    # Parameters of the model to be search using grid search
    parameters = {
        'classifier__n_estimators': (5, 10, 20, 50),
        'classifier__max_depth': (10, 50),
        'classifier__min_samples_split': (5, 10, 30),
        'classifier__min_samples_leaf': (5, 10, 30)
    }
    # Use F1 parameter for the grid search
    search = GridSearchCV(training_pipeline, parameters, n_jobs=-1, verbose=1, scoring='f1_weighted')
    search.fit(X_train, y_train)

    # Show results of grid search:
    print('Best score: %0.3f' % search.best_score_)
    print('Best parameters:')
    best = search.best_estimator_.get_params()
    for name in sorted(parameters.keys()):
        print('\t%s: %r'%(name, best[name]))

    ####################################################################################################################

    # Model Evaluation
    print("Class encoding:")
    for idx, classname in enumerate(label_encoder.classes_):
        print("{} : {}".format(str(idx), classname))
    # Perform the prediction on Test Set
    predictions = search.predict(X_test)
    print("Classification Report on Testing Data:")
    print(classification_report(y_test, predictions))
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, predictions)
    cm_data = {'True labels': classes}
    for idx, classname in enumerate(classes):
        cm_data[classname] = cm[:,idx]
    print(cm)
    cm_result = pd.DataFrame(cm_data)
    cm_result.to_csv(outputdir + '/' + cmfile, sep=',', index=False)

    ####################################################################################################################

    # Save the trained model for later use
    model = {
        'X': X,
        'y': y,
        'features': selected_features,
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test,
        'label_encoder': label_encoder,
        'pipeline': training_pipeline,
        'search': search,
        'predictions': predictions
    }
    wfile = open(outputdir + '/' + outputfile, 'wb')
    pickle.dump(model, wfile)
    wfile.close()