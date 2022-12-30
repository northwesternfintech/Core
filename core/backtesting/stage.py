from strategy import Strategy
from BollingerBandsMultiStock import BollingerBandsMultiStock


def main():
    strat = Strategy()
    strat.setStrategy(BollingerBandsMultiStock)
