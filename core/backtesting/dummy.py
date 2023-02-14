import math
import time

class dummy:
    
    def __init__(self):
        self.tick = 0
        
    def update(self, sth):
        self.tick += 1
        if self.tick % 2 == 0:
            return {'AAPL':'BUY'}
        else:
            return {'AAPL':'SELL'}