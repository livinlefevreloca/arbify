from clean.columns import *
from functools import partial

def clean_frame_ncaaf(df, truth):
    """
    clean a dataframe. format columns correctly and normalize team names
    :params
        df(pandas DataFrame) -> a DataFrame from one of the scrapers
        truth(dict) -> the ground truth dictionary for normalizing names
    return(pandas DataFrame) -> the cleaned and normalized data frame
    """
    partial_clean_names = partial(clean_names, truth=truth)
    df["Money Line"] = df["Money Line"].apply(make_moneyline_numerical)
    df["Spread"] = df["Spread"].apply(make_spread_numerical)
    df["Total Points"] = df["Total Points"].apply(make_ou_numerical)
    df["Teams"] = df["Teams"].apply(partial_clean_names)
    return df
