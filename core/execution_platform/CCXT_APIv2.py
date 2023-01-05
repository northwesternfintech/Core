import ccxt
from log_class import LoggingClass
from dotenv import load_dotenv
from collections import deque
from datetime import datetime
from threading import Thread

class executionPlatform:
    
    def __init__(self, orderQueue, logAddress = None):
        '''
        Inputs  : orderQueue - a mp.Queue() for orders; logAddress - the address of the log file (optional)
        Returns : None
        Errors  : Raise Exception if file cannot be created at the log address    
        '''
        self.orderQueue = orderQueue
        
        load_dotenv()
        self.log = LoggingClass(logAddress) if logAddress else LoggingClass(LOG_DIR_PATH)
        if self.log.status == 1:
            raise Exception("Log file could not be created")

        self.retryQueue = deque()

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
        Errors  : Raise Exception if exchangeName is not in ccxt.exchanges or if authentication fails
        '''
        if exchangeName not in ccxt.exchanges:
            self.log.errorLog("No exchange named " + exchangeName + " exists in CCXT | t=" + str(datetime.now()))
            raise Exception("No exchange named " + exchangeName + " exists in CCXT")

        exc = 'ccxt.' + exchangeName + '()'
        self.mapToExchange[exchangeName] = eval(exc)
        self.mapToExchange[exchangeName].secret = apiSecret
        self.mapToExchange[exchangeName].apiKey = apiKey

        # see if we can authenticate
        try: 
            self.mapToExchange[exchangeName].fetchBalance()
        except ccxt.AuthenticationError:
            self.log.errorLog("Authentication Error for: " + exchangeName + " | t=" + str(datetime.now()))
            raise ("Authentication Error for: " + exchangeName)
        except:
            self.log.errorLog("Unknown Error for: " + exchangeName + " | t=" + str(datetime.now()))
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
            self.log.errorLog(f"Exchange {exchange} not declared")
        else:
            try:
                return self.mapToExchange[exchange].fetchBalance()
            except Exception as e:
                self.log.errorLog(f"Exception for getBalance({exchange}), {e}")

    def inspectOrder(self, exchange: str, orderID: int):
        """inspectOrder() takes in the exchange name and order ID. It returns all of the order information in the returned 'Order Structure'."""
        if exchange not in self.mapToExchange:
            self.log.errorLog(f"Exchange {exchange} not declared")
        else:
            try:
                return self.mapToExchange[exchange].fetch_order(orderID)
            except Exception as e:
                self.log.errorLog(f"Exception for inspectOrder({exchange}), {e}")
    
    def cancelOrder(self, exchange: str, orderID: int):
        pass

    def changeOrder(self, exchange: str, orderID: int, amount: float, price: float):
        pass

    def placeOrder(self, exchange: str, symbol: str, side: str, type: str, amount: float, price: float):
        pass
    
    def retryOrders(self):
        pass

    def run(self):
        pass