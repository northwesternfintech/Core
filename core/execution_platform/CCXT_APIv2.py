import ccxt
from log_class import LoggingClass
from dotenv import load_dotenv
from collections import deque
from datetime import datetime, timedelta
from threading import Thread


'''
Return Codes:
1 - Error, will retry (Network Error for CCXT)
2 - Error, will not retry (Wrong exchange name, Wrong params, etc.)
'''

class executionPlatform:
    '''
        Constructor Notes:
        ---------
        Inputs  : orderQueue - a collections.deque() for orders; logAddress - the address of the log file (optional, will default to LOG_DIR_PATH in .env if not provided)
        Returns : None
        Errors  : Raise Exception if file cannot be created at the log address    
    '''
    
    def __init__(self, orderQueue, logAddress = None):
        
        self.orderQueue = orderQueue
        
        load_dotenv()
        self.log = LoggingClass(logAddress) if logAddress else LoggingClass(LOG_DIR_PATH)
        if self.log.status == 1:
            raise Exception("Log file could not be created")

        self.retryQueue = deque()

        self.idDict = {}

        self.mapToExchange = {}

        t1 = Thread(target=self.run)
        t2 = Thread(target=self.retryOrders)

        # start the threads
        t1.start()
        t2.start()

        # wait for the threads to complete
        t1.join()
        t2.join()

    def createExchange(self, exchangeName:str, apiKey:str, apiSecret:str):
        '''
        Inputs  : exchangeName - the name of the exchange to create; apiKey - the api key for the exchange; apiSecret - the api secret for the exchange
        Returns : 0, if successful
        Errors  : Raise Exception if exchangeName is not in ccxt.exchanges; Raise Exception if authentication fails
        '''
        if exchangeName not in ccxt.exchanges:
            self.log.errorLog("No exchange named " + exchangeName + " exists in CCXT")
            raise Exception("No exchange named " + exchangeName + " exists in CCXT")

        exc = 'ccxt.' + exchangeName + '()'
        self.mapToExchange[exchangeName] = eval(exc)
        self.mapToExchange[exchangeName].secret = apiSecret
        self.mapToExchange[exchangeName].apiKey = apiKey

        # see if we can authenticate
        try: 
            self.mapToExchange[exchangeName].fetchBalance()
        except ccxt.AuthenticationError:
            self.log.errorLog("Authentication Error for: " + exchangeName)
            raise ("Authentication Error for: " + exchangeName)
        except:
            self.log.errorLog("Unknown Error for: " + exchangeName)
            raise ("Unknown Error for: " + exchangeName)
        else:
            return 0
    
    def getBalance(self, exchange: str):
        '''
        Inputs  : exchange - the name of the exchange to get the balance of
        Returns : the balance of the exchange, if successful
        Errors  : Log error if exchange is not in mapToExchange, Log error if ccxt error occurs
        '''
        if exchange not in self.mapToExchange:
            self.log.errorLog(f"Exchange {exchange} not declared for getBalance()")
        else:
            try:
                return self.mapToExchange[exchange].fetchBalance()
            except Exception as e:
                self.log.errorLog(f"Exception for getBalance({exchange}), {e}")

    def inspectOrder(self, exchange: str, internalID: int):
        """
        Inputs  : exchange - the name of the exchange to get the balance of; internalID - the internal ID of the order
        Returns : the order specifications, if successful; Error codes, if error
        Errors  : Log error if exchange is not in mapToExchange, Log error if unknown error occurs
        """
        if exchange not in self.mapToExchange:
            self.log.errorLog(f"Exchange {exchange} not declared for inspectOrder()")
            return 2
        else:
            try:
                orderID = self.idDict[internalID]
                return self.mapToExchange[exchange].fetchOrder(orderID)
            except Exception as e:
                self.log.errorLog(f"Exception for inspectOrder({internalID}), {e}")
                return 2
    
    def cancelOrder(self, exchange: str, internalID: int):
        '''
        Inputs  : exchange - the name of the exchange to get the balance of; internalID - the internal ID of the order
        Returns : 0, if successful; Error codes, if error
        Errors  : Log error if exchange is not in mapToExchange, Log error if unknown error occurs
        '''
        if exchange not in self.mapToExchange:
            self.log.errorLog(f"Exchange {exchange} not declared for cancelOrder()")
            return 2
        else:
            try:
                orderID = self.idDict[internalID]
                orderBook = self.mapToExchange[exchange].cancelOrder(orderID)
            except:
                return 1 #TODO: add error handling; should return 1 if recoverable error (network), return 2 if unrecoverable error
            
            self.log.orderLog(orderBook, f"[CANCELLED ORDER id = {internalID}]")
            return 0

    def changeOrder(self, internalID:int, exchange: str, symbol:str, side: str, type: str, amount: float, price: float=None):
        '''
        Inputs  : internalID - the internal ID of the order; 
                    exchange - the name of the exchange to get the balance of; 
                    symbol - the symbol of the order; 
                    side - the side of the order; 
                    type - the type of the order; 
                    amount - the amount of the order; 
                    price - the price of the order (optional)
        Returns : 0, if successful; Error codes, if error
        Errors  : Log error if exchange is not in mapToExchange, Log error if unknown error occurs
        '''
        if exchange not in self.mapToExchange:
            self.log.errorLog(f"Exchange {exchange} not declared")
            return 2
        else:
            orderID = self.idDict[internalID]
            if type == 'limit':
                if not price:
                    self.log.errorLog(f"[CHANGE ORDER id = {internalID}] Limit order placed without price | exchange = {exchange}, symbol = {symbol}, side = {side}, type = {type}, amount = {amount}")
                    return 2
                else:
                    try:
                        orderBook = self.mapToExchange[exchange].editOrder(orderID, symbol, type, side, amount, price)
                    except:
                        return 1 #TODO: add error handling; should return 1 if recoverable error (network), return 2 if unrecoverable error
            elif type == 'market':
                try:
                    orderBook = self.mapToExchange[exchange].editOrder(orderID, symbol, type, side, amount)
                except:
                    return 1 #TODO: add error handling; should return 1 if recoverable error (network), return 2 if unrecoverable error
                
            self.log.orderLog(orderBook, f"[CHANGE ORDER id = {internalID}]")
            return 0  

    def placeOrder(self, internalID: int, exchange: str, symbol: str, side: str, type: str, amount: float, price: float=None):
        '''
        Inputs  : internalID - the internal ID of the order;
                    exchange - the name of the exchange to get the balance of;
                    symbol - the symbol of the order;
                    side - the side of the order;
                    type - the type of the order;
                    amount - the amount of the order;
                    price - the price of the order (optional)
        Returns : 0, if successful; Error codes, if error
        Errors  : Log error if exchange is not in mapToExchange, Log error if unknown error occurs
        '''
        if exchange not in self.mapToExchange:
            self.log.errorLog(f"Exchange {exchange} not declared for placeOrder()")
            return 2
        else:
            if type == 'limit':
                if not price:
                    self.log.errorLog(f"Limit order {internalID} placed without price | exchange = {exchange}, symbol = {symbol}, side = {side}, type = {type}, amount = {amount}")
                    return 2
                else:
                    try:
                        orderBook = self.mapToExchange[exchange].createOrder(symbol, type, side, amount, price)
                    except:
                        return 1 #TODO: add error handling; should return 1 if recoverable error (network), return 2 if unrecoverable error
            elif type == 'market':
                try:
                    orderBook = self.mapToExchange[exchange].createOrder(symbol, type, side, amount)
                except:
                    return 1 #TODO: add error handling; should return 1 if recoverable error (network), return 2 if unrecoverable error 
                
            self.idDict[internalID] = orderBook['id']
            self.log.orderLog(orderBook, f"[PLACED ORDER id = {self.idDict[internalID]}]")
            return 0  
    
    def retryOrders(self):
        '''
        Inputs  : None
        Returns : None
        Errors  : Log error if unknown error occurs
        '''
        try:
            while self.retryQueue.qsize() > 0:
                order = self.retryQueue.pop(0)
                if order['timePlaced'] + order['retryTime'] < datetime.now():
                    self.log.errorLog(f"Order {order['internalID']} has not been placed and has expired")
                else:
                    if order['category'] == 'place':
                        res = self.placeOrder(order['internalID'], order['exchange'], order['symbol'], order['side'], order['type'], order['amount'], order['price']) if order['type'] == 'limit' else self.placeOrder(order['exchange'], order['symbol'], order['side'], order['type'], order['amount'])
                    elif order['category'] == 'cancel':
                        res = self.cancelOrder(order['exchange'], order['internalID'])
                    elif order['category'] == 'change':
                        res = self.changeOrder(order['internalID'], order['exchange'], order['symbol'], order['side'], order['type'], order['amount'], order['price']) if order['type'] == 'limit' else self.changeOrder(order['internalID'], order['exchange'], order['symbol'], order['side'], order['type'], order['amount'])

                    if res == 1:
                        self.retryQueue.append(order)
        except Exception as e:
            self.log.errorLog(f"Exception for retryOrders(), {e}")
            raise RuntimeError

    def run(self):
        '''
        Inputs  : None
        Returns : None
        Errors  : Log error if unknown error occurs
        '''
        try:
            while self.orderQueue.qsize() > 0:
                order = self.orderQueue.pop(0)
                if order['timePlaced'] + order['retryTime'] < datetime.now():
                    self.log.errorLog(f"Order {order['internalID']} has not been placed and has expired")
                else:
                    if order['category'] == 'place':
                        res = self.placeOrder(order['internalID'], order['exchange'], order['symbol'], order['side'], order['type'], order['amount'], order['price']) if order['type'] == 'limit' else self.placeOrder(order['exchange'], order['symbol'], order['side'], order['type'], order['amount'])
                    elif order['category'] == 'cancel':
                        res = self.cancelOrder(order['exchange'], order['internalID'])
                    elif order['category'] == 'change':
                        res = self.changeOrder(order['internalID'], order['exchange'], order['symbol'], order['side'], order['type'], order['amount'], order['price']) if order['type'] == 'limit' else self.changeOrder(order['internalID'], order['exchange'], order['symbol'], order['side'], order['type'], order['amount'])

                    if res == 1:
                        self.retryQueue.append(order)
        except Exception as e:
            self.log.errorLog(f"Exception for run(), {e}")
            raise RuntimeError

    '''
    Order attributes:
    {   'category' : 'place', 'change', 'cancel' (type=str),                | the category of the queue entry
        'timePlaced' : datetime object (type=datetime.datetime),            | the time the order was placed
        'retryTime' : timedelta object (type=datetime.timedelta),           | the maximum elapsed time the order can be in the queue before it is cancelled
        'internalID' : 12345, (type=int),                                   | the INTERNAL ID of the order, generated by the trading team. This is the ID that will be used to cancel or modify the order. it will be internally mapped to a ccxt ID.
        'exchange' : 'binance', (type=str),                                 | the exchange the order is placed on
        'symbol' : 'USDT/ETH', (type=str),                                  | the symbol the order is placed on
        'side' : 'buy' or 'sell' (type=str),                                | the side of the order
        'type' : 'limit' or 'market' (type=str),                            | the type of the order
        'amount' : 1.0, (type=float),                                       | the amount of the order
        'price' : 100.0 (type=float) (should be None for market orders)     | the price of the order (only for limit place & limit modify orders)
    }
    '''