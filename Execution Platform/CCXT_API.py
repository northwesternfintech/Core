import ccxt
#import ccxt.async_support as ccxt

class executionPlatform:
  def __init__():
    # self.exchangeInfo = {'binance':(binanceKey, binanceSecret, ccxt.binance()), 'bitmex':(bitmexKey, bitmexSecret)}
    self.exchangeInfo = {'binance':(ccxt.binance({'apikey': binanceKey, 'secret': binanceSecret}))}

  def placeOrder(self, exchangeName, XXX):

    exchangeKey, exchangeSec, exchangeObj = self.exchangeInfo[exchangeName]

    # Place order



# kraken = ccxt.kraken({
#     'apiKey': 'YOUR_PUBLIC_API_KEY',
#     'secret': 'YOUR_SECRET_PRIVATE_KEY',
# })


