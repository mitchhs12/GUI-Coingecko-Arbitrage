from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
coin_ticker = 'chainlink'
import pandas as pd

# Get Exchange Tickers
request = cg.get_exchanges_id_name_list()
data1 = request
df1 = pd.DataFrame(data1)
#print(df1['id'][77]) #gets exchange id in the id column of the exchange list panda table
exchanges_df = pd.DataFrame()
for exchange_name in df1['id']:
    print(exchange_name)
    request2 = cg.get_exchanges_tickers_by_id(id=exchange_name,coin_ids='chainlink')
    data2 = request2.get('tickers')
    df2 = pd.DataFrame(data2)
    print(len(df2))
    if len(df2)!=0:
        print('apending')
        exchanges_df = exchanges_df.append(df2)

print('end')
# Query Exchanges for Coins
#request2 = cg.get_exchanges_tickers_by_id(id=exchange_name,coin_ids='chainlink')
#data2 = request2.get('tickers')
#df2 = pd.DataFrame(data2)
