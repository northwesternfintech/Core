from asset_trading_lib import asset


class portfolio:
    def __init__(self, starting_balance=None, transaction_cost=None):

        self.balance = starting_balance or 10000
        self.transaction_cost = transaction_cost or 0  # decimal percentage
        self.transactions = (
            []
        )  # Consider changing this to a list of transaction objects
        self.holdings = {}  # Dictionary mapping name to asset object

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions

    def get_holdings(self):
        return self.holdings

    def validate_order(self, stock_name, stock_price, shares):
        """
        this function validates if orders can be placed, it handles
        both buys and sells (shares > 0 for buy and < 0 for sell)
        returns a boolean

        stock_price: float
        shares: int
        """
        if shares > 0:  # buy
            if self.balance >= stock_price * shares * (1 + self.transaction_cost):
                return True

        else:  # sell
            if self.holdings.has_key(stock_name):
                return self.holdings[stock_name].get_amount() >= abs(shares)

        # If both conditions fail, then order is invalid
        return False

    def place_order(self, stock_name, stock_price, shares):
        """
        this function handles both buys and sells (shares > 0 for buy and < 0 for sell)
        first validate the order, if is valid, place the order and return True
        otherwise return false

        stock_price: float
        shares: int
        stock_name: string
        """
        if self.validate_order(stock_price, shares):
            if shares > 0:  # buy
                self.transactions.append(["buy", stock_name, stock_price, shares, 0])
                self.balance -= stock_price * shares * (1 + self.transaction_cost)

                if not self.get_holdings().has_key(stock_name):
                    self.holdings[stock_name] = asset(stock_name)

                self.holdings[stock_name].update_asset(amount=shares, price=stock_price)

                return True

            elif shares < 0:
                net = shares * (
                    self.holdings[stock_name].get_average_price() - stock_price
                )
                self.transactions.append(["sell", stock_name, stock_price, shares, net])
                self.balance += stock_price * shares * (1 - self.transaction_cost)

                if not self.get_holdings().has_key(stock_name):
                    self.holdings[stock_name] = asset(stock_name)

                self.holdings[stock_name].update_asset(amount=shares, price=0)

                return True

        return False
