
def clean_data(df):
    df = df.copy()
    df.drop_duplicates(inplace=True)
    # Fill missing numeric values with the median of the column
    df['Amount'] = df.groupby('Category')['Amount'].transform(lambda x: x.fillna(x.median()))
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include=['object']).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
    return df
