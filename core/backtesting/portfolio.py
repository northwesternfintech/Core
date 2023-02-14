from asset_trading_lib import asset

class portfolio:
    
    def __init__(self, starting_balance=10000, transaction_cost=0):

        self.balance = starting_balance 
        self.transaction_cost = transaction_cost  # decimal percentage
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
            return self.balance >= stock_price * shares * (1 + self.transaction_cost)
        else:  # sell
            try:
                return self.holdings[stock_name].get_amount() >= abs(shares)
            except:
                return False # no such stock in holdings and cannot sell

    def place_order(self, stock_name, stock_price, shares):
        """
        this function handles both buys and sells (shares > 0 for buy and < 0 for sell)
        first validate the order, if is valid, place the order and return True
        otherwise return false

        stock_price: float
        shares: int
        stock_name: string
        """
        if self.validate_order(stock_name, stock_price, shares):

            if shares > 0:  # buy
                self.transactions.append(["buy", stock_name, stock_price, shares])
                self.balance -= stock_price * shares * (1 + self.transaction_cost)

                if not stock_name in self.get_holdings():
                    self.holdings[stock_name] = asset(stock_name)

                self.holdings[stock_name].update_asset(amount=shares, price=stock_price)

                return True
            else: # sell
                shares = -shares
                net = shares * stock_price
                self.transactions.append(["sell", stock_name, stock_price, shares])
                self.balance += stock_price * shares * (1 - self.transaction_cost)

                if not stock_name in self.get_holdings():
                    self.holdings[stock_name] = asset(stock_name)

                self.holdings[stock_name].update_asset(amount=shares, price=0)

                return True


        return False

p = portfolio(starting_balance= 10000)
p.place_order(stock_name = "test", stock_price=1050, shares = 1)
p.place_order(stock_name = "test", stock_price=1040, shares = -1)
print(p.get_transactions())

    