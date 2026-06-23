from strategy import strategy
from models import Position

'''
This file controls order matching and position tracking
'''

def backtester(data_df):
    order_id = 0
    positions = {
        "LONG": Position(1, "LONG"),
        "SHORT": Position(2, "SHORT"),
    }
    capital = initial_capital()
    starting_capital = capital
    total_orders = []
    trades = []

    for entry in data_df.itertuples():
        time = entry.t
        price = entry.p
        orders = strategy(
            time,
            price,
            capital,
            positions["LONG"].remaining_quantity,
            positions["SHORT"].remaining_quantity
        )
        for order in orders:
            if order.direction not in positions:
                continue

            quantity = order.quantity
            if quantity == 0:
                continue

            fill_price = position_price(order.direction, price)
            position = positions[order.direction]

            if quantity > 0:
                cost = fill_price * quantity
                if capital < cost:
                    continue

                position.add(fill_price, quantity, time)
                capital -= cost
                order_id += 1
                trade = {
                    "id": order_id,
                    "time": time,
                    "action": "BUY",
                    "direction": order.direction,
                    "price": fill_price,
                    "quantity": quantity,
                    "remaining_quantity": quantity,
                    "cost": cost,
                    "profit": position.unrealized_pnl(fill_price),
                    "return_pct": position_return_pct(position, fill_price),
                    "status": "OPEN",
                }
            else:
                close_quantity = abs(quantity)
                if close_quantity > position.remaining_quantity:
                    continue

                proceeds = fill_price * close_quantity
                closed_trade = position.close(fill_price, close_quantity, time)
                capital += proceeds
                reduce_open_trade_quantities(trades, order.direction, close_quantity)
                order_id += 1
                trade = {
                    "id": order_id,
                    "time": time,
                    "action": "SELL",
                    "direction": order.direction,
                    "price": fill_price,
                    "quantity": close_quantity,
                    "proceeds": proceeds,
                    "profit": closed_trade["profit"],
                    "return_pct": closed_trade["return_pct"],
                    "status": "CLOSED",
                    "average_entry_price": closed_trade["average_entry_price"],
                }

            total_orders.append((order_id, time, trade["action"], order.direction, trade["quantity"], fill_price))
            trades.append(trade)
    
    last_price = float(data_df.iloc[-1].p)
    marked_trades = mark_open_trades(trades, last_price)
    open_positions_value = (
        positions["LONG"].market_value(position_price("LONG", last_price))
        + positions["SHORT"].market_value(position_price("SHORT", last_price))
    )
    realized_pnl = positions["LONG"].realized_pnl + positions["SHORT"].realized_pnl
    return {
        "realized_pnl": realized_pnl,
        "unrealized_pnl": (
            positions["LONG"].unrealized_pnl(position_price("LONG", last_price))
            + positions["SHORT"].unrealized_pnl(position_price("SHORT", last_price))
        ),
        "final_equity": capital + open_positions_value,
        "total_pnl": capital + open_positions_value - starting_capital,
        "orders": total_orders,
        "trades": marked_trades,
        "ranked_trades": rank_trades_by_profitability(marked_trades),
        "cash": capital,
        "remaining_long_position": positions["LONG"].remaining_quantity,
        "remaining_short_position": positions["SHORT"].remaining_quantity,
        "long_average_entry_price": positions["LONG"].average_entry_price,
        "short_average_entry_price": positions["SHORT"].average_entry_price,
    }


def position_price(direction, yes_price):
    if direction == "LONG":
        return yes_price
    return 1 - yes_price


def position_return_pct(position, current_price):
    invested = position.average_entry_price * position.remaining_quantity
    return position.unrealized_pnl(current_price) / invested if invested else 0


def mark_open_trades(trades, last_price):
    marked_trades = []

    for trade in trades:
        marked_trade = trade.copy()
        if trade["status"] == "OPEN":
            current_price = position_price(trade["direction"], last_price)
            remaining_quantity = trade["remaining_quantity"]
            remaining_cost = trade["price"] * remaining_quantity
            current_value = current_price * remaining_quantity
            profit = current_value - remaining_cost
            marked_trade["current_value"] = current_value
            marked_trade["profit"] = profit
            marked_trade["return_pct"] = profit / remaining_cost if remaining_cost else 0
        marked_trades.append(marked_trade)

    return marked_trades


def reduce_open_trade_quantities(trades, direction, close_quantity):
    remaining_to_close = close_quantity

    for trade in trades:
        if remaining_to_close == 0:
            break
        if trade["status"] != "OPEN" or trade["direction"] != direction:
            continue

        quantity_closed = min(trade["remaining_quantity"], remaining_to_close)
        trade["remaining_quantity"] -= quantity_closed
        remaining_to_close -= quantity_closed

        if trade["remaining_quantity"] == 0:
            trade["status"] = "CLOSED"


def rank_trades_by_profitability(trades):
    rankable_trades = [
        trade for trade in trades
        if trade["action"] == "SELL" or trade.get("remaining_quantity", 0) > 0
    ]
    return sorted(rankable_trades, key=lambda trade: trade["profit"], reverse=True)

def initial_capital():
    while True:
        capital = input("Initial capital: ")
        try:
            capital = round(float(capital), 2)
            return capital
        except ValueError:
            print("Please enter a valid float")
