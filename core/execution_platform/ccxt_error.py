import time

class no_exchange_error:
    """CCXT error logged when an exchange is not found."""
    def __init__(self, exchange):
        self.exchange = exchange
        self.error = "ERROR>>Exchange Not Created!"
        self.time = time.time()

class no_order_error:
    """CCXT error logged when an order is not found."""
    def __init__(self, orderID):
        self.orderID = orderID
        self.error = "ERROR>>Order Not Found!"
        self.time = time.time()
