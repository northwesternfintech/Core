import attr


@attr.s(slots=True)
class Asset():
    """Object for storing asset information for a portfolio

    Parameters
    ----------
    name : str
        Name of the asset

    Returns
    -------
    _type_
        _description_
    """
    name: str = attr.ib()
    amount: float = attr.ib(init=False, default=0)
    average_price: float = attr.ib(init=False, default=0)

    def update_asset(self, amount: float, price: float) -> bool:
        """This function updates the asset whenever a buy/sell order
        order is completed.

        Parameters
        ----------
        amount : float
            an integer that represents the change in the number of assets
            (amount < 0 decreases self.amount, amount > 0 increases self.amount)
        price : float
            a float that represents the price of the incoming asset

        When amount < 0 and price = 0, this indicates a sell order

        Returns
        -------
        _type_
            _description_
        """
        # calculate the new average price
        curr_average_weight = self.average_price * self.amount
        new_average_weight = price * amount
        total_amount = self.amount + amount

        self.average_price = (curr_average_weight + new_average_weight) / total_amount

        # updates the amount of assets held
        self.amount += amount

        return True
