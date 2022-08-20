import numpy as np
import pandas as pd
from pandastable import Table, TableModel
from coingeckopremium_test.api import CoinGeckoAPI

cg = CoinGeckoAPI()
import tkinter as tk

markets2 = cg.get_exchanges_by_id(id="kraken")

markets = cg.get_exchanges_tickers_by_id(id="kraken")


print("wait")
