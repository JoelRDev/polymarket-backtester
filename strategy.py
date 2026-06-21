class Order:
    def __init__(self, order_id, price, size):
        self.order_id = order_id
        self.price = price
        self.size = size

# Sample strategy

def strategy(time, price, order_id):
    orders = []
    if price < 0.4:
        orders.append(Order(order_id, price, 50))
    return orders