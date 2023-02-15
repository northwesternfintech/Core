import math
import time

class dummy:
    
    def __init__(self):
        self.tick = 0
        self.tickers = \
        ['CSCO', 'UAL', 'TROW', 'ISRG', 'NVR', 'TPR', 'DVN', 'CE', 'MRO',
       'BA', 'VRTX', 'GILD', 'EQIX', 'TER', 'MDT', 'V', 'QRVO', 'A',
       'FOX', 'FLT', 'MO', 'CTRA', 'SWKS', 'ENPH', 'MCHP', 'CDNS', 'MSCI',
       'CHTR', 'EIX', 'KDP', 'BBY', 'WBA', 'LVS', 'HCA', 'AJG', 'DTE',
       'C', 'T', 'CF', 'DISH', 'MGM', 'HUM', 'CBOE', 'CFG', 'APH', 'SYY',
       'MSI', 'FCX', 'ADM', 'OGN', 'LH', 'PKI', 'LNT', 'BAC', 'LNC',
       'PSX', 'GPN', 'PPG', 'TECH', 'IRM', 'IQV', 'ESS', 'WBD', 'HAL',
       'STZ', 'DXC', 'PARA', 'ADI', 'F', 'ADBE', 'CPRT', 'TDG', 'TFX',
       'ULTA', 'ARE', 'SYK', 'CB', 'TSN', 'GNRC', 'PEP', 'PEG', 'NOW',
       'LLY', 'COST', 'REG', 'NWS', 'LOW', 'MDLZ', 'BKNG', 'ZBRA', 'FMC',
       'XEL', 'AIZ', 'MET', 'FTV', 'DLR', 'ACGL', 'XRAY', 'FAST', 'TJX',
       'SNA', 'MPC', 'BR', 'D', 'MRK', 'STX', 'NOC', 'BXP', 'KHC', 'IPG',
       'UNP', 'ALLE', 'ABBV', 'CDAY', 'ORCL', 'ECL', 'ETR', 'EBAY',
       'SBUX', 'IR', 'AMT', 'INTU', 'DPZ', 'PAYC', 'CMA', 'PG', 'CAT',
       'ODFL', 'MCD', 'MNST', 'AMZN', 'INTC', 'PNR', 'GLW', 'BDX', 'KMI',
       'CSGP', 'PWR', 'APTV', 'BBWI', 'DXCM', 'EXR', 'WELL', 'HOLX',
       'EXPD', 'GM', 'TXN', 'VRSK', 'SJM', 'TMO', 'OXY', 'RL', 'CCI',
       'MMM', 'MOS', 'FTNT', 'HSY', 'JNPR', 'DHI', 'ED', 'ES', 'ADSK',
       'GL', 'INVH', 'IP', 'EXPE', 'KO', 'PCAR', 'WDC', 'LUMN', 'PYPL',
       'NEE', 'UPS', 'ELV', 'EMR', 'MSFT', 'ANSS', 'CTAS', 'BIO', 'UDR',
       'CTLT', 'WEC', 'AME', 'IT', 'DD', 'ACN', 'VRSN', 'EW', 'CMG',
       'AWK', 'COO', 'SHW', 'HPQ', 'AMAT', 'CCL', 'MLM', 'AVY', 'AAP',
       'ATVI', 'EVRG', 'EA', 'DE', 'SPG', 'AMD', 'KLAC', 'NDAQ', 'URI',
       'WHR', 'RTX', 'NXPI', 'PNC', 'KMX', 'SEDG', 'WRK', 'MTCH', 'BIIB',
       'NVDA', 'CHRW', 'ROP', 'IDXX', 'EXC', 'HES', 'HD', 'ALB', 'VLO',
       'AON', 'ZTS', 'FDX', 'DG', 'TYL', 'HIG', 'CMS', 'CAG', 'INCY',
       'SCHW', 'HSIC', 'AZO', 'AXP', 'HPE', 'DFS', 'SEE', 'HRL', 'SO',
       'FRT', 'ZBH', 'FRC', 'CME', 'XOM', 'AMP', 'CVX', 'CMCSA', 'PCG',
       'PNW', 'ICE', 'BEN', 'UHS', 'BKR', 'EMN', 'SBAC', 'ROK', 'PTC',
       'NRG', 'NSC', 'NKE', 'FIS', 'FANG', 'VTR', 'MAS', 'RF', 'ETSY',
       'AMCR', 'TAP', 'MAR', 'XYL', 'CMI', 'MTD', 'KR', 'PLD', 'IBM',
       'USB', 'BSX', 'LKQ', 'FBHS', 'LIN', 'ITW', 'EOG', 'KMB', 'PEAK',
       'SPGI', 'NEM', 'WFC', 'CTVA', 'EL', 'GS', 'GD', 'CNP', 'PM', 'RE',
       'MCO', 'CLX', 'CAH', 'MPWR', 'DGX', 'AVB', 'DIS', 'CBRE', 'GE',
       'HII', 'LDOS', 'ALL', 'ETN', 'ALGN', 'NFLX', 'SBNY', 'LEN', 'FITB',
       'WST', 'GWW', 'TRGP', 'NTRS', 'CVS', 'AOS', 'FE', 'ABC', 'JPM',
       'ABT', 'OMC', 'COF', 'TSCO', 'PH', 'HST', 'JBHT', 'MRNA', 'TSLA',
       'MOH', 'ATO', 'COP', 'DHR', 'CNC', 'MCK', 'TXT', 'MTB', 'FDS',
       'VTRS', 'AKAM', 'ROL', 'RMD', 'WRB', 'GOOGL', 'BRO', 'ANET',
       'PAYX', 'ALK', 'DRI', 'ILMN', 'META', 'AAL', 'MAA', 'MMC', 'FOXA',
       'POOL', 'CZR', 'FFIV', 'VNO', 'CINF', 'VMC', 'MKTX', 'SRE', 'LHX',
       'ORLY', 'IVZ', 'RCL', 'PXD', 'SNPS', 'GOOG', 'EPAM', 'SIVB',
       'NDSN', 'YUM', 'EQT', 'LYV', 'PFE', 'AVGO', 'DUK', 'REGN', 'CL',
       'VFC', 'VZ', 'JCI', 'AMGN', 'TEL', 'JKHY', 'ADP', 'ON', 'STT',
       'RSG', 'IFF', 'CARR', 'TRMB', 'QCOM', 'LYB', 'GIS', 'PHM', 'ROST',
       'LUV', 'LW', 'MS', 'CPB', 'OKE', 'BK', 'J', 'SYF', 'CHD', 'HWM',
       'MHK', 'TFC', 'DAL', 'APA', 'K', 'AFL', 'CSX', 'NI', 'CPT', 'PFG',
       'NCLH', 'ZION', 'RJF', 'HBAN', 'UNH', 'PRU', 'GPC', 'WTW', 'FISV',
       'WMB', 'EQR', 'DVA', 'AIG', 'MA', 'HON', 'VICI', 'O', 'NWSA',
       'TTWO', 'AES', 'SLB', 'TT', 'TGT', 'AAPL', 'MKC', 'OTIS', 'CEG',
       'TDY', 'WY', 'APD', 'GRMN', 'AEE', 'HLT', 'DLTR', 'STE', 'HAS',
       'TMUS', 'WMT', 'NTAP', 'KIM', 'BAX', 'LMT', 'ABMD', 'KEY', 'KEYS',
       'BMY', 'PSA', 'WYNN', 'RHI', 'EFX', 'NUE', 'PKG', 'WAB', 'CTSH',
       'SWK', 'CRL', 'MU', 'TRV', 'L', 'AEP', 'CI', 'DOW', 'CDW', 'BALL',
       'JNJ', 'WM', 'DOV', 'CRM', 'PGR', 'WAT', 'IEX', 'BWA', 'LRCX',
       'NWL', 'BLK', 'PPL']
        self.buy_dict = dict.fromkeys(self.tickers, "BUY")
        self.sell_dict = dict.fromkeys(self.tickers, "SELL")
        
    def update(self, sth):
        self.tick += 1
        if self.tick % 2 == 0:
            return self.buy_dict
        else:
            return self.sell_dict