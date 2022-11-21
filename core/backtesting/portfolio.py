import attr
from .asset import Asset
from typing import List, Dict


@attr.s()
class Portfolio():
    """Portfolio object for strategy

    Parameters
    ----------
    balance : float, optional
        Starting balance of portfolio, by default 10000
    transaction_cost : float, optional
        Cost of transaction, by default 0
    """
    balance: float = attr.ib(default=10000)
    transaction_cost: float = attr.ib(default=0)  # decimal percentage
    transactions: List = attr.ib(init=False, factory=list)  # Consider changing this to a list of transaction objects
    holdings: Dict = attr.ib(init=False, factory=dict)  # Dictionary mapping name to asset object
    
    def validate_order(self, stock_name, stock_price, shares):
        '''
        this function validates if orders can be placed, it handles
        both buys and sells (shares > 0 for buy and < 0 for sell)
        returns a boolean
        
        stock_price: float
        shares: int
        '''
        if shares > 0: # buy
            if self.balance >= stock_price*shares*(1+self.transaction_cost):
                return True

        else: # sell
            if (self.holdings.has_key(stock_name)):
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
            if shares > 0:
                self.transactions.append(['buy',stock_name, stock_price, shares, 0])
                self.balance -= stock_price*shares*(1+self.transaction_cost)

                if (not self.holdings.has_key(stock_name)):
                    self.holdings[stock_name] = Asset(stock_name)

                self.holdings[stock_name].update_asset(amount=shares, price=stock_price)

                return True

            elif shares < 0:
                net = shares * (self.holdings[stock_name].get_average_price() - stock_price)
                self.transactions.append(['sell',stock_name, stock_price, shares, net])
                self.balance += stock_price*shares*(1-self.transaction_cost)
                
                if stock_name not in self.holdings:
                    self.holdings[stock_name] = Asset(stock_name)

                self.holdings[stock_name].update_asset(amount=shares, price=0)

                return True
                
        return False 
            
            
                    