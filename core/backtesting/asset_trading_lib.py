class asset():

    def __init__(self, asset_name):

        self.name = asset_name
        self.amount = 0
        self.average_price = 0

    def get_name(self): return self.name

    def get_amount(self): return self.amount

    def get_average_price(self): return self.amount

    def update_asset(self, amount, price):
        '''
        This function updates the asset whenever a buy/sell order
        order is completed.
        '''

        curr_average_weight = self.get_average_price() * self.get_amount() 
        new_average_weight = price * amount
        total_amount = self.get_amount + amount

        self.average_price = (curr_average_weight + new_average_weight) / total_amount
        self.amount += amount

        return