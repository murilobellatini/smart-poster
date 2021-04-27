from hashlib import md5


def select_closest(list_: list, target_value: float, key: str):
    """
    Assumes `list_` as a list of dicts and not sorted.
    Returns closest value to `target_value` from `key`.
    """
    return min(list_, key=lambda x: abs(x[key]-target_value))


def get_hashed_str(txt: str, method: str = "MD5"):

    if method == "MD5":
        hashed = md5(txt.encode())
    else:
        raise NotImplementedError

    return hashed.hexdigest()


def capitalize_first_letter(txt: str) -> str:
    if len(txt) > 0:
        txt = f'{txt[0].upper()}{txt[1:]}'
    return txt
