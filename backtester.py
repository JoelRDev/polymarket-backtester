from strategy import strategy

def backtester(data_df):
    order_id = 1
    position = 0
    pnl = 0
    for entry in data_df.itertuples():
        time = entry.t
        price = entry.p
        orders = strategy(time, price, order_id)
        for order in orders:
            position += order.size
            pnl -= (order.price * order.size)
            order_id += 1
    last_price = data_df.iloc[-1].p
    pnl += position * last_price
    return pnl