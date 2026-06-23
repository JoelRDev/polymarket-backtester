class Order:
    def __init__(self, price, quantity, direction):
        self.price = price
        self.quantity = quantity # Negative size indicates a sell
        self.direction = direction
        self.cost = self.price * self.quantity

class Position:
    def __init__(self, position_id, direction, entry_price=0, entry_quantity=0, remaining_quantity=0, entry_time=None):
        self.position_id = position_id
        self.direction = direction
        self.entry_price = 0
        self.remaining_quantity = 0
        self.entry_time = None
        self.realized_pnl = 0
        self.closed_trades = []

        opening_quantity = remaining_quantity or entry_quantity
        if opening_quantity:
            self.add(entry_price, opening_quantity, entry_time)

    @property
    def entry_quantity(self):
        return self.remaining_quantity

    @property
    def average_entry_price(self):
        return self.entry_price

    def add(self, price, quantity, time):
        if quantity <= 0:
            raise ValueError("Position add quantity must be positive")

        total_cost = self.entry_price * self.remaining_quantity + price * quantity
        self.remaining_quantity += quantity
        self.entry_price = total_cost / self.remaining_quantity

        if self.entry_time is None:
            self.entry_time = time

    def close(self, price, quantity, time):
        if quantity <= 0:
            raise ValueError("Position close quantity must be positive")
        if quantity > self.remaining_quantity:
            raise ValueError("Cannot close more than the remaining position")

        profit = (price - self.entry_price) * quantity
        self.remaining_quantity -= quantity
        self.realized_pnl += profit

        closed_trade = {
            "direction": self.direction,
            "exit_time": time,
            "exit_price": price,
            "quantity": quantity,
            "average_entry_price": self.entry_price,
            "profit": profit,
            "return_pct": profit / (self.entry_price * quantity) if self.entry_price else 0,
        }
        self.closed_trades.append(closed_trade)

        if self.remaining_quantity == 0:
            self.entry_price = 0
            self.entry_time = None

        return closed_trade

    def market_value(self, price):
        return self.remaining_quantity * price

    def unrealized_pnl(self, price):
        return (price - self.entry_price) * self.remaining_quantity
