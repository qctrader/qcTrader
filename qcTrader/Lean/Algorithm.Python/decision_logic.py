import sys

def make_decision(short_ma, long_ma, invested):
    if short_ma > long_ma and not invested:
        return 'buy'
    elif short_ma < long_ma and invested:
        return 'sell'
    return 'hold'

if __name__ == "__main__":
    short_ma = float(sys.argv[1])
    long_ma = float(sys.argv[2])
    invested = sys.argv[3].lower() == 'true'

    decision = make_decision(short_ma, long_ma, invested)
    print(decision)
