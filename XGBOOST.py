print("Démarrage")


import pandas as pd
from sklearn.preprocessing import LabelEncoder


def preprocess_dataframe(df):
    def replace_nulls_with_mean(df):
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                mean_value = df[column].mean()
                df[column].fillna(mean_value, inplace=True)
        return df

    def encode_non_numeric_columns(df):
        label_encoders = {}
        for column in df.columns:
            if not pd.api.types.is_numeric_dtype(df[column]):
                le = LabelEncoder()
                df[column] = le.fit_transform(df[column])
                label_encoders[column] = le
        return df, label_encoders

    def remove_outliers(df):
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        return df

    df = replace_nulls_with_mean(df)
    df, _ = encode_non_numeric_columns(df)
    df = remove_outliers(df)
    return df

def prepare_XY(name, df):
    y = df[name]
    df = df.drop(df.columns[0], axis=1)
    if name in df.columns:
        df = df.drop(name, axis=1)
    else:
        print("ERROR")
    return df, y


def prepare_XY2(name,df,query):
    y = df[name]
    X = df[query]
    return X, y












