"""
Some useful functions for the classifiers

"""
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix


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


# Prints report and save Confussion Matrix
def generates_report_and_save_cm(model, Y, Y_hat, file):
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
