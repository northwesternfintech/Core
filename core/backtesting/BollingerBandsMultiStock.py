import collections
import math


class BollingerBandsMultiStock:
    def __init__(self, tickers, dayConst=60, MAL=20, bandSD=2, clearDataLen=10000):
        """
        Constructor for multi stock Bollinger Bands algo. If the stock price exceeds the upper band, add a sell order,
        and if it goes below the lower band, add a buy order.
        """
        # general data dict, not used here, but keeping in case needed for revisions later
        self.data = {}
        # stores ticker: orders
        self.orders = {}
        # Stands for typical price. stores ticker: list of len(MAL) where self.TP[ticker][i] contains that days [open, high, low, close]
        self.typicalPrices = {}
        # contains ticker: [open, high, low, close] of current day. Reset at beginning of each day
        self.dayData = {}
        # stores ticker: lower band, upper band
        self.bands = {}
        for ticker in tickers:
            self.data[ticker] = []
            self.orders[ticker] = []
            self.typicalPrices[ticker] = []
            self.dayData[ticker] = [-1, -1, math.inf, -1]
            self.bands[ticker] = [0, 0]

        self.ticks = 0
        # stores how many ticks we want there to be in each day. By default set to 60, or every hour
        self.ticksPerDay = dayConst
        # stores how many previous days' data we want to use in our moving average. By default set to 20
        self.daysInMovingAverage = MAL
        # stores how many standard deviations we want to use to calculate our upper and lower bands. By default set to 2
        self.bandSigmaFromMean = bandSD
        # stores when our next day stats (in ticks)
        self.nextDayStart = dayConst
        # variable to clear our least recent orders so that the length of the list doesnt get too big. By default set to 10,000
        self.clearDataLen = clearDataLen

    def clear_orders(self, ticker):
        """
        Clears all current orders and logs relevant information.
        """
        print(f"Trashing %d orders.", len(self.orders[ticker]))
        self.orders[ticker] = []

    def getSigma(self, ticker):
        """
        Returns the standard deviation data in self.typicalPrices. Follows standard sigma formula
        """
        mean = sum(self.typicalPrices[ticker]) / self.daysInMovingAverage
        total = 0.0
        for price in self.typicalPrices[ticker]:
            total += (price - mean) ** 2
        total /= self.daysInMovingAverage
        return total**0.5

    def update_all(self, newData):
        """
        generic update method that calls update on every ticker
        """

        newDay = False
        # if the tick we're at is equal to our defined time for when the next "day" starts, make note of the fact that we're
        # on a new "day" and update the time of the next "day" start.
        if self.ticks == self.nextDayStart:
            self.nextDayStart = self.ticks + self.ticksPerDay
            newDay = True

        for ticker, newPrice in newData.items():
            self.update(ticker, newPrice, newDay)
        self.ticks += 1
        # print("Typical Prices:", self.typicalPrices)
        # print("Bands:", self.bands)
        # print("Orders:", self.orders)
        # print()

    def update(self, ticker, price, newDay):
        """
        Update method called every tick. Just takes in the stock's price at the time of the tick
        """
        if newDay:
            # handle all new day management stuff
            # if we're at a new day, add our current day's data to TP and reset the dayData
            # print(ticker, self.dayData[ticker])
            self.typicalPrices[ticker].append(sum(self.dayData[ticker]) / 4)
            self.dayData[ticker] = [-1, price, price, price]

        # open, high, low, close — update all accordingly
        # update open only once
        if self.dayData[ticker][0] == -1:
            self.dayData[ticker][0] = price
        self.dayData[ticker][1] = max(self.dayData[ticker][1], price)
        self.dayData[ticker][2] = min(self.dayData[ticker][2], price)
        self.dayData[ticker][3] = price

        # only run core logic if algo has been running for at least MAL ticks
        if len(self.typicalPrices[ticker]) > self.daysInMovingAverage:
            self.typicalPrices[ticker].pop(0)
            # get appropriate stats
        if len(self.typicalPrices[ticker]) == self.daysInMovingAverage:
            sig = self.getSigma(ticker)
            mean = sum(self.typicalPrices[ticker]) / self.daysInMovingAverage

            lowerBand = mean - self.bandSigmaFromMean * sig
            upperBand = mean + self.bandSigmaFromMean * sig
            # update appropriate bands
            self.bands[ticker][0] = lowerBand
            self.bands[ticker][1] = upperBand

            if price > upperBand:
                # print("ADDING SELL ORDER")
                self.orders[ticker].append("SELL")
            elif price < lowerBand:
                # print("ADDING BUY ORDER")
                self.orders[ticker].append("BUY")
            # print()

            if len(self.orders[ticker]) > self.clearDataLen:
                self.orders[ticker].pop(0)


"""BB = BollingerBandsMultiStock(["A", "B", "C"], 4, 4, 2, 100)
BB.update_all({"A": 4.0, "B": 6.0, "C": 8.0})
BB.update_all({"A": 2.0, "B": 16, "C": 7})
BB.update_all({"A": 12, "B": 9, "C": 11})
BB.update_all({"A": 4.0, "B": 3.3, "C": 8.7})

BB.update_all({"A": 3.1, "B": 6.4, "C": 9.23})
BB.update_all({"A": 15.4, "B": 19.3, "C": 10.1})
BB.update_all({"A": 4.2, "B": 4.2, "C": 1.1})
BB.update_all({"A": 3, "B": 6, "C": 8})

BB.update_all({"A": 3.0, "B": 6.0, "C": 8.0})
BB.update_all({"A": 4, "B": 16, "C": 7})
BB.update_all({"A": 12, "B": 9, "C": 11})
BB.update_all({"A": 5, "B": 3.3, "C": 8.7})

BB.update_all({"A": 3.1, "B": 6.4, "C": 9.23})
BB.update_all({"A": 15.4, "B": 19.3, "C": 10.1})
BB.update_all({"A": 4.2, "B": 4.2, "C": 1.1})
BB.update_all({"A": 3, "B": 6, "C": 8})"""
