from models import Order

# Sample strategy
def strategy(time, price, capital, long_position, short_position):
    orders = []
    if price < 0.4:
        orders.append(Order(price, 50, "LONG"))
    return orders