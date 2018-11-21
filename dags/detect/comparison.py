import pandas as pd
import numpy as np


def clean(event_data):
    # read list of dfs from adam into one df
    master = None
    for source in event_data.keys():
        # add source column
        event_data[source]['Source'] = source
        if master is None:
            master = event_data[source]
        else:
            master = pd.concat([master, event_data[source]], axis=0)

    # drop rows where money line is empty
    df = master[master['Money Line'] != ()]
    df.reset_index(drop=True, inplace=True)

    # split Money Line tuple
    df['ML_A'] = df['Money Line'].apply(lambda t: max(t))
    df['ML_B'] = df['Money Line'].apply(lambda t: min(t))
    df['Line_1'] = df['Money Line'].apply(lambda t: t[0])
    df['Line_2'] = df['Money Line'].apply(lambda t: t[1])

    # split Teams string
    df['Team_1'], df['Team_2'] = df['Teams'].str.split(', ', 1).str

    # assign Teams to lines / title of underdog or favorite
    df['Underdog_A'] = np.where(df['ML_A'] == df['Line_1'],
                                df['Team_1'],
                                df['Team_2'])
    df['Favorite_B'] = np.where(df['ML_B'] == df['Line_2'],
                                df['Team_2'],
                                df['Team_1'])

    # remove extraneous columns
    df.drop(['Line_1', 'Line_2', 'Team_1', 'Team_2', 'Spread',
             'Total Points', 'Money Line', 'Teams'],
            axis=1,
            inplace=True)

    return df




def find_arbs(df, bet_size):
    df_gimmes = None

    # find if it is possible to bet on both sides as underdogs => a "gimme"
    gimmes = set(df['Underdog_A'].tolist()). \
        intersection(df['Favorite_B'].tolist())

    if len(gimmes) != 0:
        # assign value to df_gimmes, indicating this chunk has been executed
        # only get rows where team name is involved in a gimme
        df_gimmes = df[((df['Underdog_A'].isin(gimmes)) |
                       (df['Favorite_B'].isin(gimmes)))]

        # get the underdog lines from the 2 rows consisting of the best arb
        df_gimmes['best_ML_A'] = df_gimmes.groupby(by=['Underdog_A'])['ML_A'].\
            transform('max')

        # filter out any rows where it is not part of the best arb
        df_gimmes = df_gimmes[df_gimmes['ML_A'] == df_gimmes['best_ML_A']]

        # remove duplicates
        df_gimmes.drop_duplicates(['ML_A', 'Underdog_A', 'Favorite_B'],
                                  inplace=True)

        # combine the 2 rows representing each arb into 1 row,
        # drop the then unnecessary columns
        df_gimmes = combine_arb_rows(df_gimmes)

        # after above, there are 2 rows with same info.
        # Drop duplicate rows resulting from the merge
        df_gimmes = drop_duplicate_arb_rows(df_gimmes)

        # calculate ideal bet values and yielded profit
        df_gimmes = add_profit(df_gimmes, bet_size)

        # format for export
        df_gimmes.rename({'Underdog_A': 'Team_A',
                          'Underdog_B': 'Team_B',
                          'Date_x': 'Date'},
                         axis=1,
                         inplace=True)

        df_gimmes = df_gimmes[['Date', 'Team_A', 'Team_B', 'best_ML_A',
                               'best_ML_B', 'Source_A', 'Source_B', 'Bet_on_A',
                               'Bet_on_B', 'Profit_A', 'Profit_B']]

    # add best money line values for each team
    df['best_ML_A'] = df.groupby(by=['Underdog_A'])['ML_A'].transform('max')
    df['best_ML_B'] = df.groupby(by=['Favorite_B'])['ML_B'].transform('max')

    # filter for only cases where A > abs(B), since A>abs(B) <=> arb
    df = df[(df['best_ML_A'] > abs(df['best_ML_B']))]

    if df.shape[0] == 0:
        # if here, then no arb opportunities exist of form A>abs(B)
        if df_gimmes is not None:
            # if here, then arb opportunities did exist with 2 underdogs,
            # so return those
            return df_gimmes
        else:
            # if here, then no arb opportunities of either kind exist
            print('No arb available')
            return

    else:
        # only keep quoted lines that could be used in half of an arb
        df = df[((df['ML_A'] == df['best_ML_A']) |
                (df['ML_B'] == df['best_ML_B']))]

        # determine the sources of the two quoted lines to be used in arb
        df['source_1'] = df.groupby(['Underdog_A', 'Favorite_B'])['Source']\
            .transform('max')
        df['source_2'] = df.groupby(['Underdog_A', 'Favorite_B'])['Source']\
            .transform('min')

        # assign to underdog or favorite
        df = underdog_or_favorite(df)

        # after above, are 2 rows with same info. drop duplicate rows
        df.drop_duplicates(['Underdog_A', 'Favorite_B'], inplace=True)

        # determine ideal bet size and profit
        df = ideal_bet_size(df)

        # return with gimmes if they exist, as is if no gimmes
        if df_gimmes is not None:
            return pd.concat([df, df_gimmes], axis=0)
        else:
            return df



def underdog_or_favorite(df):
    df['Source_A'] = df['Source']
    df['Source_B'] = df['Source']
    df['Source_A'] = np.where((df['ML_B'] == df['best_ML_B']),
                              np.where(df['source_1'] == df['Source'],
                                       df['source_2'],
                                       df['source_1']),
                              df['Source_A'])
    df['Source_B'] = np.where((df['ML_A'] == df['best_ML_A']),
                              np.where(df['source_1'] == df['Source'],
                                       df['source_2'],
                                       df['source_1']),
                              df['Source_B'])
    return df.drop(['Source', 'source_1', 'source_2', 'ML_A', 'ML_B'],
            axis=1)

def ideal_bet_size(df):
    df['Bet_on_A'] = bet_size * (100.0 / abs(df['best_ML_B']) + 1) / \
        (df['best_ML_A'] / 100.0 + 100.0 / abs(df['best_ML_B']) + 2)\

    df['Bet_on_B'] = bet_size - df['Bet_on_A']

    df['Profit_A'] = df['Bet_on_A'] * df['best_ML_A'] / \
        100.0 + df['Bet_on_A'] - bet_size

    df['Profit_B'] = df['Bet_on_B'] * 100.0 / abs(df['best_ML_B']) + \
        df['Bet_on_B'] - bet_size

    return df.rename({'Underdog_A': 'Team_A', 'Favorite_B': 'Team_B'},
              axis=1)


def drop_duplicate_arb_rows(df_gimmes):

    df_gimmes['Teams'] = df_gimmes.apply(lambda row: str(
                                                sorted([row.Underdog_A,
                                                        row.Underdog_B])),
                                         axis=1)

    df_gimmes.drop_duplicates('Teams', inplace=True)

    return df_gimmes.drop('Teams', axis=1)


def combine_arb_rows(df_gimmes):
    """
    combines the 2 rows representing a single arb into one row
    :parameters
        df_gimmes(pandas DataFrame) -> a dataframe containing find_arbs
    returns(pandas DataFrame) -> A data frame with detected arbs combined into
    one row

    """

    df_gimmes = df_gimmes.merge(df_gimmes, how='inner',
                                left_on='Underdog_A',
                                right_on='Favorite_B')

    df_gimmes.drop(['Favorite_B_x', 'Favorite_B_y', 'ML_B_x',
                    'ML_B_y', 'Date_y', 'ML_A_x', 'ML_A_y'],
                   axis=1,
                   inplace=True)

    return df_gimmes.rename({'Source_x': 'Source_A',
                             'Source_y': 'Source_B',
                             'best_ML_A_x': 'best_ML_A',
                             'best_ML_A_y': 'best_ML_B',
                             'Underdog_A_x': 'Underdog_A',
                             'Underdog_A_y': 'Underdog_B'},
                            axis=1)


def add_profit(df_gimmes, bet_size):
    """
    adds the calculated profit into the gimmies dataframe
    :parameters
        df_gimmes(pandas DataFrame) -> A dataframe containing possible arbs
        bet_size(int) -> an int denoting the size of the bet being made on the
        arb opportunities

    return(df) -> a modified data frame with the calculated profit added in.
    """
    df_gimmes['Bet_on_A'] = bet_size * \
        (df_gimmes['best_ML_B']/100 + 1) / \
        (df_gimmes['best_ML_A']/100.0 +
            df_gimmes['best_ML_B']/100.0 + 2)

    df_gimmes['Bet_on_B'] = bet_size - df_gimmes['Bet_on_A']

    df_gimmes['Profit_A'] = df_gimmes['Bet_on_A'] * \
        df_gimmes['best_ML_A'] / 100.0 + \
        df_gimmes['Bet_on_A'] - bet_size

    df_gimmes['Profit_B'] = df_gimmes['Bet_on_B'] * \
        df_gimmes['best_ML_B'] / 100.0 + \
        df_gimmes['Bet_on_B'] - bet_size

    return df_gimmes
