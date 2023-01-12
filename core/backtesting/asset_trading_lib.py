class asset:
    def __init__(self, asset_name):
        """
        Asset Object contains the fields storing the information to be stored
        about each individual stock/asset the portfolio holds

        asset_name: String that holds the name of the object
        """

        self.name = asset_name
        self.amount = 0  # stores the amount of asset
        self.average_price = 0  # stores the average price of the asset

    def get_name(self):
        return self.name

    def get_amount(self):
        return self.amount

    def get_average_price(self):
        return self.amount

    def update_asset(self, amount, price):
        """
        This function updates the asset whenever a buy/sell order
        order is completed.

        amount: an integer that represents the change in the number of assets
                (amount < 0 decreases self.amount, amount > 0 increases self.amount)
        price: a float that represents the price of the incoming asset

        When amount < 0 and price = 0, this indicates a sell order
        """

        # calculate the new average price
        curr_average_weight = self.get_average_price() * self.get_amount()
        new_average_weight = price * amount
        total_amount = self.get_amount + amount

        self.average_price = (curr_average_weight + new_average_weight) / total_amount

        # updates the amount of assets held
        self.amount += amount

        return True
