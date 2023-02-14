import time
import collections
import math

#Single-stock template for EMA strategy

class EMASingleStock():
  """
  Single-stock template for overlapping EMA strategy
  """
  
  def __init__(self):
    """
    Version of init if we have no previous data
    """
    self.price = 0
    self.time = time.time()
    self.orders = []
    self.EMA200d = 0
    self.EMA50d = 0
    self.days = 0
    self.shortOverLong = False
  
  def __init__(self, **kwargs):
    """
    Version of init if we already have values for EMA200d, EMA50d, and price
    @type price: float
    @type EMA200d: float
    @type EMA50d: float
    """
    self.price = kwargs["price"]
    self.time = time.time()
    self.orders = []
    self.EMA200d = kwargs["EMA200d"]
    self.EMA50d = kwargs["EMA50d"]
    self.days = 201
    self.shortOverLong = self.EMA50d>self.EMA200d
  
  #these are probably just here for template for multi-stock. for one stock can just use self.x
  def get_price(self):
    return self.price
  def get_time(self):
    return self.time
  def get_orders(self):
    return self.orders
  def get_ticks(self):
    return self.ticks
  def get_EMA50(self):
    return self.EMA50d
  def get_EMA200(self):
    return self.EMA200d
  def get_days(self):
    return self.days

  def clear_orders(self):
    """
    Clears all current orders and logs relevant information.
    """
    print(f"Trashing %d orders.", len(self.orders))
    self.orders = []

  def calculate_ema(days, newPrice, prev_ema):
    """
    @type days: int
    @type newPrice: float
    @type prev_ema: float
    @rtype: float
    """
    mult = 2/(days+1)
    new_ema = newPrice*mult + prev_ema*(1-mult)
    return new_ema
    
  def update(self, newPrice):
    """
    Will be called on every tick to update the algorithm state and output buys/sells.
    @type newPrice: float
    @rtype: list
    """
    #Increment days and clear orders
    self.days += 1
    self.clear_orders()
    
    #Calculate EMA based on how many days are currently updated
    if self.days<50:
      self.EMA50d = self.calculate_ema(self.days, newPrice, self.EMA50d)
      self.EMA200d = self.calculate_ema(self.days, newPrice, self.EMA200d)
    elif self.days<200:
      self.EMA50d = self.calculate_ema(50, newPrice, self.EMA50d)
      self.EMA200d = self.calculate_ema(self.days, newPrice, self.EMA200d)
    else:
      self.EMA50d = self.calculate_ema(50, newPrice, self.EMA50d)
      self.EMA200d = self.calculate_ema(200, newPrice, self.EMA200d)


    if self.EMA50d>self.EMA200d: #If our short signal is higher than our long signal, we expect future rises
      if not(self.shortOverLong) and self.days>250: #When short goes from under long signal to over long signal
        self.orders.append("BUY")                   #We think prices are low now and will rise in the future, so we buy
      self.shortOverLong = True

    elif self.EMA50<=self.EMA200d: #If our short signal is lower than our long signal, we expect future dips
      if self.shortOverLong and self.days>250:       #When short goes from over long signal to under long signal
        self.orders.append("SELL")                   #We think prices are high now and will lower in the future, so we sell
      self.shortOverLong = False
    

    return self.orders