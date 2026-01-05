
def clean_data(df):
    df = df.copy()
    df.drop_duplicates(inplace=True)
    # Fill missing numeric values with the median of the column
    df['Amount'] = df.groupby('Category')['Amount'].transform(lambda x: x.fillna(x.median()))
    # Convert all numeric columns to absolute values
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].abs()
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include=['object']).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
    # Filter rows where 'Category' is in a predefined list
    valid_categories = ['A', 'B', 'C']
    df = df[df['Category'].isin(valid_categories)]
    #sort rows 
    df = df.sort_values(by=['Category', 'Amount'], ascending=[True, True])
    return df
