import ccxt
import ccxt_error
from dotenv import load_dotenv
from collections import deque


class executionPlatform:
    def __init__(self):
        load_dotenv()
        self.mapToExchange = {}
        self.errorLog = []
        self.retryQueue = deque()

    def createExchange(self, exchangeName):
        """createExchange() takes in the name of the exchange you want to use and creates an instance of it in the mapToExchange dictionary. Raises an exception if the exchange doesn't exist in CCXT."""

        if exchangeName not in ccxt.exchanges:
            self.errorLog.append(ccxt_error.no_exchange_error(exchangeName))
        self.mapToExchange[exchangeName] = ccxt.eval(exchangeName)()
        self.mapToExchange[exchangeName].secret = eval(exchangeName)[0]
        self.mapToExchange[exchangeName].apiKey = eval(exchangeName)[1]

    def getBalance(self, exchange: str):
        """getBalance() takes in the name of the exchange that you want to use and returns the current balance of the account."""
        if exchange not in self.mapToExchange:
            self.errorLog.append(ccxt_error.no_exchange_error(exchange))
        else:
            try:
                return self.mapToExchange[exchange].fetchBalance()
            except Exception as e:
                print(e)

    def placeOrder(
        self,
        exchange: str,
        tradeSymbol: str,
        tradeType: str,
        tradeSide: str,
        tradeAmount: int,
        price: float = None,
    ):
        """placeOrder() takes in the exchange name, trading pair symbols, trade type, trade side, trade amount, and price (if limit order) and places an order on the exchange
        Returns an 'Order Structure' that contains all of the information related to that order"""
        # ->return order structure
        if exchange not in self.mapToExchange:
            self.errorLog.append(ccxt_error.no_exchange_error(exchange))
        else:
            try:
                if tradeType == "limit":
                    orderBook = self.mapToExchange[exchange].createOrder(
                        tradeSymbol, tradeType, tradeSide, tradeAmount, price
                    )
                elif tradeType == "market":
                    orderBook = self.mapToExchange[exchange].createOrder(
                        tradeSymbol, tradeType, tradeSide, tradeAmount
                    )

                return orderBook

            except Exception as e:
                print(e)

    def editOrder(
        self,
        exchange: str,
        orderID: str,
        tradeSymbol: str,
        tradeType: str,
        tradeSide: str,
        tradeAmount: int,
        price: float = None,
    ):
        """editOrder() takes in the exchange name, order ID, trading pair symbols, trade type, trade side, trade amount, and price (if limit order). It edits the corresponding order with these parameters. Returns an exception if failed."""
        if exchange not in self.mapToExchange:
            self.errorLog.append(ccxt_error.no_exchange_error(exchange))
        else:
            try:
                if tradeType == "limit":
                    return self.mapToExchange[exchange].editOrder(
                        orderID, tradeSymbol, tradeType, tradeSide, tradeAmount, price
                    )
                elif tradeType == "market":
                    return self.mapToExchange[exchange].editOrder(
                        orderID, tradeSymbol, tradeType, tradeSide, tradeAmount
                    )
            except Exception as e:
                print(e)

   

    def inspectOrder(self, exchange: str, orderID=None):
        """inspectOrder() takes in the exchange name and order ID. It returns all of the order information in the returned 'Order Structure'."""
        if exchange not in self.mapToExchange:
            self.errorLog.append(ccxt_error.no_exchange_error(exchange))
        else:
            try:
                return self.mapToExchange[exchange].fetch_order(orderID)
            except Exception as e:
                print(e)

    

    def cancelOrder(self, exchange: str, orderID, tradingPair: str = None):
        """cancelOrder() takes in the exchange name, orderID, and the trading pair symbols. It cancels the corresponding order. Returns an exception if failed."""
        if exchange == "ALL":
            if tradingPair != None:
                for i in self.mapToExchange:
                    i.cancelAllOrders(tradingPair)
            else:
                for i in self.mapToExchange:
                    i.cancelAllOrders()
        else:
            if exchange not in self.mapToExchange:
                self.errorLog.append(ccxt_error.no_exchange_error(exchange))
            else:
                try:
                    self.mapToExchange[exchange].cancelOrder(orderID)
                    orderStruct = self.inspectOrder(exchange, orderID)
                    if orderStruct["status"] == "cancelled":
                        return f"Order {orderID} successfully cancelled"
                    else:
                        return f"ERROR>>> The order {orderID} is currently {orderStruct['status']}."
                except Exception as e:
                    print(e)

    """calls the given algorithm and then runs all the orders returned from it.

    return type of algorithm: list of dictionaries with the following fields
    [{exchange:str, tradeSymbol:str, tradeType:str, tradeSide:str, tradeAmount:int, price:float},]

    def update(self,algorithm):
      orders = algorithm()
      result = [None for _ in range(len(orders))]
      for i,order in orders:
        result[i] = self.placeOrder(order) #unpack
        #get all the order info and then call self.createOrder()
        #return a list of order structures - each order structure corresponding to that order
      return result
    """
