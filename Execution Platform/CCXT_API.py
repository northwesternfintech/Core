import ccxt
from dotenv import load_dotenv

class executionPlatform():
  def __init__(self):
    load_dotenv()
    self.mapToExchange = {}

  def createExchange(self, exchangeName):
    if exchangeName not in ccxt.exchanges:
      raise Exception("ERROR>>Exchange Doesn't Exist in CCXT!")
    self.mapToExchange[exchangeName] = ccxt.eval(exchangeName)()
    self.mapToExchange[exchangeName].secret = eval(exchangeName)[0]
    self.mapToExchange[exchangeName].apiKey = eval(exchangeName)[1]

  def getBalance(self, exchange:str):
    if exchange not in self.mapToExchange:
      raise Exception("ERROR>>Exchange Not Created!")
    else:
      try:
        return self.mapToExchange[exchange].fetchBalance()

      except Exception as e: 
        print(e)

  def placeOrder(self, exchange:str, tradeSymbol:str, tradeType:str, tradeSide:str, tradeAmount:int, price:float=None): #->return order ID
    if exchange not in self.mapToExchange:
      raise Exception("ERROR>>Exchange Not Created!")
    else:
      try:
        if tradeType == 'limit':
          orderBook = self.mapToExchange[exchange].createOrder(tradeSymbol, tradeType, tradeSide, tradeAmount, price)
        elif tradeType == 'market':
          orderBook = self.mapToExchange[exchange].createOrder(tradeSymbol, tradeType, tradeSide, tradeAmount)

        return orderBook['id']

      except Exception as e: 
        print(e)

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

  def cancelOrder(self, exchange:str, tradingPair:str=None, orderID:list(str)=None):
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
          if tradingPair != None:
            self.mapToExchange[exchange].cancelOrder(orderID, tradingPair)
          else:
            self.mapToExchange[exchange].cancelOrder(orderID)
        except Exception as e: 
          print(e)