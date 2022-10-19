class portfolio():
    
    def __init__(self, starting_balance=None, transaction_cost=None):
        
        self.balance = starting_balance or 10000
        self.transaction_cost = transaction_cost or 0
        self.transactions = []
        self.holdings = [] # list of lists
                           # each sublist contains two elements: [stock_name, amount_holding]

    def get_balance(self): return self.balance
    
    def get_holdings(self): return self.holdings
    
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
            else: 
                return False
        else: # sell
            for stock in self.holdings:
                if stock[0] == stock_name: 
                    return stock[1] >= abs(shares)
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
                self.transactions.append(['buy',stock_name, stock_price, shares])
                self.balance -= stock_price*shares*(1+self.transaction_cost)
                for stock in self.holdings:
                    if stock[0] == stock_name: 
                        stock[1] += shares; return True 
                self.holdings.append([stock_name, shares]); return True
            elif shares < 0:
                self.transactions.append(['sell',stock_name, stock_price, shares])
                self.balance += stock_price*shares*(1-self.transaction_cost)
                for stock in self.holdings:
                    if stock[0] == stock_name: 
                        stock[1] -= shares; return True 
        else: return False 
            
            
                    