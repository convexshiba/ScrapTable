def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
