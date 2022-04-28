import numpy as np
import json
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import os

dataset_file = os.path.dirname(__file__) + "/output/collections2.txt"

def mean_absolute_percentage_error(y_true, y_pred):
    return 100 * (np.abs((y_true - y_pred) / y_true)).mean()

def count_errors(X, y, model):
    score = accuracy_score(y, model.predict(X))
    print(f"Accuracy_score of {type(model)}: {score}")

def make_model(X, y, model):
    model.fit(X, y)
    return model

def get_numpy(df, scale_par=None, print_size=0):
    X = np.array(train[['NOW_PRICE', 'SOLD_ONCE', 'WEEK_DEALS',
        'COLLECTION_SOLD_ONCE', 'COLLECTION_WEEK_DEALS', 'COLLECTION_OWNERS']])
    y = np.array(train['target'])
    if (scale_par is None):
        scale_par = X.max(axis=0)
        print(scale_par)
    X /= scale_par
    if (print_size != 0):
        print(f"Len: {X.shape[0]}, Data:\n{X[:print_size]}\n\n")
        print(f"Len: {len(y)}, Data:\n{y[:print_size]}")
    return X, y, scale_par

def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    df = df.reset_index()
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)

if __name__ == '__main__':
    # Preparing data
    df = pd.read_json(dataset_file)
    df.drop(columns=['col_id', 'id'], inplace=True)
    df = clean_dataset(df)

    # Setting target     
    df['target'] = 0
    df['target'][df[df['FUTURE_PRICE'] >= df['NOW_PRICE']].index] = 1
    df['target'][df[df['FUTURE_PRICE'] < df['NOW_PRICE']].index] = -1
    train, test = train_test_split(df, test_size=0.5) 

    # Learning
    X_train, y_train, scale_par = get_numpy(train) 
    lda = make_model(X_train, y_train, LinearDiscriminantAnalysis())
    qda = make_model(X_train, y_train, QuadraticDiscriminantAnalysis())
    mnb = make_model(X_train, y_train, MultinomialNB())
    log_regr = make_model(X_train, y_train, LogisticRegression()) 
    
    # Results
    X_test, y_test, scale_par = get_numpy(test, scale_par)
    count_errors(X_test, y_test, lda)
    count_errors(X_test, y_test, qda)
    count_errors(X_test, y_test, mnb)
    count_errors(X_test, y_test, log_regr)
