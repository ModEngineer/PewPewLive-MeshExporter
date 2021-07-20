def cleanRound(number, ndigits):
    out = round(number, ndigits=ndigits)
    if out == int(out):
        return int(out)
    return out


def clamp(number, minimum, maximum):
    return max(minimum, min(maximum, number))
