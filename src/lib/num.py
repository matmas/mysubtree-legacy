def num(str):
    try:
        return int(str)
    except ValueError:
        return 0