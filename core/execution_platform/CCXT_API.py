import ccxt
from dotenv import load_dotenv


class executionPlatform():
  def __init__(self):
    load_dotenv()
    self.mapToExchange = {}


  '''createExchange() takes in the name of the exchange you want to use and creates an instance of it in the mapToExchange dictionary. Raises an exception if the exchange doesn't exist in CCXT.'''
  def createExchange(self, exchangeName):
    if exchangeName not in ccxt.exchanges:
      raise Exception("ERROR>>Exchange Doesn't Exist in CCXT!")
    self.mapToExchange[exchangeName] = ccxt.eval(exchangeName)()
    self.mapToExchange[exchangeName].secret = eval(exchangeName)[0]
    self.mapToExchange[exchangeName].apiKey = eval(exchangeName)[1]

  '''getBalance() takes in the name of the exchange that you want to use and returns the current balance of the account.'''
  def getBalance(self, exchange:str):
    if exchange not in self.mapToExchange:
      raise Exception("ERROR>>Exchange Not Created!")
    else:
      try:
        return self.mapToExchange[exchange].fetchBalance()
      except Exception as e: 
        print(e)

  '''placeOrder() takes in the exchange name, trading pair symbols, trade type, trade side, trade amount, and price (if limit order) and places an order on the exchange'''
  '''Returns an 'Order Structure' that contains all of the information related to that order'''
  def placeOrder(self, exchange:str, tradeSymbol:str, tradeType:str, tradeSide:str, tradeAmount:int, price:float=None): #->return order structure
    if exchange not in self.mapToExchange:
      raise Exception("ERROR>>Exchange Not Created!")
    else:
      try:
        if tradeType == 'limit':
          orderBook = self.mapToExchange[exchange].createOrder(tradeSymbol, tradeType, tradeSide, tradeAmount, price)
        elif tradeType == 'market':
          orderBook = self.mapToExchange[exchange].createOrder(tradeSymbol, tradeType, tradeSide, tradeAmount)

        return orderBook

      except Exception as e: 
        print(e)

  '''editOrder() takes in the exchange name, order ID, trading pair symbols, trade type, trade side, trade amount, and price (if limit order). It edits the corresponding order with these parameters. Returns an exception if failed.'''
  def editOrder(self, exchange:str, orderID:str, tradeSymbol:str, tradeType:str, tradeSide:str, tradeAmount:int, price:float=None):
    if exchange not in self.mapToExchange:
      raise Exception("ERROR>>Exchange Not Created!")
    else:
      try:
        if tradeType == 'limit':
          return self.mapToExchange[exchange].editOrder(orderID, tradeSymbol, tradeType, tradeSide, tradeAmount, price)
        elif tradeType == 'market':
          return self.mapToExchange[exchange].editOrder(orderID, tradeSymbol, tradeType, tradeSide, tradeAmount)
      except Exception as e: 
        print(e)

  '''inspectOrder() takes in the exchange name and order ID. It returns all of the order information in the returned 'Order Structure'.'''
  def inspectOrder(self, exchange:str, orderID=None):
    if exchange not in self.mapToExchange:
      raise Exception("ERROR>>Exchange Not Created!")
    else:
      try:
        return self.mapToExchange[exchange].fetch_order(orderID)
      except Exception as e: 
        print(e)

  '''cancelOrder() takes in the exchange name, orderID, and the trading pair symbols. It cancels the corresponding order. Returns an exception if failed.'''
  def cancelOrder(self, exchange:str, orderID, tradingPair:str=None):
    if exchange == 'ALL':
      if tradingPair != None:
        for i in self.mapToExchange:
          i.cancelAllOrders(tradingPair)
      else:
        for i in self.mapToExchange:
          i.cancelAllOrders()
    else:
      if exchange not in self.mapToExchange:
        raise Exception("ERROR>>Exchange Not Created!")
      else:
        try:
            self.mapToExchange[exchange].cancelOrder(orderID)
        except Exception as e: 
          print(e)

  '''calls the given algorithm and then runs all the orders returned from it.
  def update(self,algorithm):
    orders = algorithm()
    result = [None for _ in range(len(orders))]
    for i,order in orders:
      result[i] = self.placeOrder(order) #unpack
      #get all the order info and then call self.createOrder()
      #return a list of order structures - each order structure corresponding to that order
    return result
'''



