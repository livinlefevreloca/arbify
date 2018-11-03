def make_ou_numerical(ou_strings):
    """
    format over under strings
    ***format***
        string: 'O ##.# ##' -----> tuple(float: #.#, int: #)
        string: 'U ##.# ##' -----> tuple(float: -#.#, int: #)
        unders denoted by negative handicap
    :params
        ou_strings(string) -> strings for the over unders of a game
    return(tuple(float,int)) -> a tuple of the handicap and price of the ou
    """
    ous = []
    for string in ou_strings:
        if len(string) < 3:
            continue
        components = string.split(" ")
        components = clean_components(components)
        sign = ""
        if components[0] in "Un":
            sign = '-'
        handicap = float(sign + components[1])
        price = int(components[2])
        ous.append((handicap, price))
    return tuple(ous)

def make_spread_numerical(spread_strings):
    """
    format spread
    ***format***
        string: '+##.# ##' -----> tuple(float: #.#, int: #)
        string: '-##.# ##' -----> tuple(float: -#.#, int: #)
        negative spread denoted by negative handicap
    :params
        spread_strings(string) -> strings for the spread of a game
    return(tuple(float,int)) -> a tuple of the handicap and price of the spread
    """
    spreads = []
    for string in spread_strings:
        if len(string) < 3:
            continue
        components = string.split(" ")
        if len(components) < 2:
            components.insert(0, '0')
        components = clean_components(components)
        spreads.append((float(components[0]), int(components[1])))
    return tuple(spreads)

def make_moneyline_numerical(mline_strings):
    """
    format over under strings
    ***format***
        string: '##' -----> int: ##
        string: '-##' -----> int: -##
    :params
        mline_strings(string) -> strings for the money lines of a game
    return(int) -> an integer of the moneyline price
    """
    moneylines = []
    for string in mline_strings:
        if len(string) < 3:
            continue
        string = clean_components([string,])[0]
        moneylines.append(int(string))
    return tuple(moneylines)

def clean_names(team_strings, truth):
    teams = replace_with_ground_truth(team_strings, truth=truth)
    return ", ".join(teams)

def clean_components(items):
    """
    remove certain non machine readable denotations of a line
    :params
        items(list) -> a list of lines(genric)
    return(list) -> lines with replacement made
    """
    new_items = []
    for item in items:
        new_item = item
        if item.lower() == "even":
            new_item = "100"
        elif item.lower() == "pk":
            new_item = "100"
        elif item == "":
            new_item = "100"
        new_item = translate_fraction(new_item)
        new_items.append(new_item)
    return new_items

def replace_with_ground_truth(pair, truth):
    """
    normalize names of a game to the ground_truth names
    :params
        pair(tuple) -> tuple containing two team names
        truth(dict) -> the ground truth mapping to translate names
    return(tuple) -> a tuple of corrected names
    """
    pair = list(pair)
    if pair[0] in truth.keys():
        pair[1] = truth[pair[0]]
        pair = tuple(pair)
        return pair
    elif pair[1] in truth.keys():
        pair[0] = truth[pair[1]]
        pair = tuple(pair)
        return pair
    else:
        return pair

def translate_fraction(string):
    """
    translate the unicode ½ charcter to the string '.5'
    :params
        string(str) -> a string possibly containing the ½ character
    return(string) -> a srting with  ½ replaced by '.5'
    """
    frac_bytes = b'\xc2\xbd'
    dec_bytes = b'.5'
    if frac_bytes not in string.encode():
        return string
    return string.encode().replace(frac_bytes, dec_bytes).decode()
