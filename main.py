from data_setup import get_data
from backtester import backtester

def main():
    data = get_data()
    pnl = backtester(data)
    print(pnl)

if __name__ == "__main__":
    main()