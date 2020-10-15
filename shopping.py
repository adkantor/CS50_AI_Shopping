# import csv
import sys
import json

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # NOTE:
    # It would be easier to train model directly with pandas Dataframe/Series, but because of
    # the project specification I will convert X and y to list of lists / list.

    # read csv
    df = pd.read_csv(filename)

    # transform categorical / boolean columns
    df_transformed = transform_df(df)

    # extract X, y
    X = df_transformed.iloc[:, : -1]
    y = df_transformed.iloc[:, -1]

    # convert to list of lists / list
    evidence = dataframe_to_list_of_lists(X)
    labels = dataframe_to_list_of_lists(y)

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1) 
    model.fit(evidence, labels) 
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    cm = confusion_matrix(y_true=labels, y_pred=predictions)
    
    TN = cm[0,0]
    FN = cm[1,0]
    FP = cm[0,1]
    TP = cm[1,1]
    
    sensitivity = TP / (TP + FN)
    specificty = TN / (TN + FP)

    return (sensitivity, specificty)


def transform_df(df):
    """
    Transforms the specified columns of the dataframe to the specified form.
    """
    mapping = {
        'Month': {
            'Jan': 0, 'Feb': 1, 'Mar': 2,
            'Apr': 3, 'May': 4, 'June': 5,
            'Jul': 6, 'Aug': 7, 'Sep': 8,
            'Oct': 9, 'Nov': 10, 'Dec': 11
        },
        'VisitorType': {
            'Returning_Visitor': 1,
            'New_Visitor': 0,
            'Other': 0
        },
        'Weekend': {
            True: 1,
            False: 0
        },
        'Revenue': {
            True: 1,
            False: 0
        }
    }
    df = df.replace(mapping)
    return df


def dataframe_to_list_of_lists(df):
    """
    Converts DataFrame to list of lists, while preserving dtypes.
    """
    # N.B.: df.as_array(), df.to_numpy, df.values() does not preserve dtype, therefore
    # DataFrame is first converted to json then parsed again.
    # inspired by: https://stackoverflow.com/questions/28006793/pandas-dataframe-to-list-of-lists
    j = df.to_json(orient='split')
    return json.loads(j)['data']


if __name__ == "__main__":
    main()
