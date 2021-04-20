def select_closest(list_:list, target_value:float, key:str):
    """
    Assumes `list_` as a list of dicts and not sorted.
    Returns closest value to `target_value` from `key`.
    """
    return min(list_, key=lambda x:abs(x[key]-target_value))