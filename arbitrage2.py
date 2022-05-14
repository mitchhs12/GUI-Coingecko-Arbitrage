import numpy as np
import pandas as pd
from pandastable import Table, TableModel
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
import time
import tkinter as tk

historic_data = []
profit_threshold = 200  # Given so as to remove data outliers (expressed as a percentage e.g. 100 will remove profits > 100%)
volume_threshold = 1000000  # Given in USD to remove low volume trades
target = "LINK"  # set to '0' if no coin pair target is specified
pages = 1  # how many pages for each cryptocurrency are needed


# --- functions ---


def append(df, g):
    historic_data.append(df)
    if g == True:
        return historic_data
    if g == False:
        del historic_data[
            (len(historic_data) - ((len(historic_data) - 1))) : (len(historic_data) - 1)
        ]
        return historic_data


def btn_update():  # reruns app
    pt.model.df = df_loop()
    pt.redraw()


def call(coin_ticker):
    amount_per_page = 100
    pairs = amount_per_page * pages
    call = int((pairs - pairs % amount_per_page) / amount_per_page) + 1
    list_of_coins = cg.get_coin_ticker_by_id(id=coin_ticker, page=1)
    list_of_coins = list_of_coins.get("tickers")
    list = list_of_coins
    df = pd.DataFrame(list)
    print("Getting page:", 1)
    for q in range(
        call - 1
    ):  # needs to be (call-1) because we already have the first page
        strung = str(q + 2)
        list2 = cg.get_coin_ticker_by_id(id=coin_ticker, page=strung)
        list2 = list2.get("tickers")
        if (list2 == []) or (int(strung) > pairs / amount_per_page):
            break
        else:
            print("Getting page:", strung)
            df2 = pd.DataFrame(list2)
            df2.reset_index(drop=True, inplace=True)
            df = pd.concat([df, df2])
            df.reset_index(drop=True, inplace=True)
            time.sleep(7)
    return df


def df_loop():
    df = call(coin_ticker)
    df = format_columns(df, coin_ticker)
    summary_statistics(df)
    historic_data = append(df, True)
    if historic_data[(len(historic_data) - 1) - 1]["Usd Price"].equals(
        historic_data[(len(historic_data) - 1)]["Usd Price"]
    ):
        return df
    else:
        print("PRICES UPDATED")
        summary_statistics(
            historic_data[(len(historic_data) - 1)]
        )  # summary statistics on last df
        historic_data = append(df, False)
        return historic_data[(len(historic_data) - 1)]  # returns last df


def format_columns(df, coin_ticker):
    market_data_df = isolate_column(df, "market")
    df.insert(3, "trading_incentive", market_data_df["has_trading_incentive"])
    df.insert(3, "identifier", market_data_df["identifier"])
    df.insert(3, "name", market_data_df["name"])
    del df["market"]
    converted_last_df = isolate_column(df, "converted_last")
    df.insert(7, "usd_price", converted_last_df["usd"])
    df.insert(7, "eth_price", converted_last_df["eth"])
    df.insert(7, "btc_price", converted_last_df["btc"])
    del df["converted_last"]
    converted_volume_df = isolate_column(df, "converted_volume")
    df.insert(10, "usd_volume", converted_volume_df["usd"])
    df.insert(10, "eth_volume", converted_volume_df["eth"])
    df.insert(10, "btc_volume", converted_volume_df["btc"])
    del df["converted_volume"]
    del df["token_info_url"]
    # formatting column titles
    df.rename(columns={"volume": coin_ticker + " volume"}, inplace=True)
    df.columns = [x.title() for x in df.columns]
    df.columns = [x.replace("_", " ") for x in df.columns]
    return df


def get_coin_list(data):
    coin_df = pd.DataFrame(data)
    list = coin_df["id"].tolist()
    return list


def isolate_column(
    raw_data, column_name
):  # isolates and returns a column in a panda as a panda data frame
    list = []
    for i in range(len(raw_data)):
        list.append(raw_data.iloc[i][column_name])
    listFrame = pd.DataFrame(list)
    return listFrame


def profit_maximiser():
    list_of_coins = get_coin_list(cg.get_coins_markets("usd"))
    profit_list = []
    stats_list = []
    for coin_ticker in list_of_coins:
        print("COIN ID:", coin_ticker)
        df = call(coin_ticker)
        df = format_columns(df, coin_ticker)
        profit_margin = summary_statistics(df)
        profit_list.append(profit_margin[0])
        stats_list.append(profit_margin[1])
        time.sleep(1 * pages)  # otherwise I have to pay for Coingecko
    combined_dictionary = {"Coin Ticker": list_of_coins, "Expected Profit": profit_list}
    stats_dictionary = {
        "Marketcap Rank": [item for item in range(1, 101)],
        "Coin Ticker": list_of_coins,
        "Expected Profit": [item[10] for item in stats_list],
        "Lowest Price": [item[0] for item in stats_list],
        "Exchange with lowest price": [item[6] for item in stats_list],
        "Target for lowest price": [item[1] for item in stats_list],
        "Volume on exchange with lowest price (USD)": [item[7] for item in stats_list],
        "Highest Price": [item[2] for item in stats_list],
        "Exchange with highest price": [item[8] for item in stats_list],
        "Target for highest price": [item[3] for item in stats_list],
        "Volume on exchange with highest price (USD)": [item[9] for item in stats_list],
        "Row of lowest price": [item[4] for item in stats_list],
        "Row of highest price": [item[5] for item in stats_list],
    }
    expected_profit_df = pd.DataFrame(combined_dictionary)
    stats_df = pd.DataFrame(stats_dictionary)
    return expected_profit_df, stats_df


def replace_column(
    data_frame, column_to_be_replaced, data_frame_2, column_data_frame_2
):  # replaces a column in a panda df with another
    data_frame[column_to_be_replaced] = data_frame_2[column_data_frame_2]
    return data_frame


def summary_statistics(df):
    df.replace(0, np.NaN, inplace=True)
    if target != "0":
        if target in df["Target"].values or target in df["Base"].values:
            df1 = df[df["Target"].str.contains(target)]
            df2 = df[df["Base"].str.contains(target)]
            df = pd.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
            percentage_profit, stats_df = summary_statistics_continue(df)
            return percentage_profit, stats_df
        else:
            percentage_profit = 0
            stats_df = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            return percentage_profit, stats_df
    else:
        percentage_profit, stats_df = summary_statistics_continue(df)
        return percentage_profit, stats_df


def summary_statistics_continue(df):
    min_price = df["Usd Price"].min(skipna=True)  # returns the lowest price
    max_price = df["Usd Price"].max(skipna=True)  # returns the highest price
    index_min = df["Usd Price"].idxmin(
        skipna=True
    )  # returns the index of the row of the lowest price
    index_max = df["Usd Price"].idxmax(
        skipna=True
    )  # returns the index of the row of the highest price
    min_price_exchange = df.at[
        index_min, "Name"
    ]  # returns the exchange with the lowest price
    max_price_exchange = df.at[
        index_max, "Name"
    ]  # returns the exchange with the highest price
    min_price_vol = df.at[
        index_min, "Usd Volume"
    ]  # returns the volume on the exchange that has the lowest price
    max_price_vol = df.at[
        index_max, "Usd Volume"
    ]  # returns the volume on the exchange that has the highest price
    if min_price != max_price:
        while (min_price_vol < volume_threshold) or (np.isnan(min_price_vol)):
            if min_price_vol != max_price_vol:
                if np.isnan(min_price_vol) and np.isnan(max_price_vol):
                    percentage_profit = min_price_vol
                    print("No exchange meets the required volume threshold")
                    stats_df = (
                        min_price,
                        (df.at[index_min, "Target"]),
                        max_price,
                        df.at[index_max, "Target"],
                        index_min + 1,
                        index_max + 1,
                        min_price_exchange,
                        min_price_vol,
                        max_price_exchange,
                        max_price_vol,
                        percentage_profit,
                    )
                    return percentage_profit, stats_df
                else:
                    df.at[index_min, "Usd Price"] = np.NaN
                    min_price = df["Usd Price"].min(skipna=True)
                    index_min = df["Usd Price"].idxmin(
                        skipna=True
                    )  # returns the row of the lowest price
                    min_price_vol = df.at[index_min, "Usd Volume"]
                    min_price_exchange = df.at[
                        index_min, "Name"
                    ]  # returns the exchange with the lowest price
            else:
                break
        while (max_price_vol < volume_threshold) or (np.isnan(max_price_vol)):
            if min_price_vol != max_price_vol:
                if np.isnan(min_price_vol) and np.isnan(max_price_vol):
                    percentage_profit = max_price_vol
                    print("No exchange meets the required volume threshold")
                    stats_df = (
                        min_price,
                        (df.at[index_min, "Target"]),
                        max_price,
                        df.at[index_max, "Target"],
                        index_min + 1,
                        index_max + 1,
                        min_price_exchange,
                        min_price_vol,
                        max_price_exchange,
                        max_price_vol,
                        percentage_profit,
                    )
                    return percentage_profit, stats_df
                else:
                    df.at[index_max, "Usd Price"] = np.NaN
                    max_price = df["Usd Price"].max(skipna=True)
                    index_max = df["Usd Price"].idxmax(
                        skipna=True
                    )  # Returns the row of the highest price
                    max_price_vol = df.at[
                        index_max, "Usd Volume"
                    ]  # Returns the volume on the exchange that has the highest price
                    max_price_exchange = df.at[
                        index_max, "Name"
                    ]  # Returns the exchange with the highest price
            else:
                break
    print("Lowest Price:", min_price, "in:", (df.at[index_min, "Target"]))
    print("Highest Price:", max_price, "in:", (df.at[index_max, "Target"]))
    print("Row number with the lowest price:", index_min + 1)
    print("Row number with the highest price:", index_max + 1)
    print("Exchange with the lowest price:", min_price_exchange)
    print("Exchange with the highest price:", max_price_exchange)
    print("The Volume on exchange with the lowest price (USD):", min_price_vol)
    print("The Volume on exchange with the highest price (USD):", max_price_vol)
    percentage_profit = ((max_price - min_price) / min_price) * 100
    print(
        "Assuming Buy and Sell at the lowest and highest price:", percentage_profit, "%"
    )
    print("Lowest and highest prices are equal:", min_price_vol == max_price_vol)
    stats_df = (
        min_price,
        (df.at[index_min, "Target"]),
        max_price,
        df.at[index_max, "Target"],
        index_min + 1,
        index_max + 1,
        min_price_exchange,
        min_price_vol,
        max_price_exchange,
        max_price_vol,
        percentage_profit,
    )
    return percentage_profit, stats_df


def tableSelChange(*args):
    if tableSelBtn.get() == "Most Profitable Coin":
        print("Most Profitable Coin")
        pt.updateModel(TableModel(df))
        btn.pack(in_=frame_buttons, side="left")
    elif tableSelBtn.get() == "All Statistics":
        print("All Statistics")
        pt.updateModel(TableModel(stats_df))
        btn.forget()
    elif tableSelBtn.get() == "Expected Profits":
        print("Expected Profits")
        pt.updateModel(TableModel(expected_profit_df))
        btn.forget()
    pt.redraw()


# --- Determines the Best Coin with the Best Return ---
expected_profit_df, stats_df = profit_maximiser()
expected_profit_df.mask(
    expected_profit_df["Expected Profit"] >= profit_threshold, np.NaN, inplace=True
)
max_price_profit = expected_profit_df["Expected Profit"].max(skipna=True)
index = expected_profit_df["Expected Profit"].idxmax(skipna=True)
print(expected_profit_df)
print("Maximum price profit: ", max_price_profit, "%")  # print maximum profit %
coin_ticker = expected_profit_df.at[index, "Coin Ticker"]
print("For coin: ", coin_ticker)  # print coin ticker


# --- Gets the Current Market Data for the Coin with Best Return ---
tickers_data = call(coin_ticker)
df = format_columns(tickers_data, coin_ticker)
summary_statistics(df)
append(df, True)


# --- GUI ---
# creates a window called root
root = tk.Tk()

# creates a title for the window
root.title("Crypto Data Analysis")

# creates a frame and places it with the pack method
frame0 = tk.Frame(root)
frame0.pack(side="bottom", fill="x")

# sets starting state of button
tableSelBtn = tk.StringVar(frame0)
tableSelBtn.set("Table One")

# creates frame for buttons
frame_buttons = tk.Frame(frame0)
frame_buttons.pack(side="left", fill="x")

# button logic
tableSelMenu = tk.OptionMenu(
    frame_buttons,
    tableSelBtn,
    "Most Profitable Coin",
    "All Statistics",
    "Expected Profits",
)
btn = tk.Button(frame0, text="Update Prices", command=btn_update)
tableSelMenu.pack(in_=frame_buttons, side="left")
btn.pack(in_=frame0, side="left")

# creates a frame for the table and puts the data frame inside of it
frame1 = tk.LabelFrame(root, text="Data")
frame1.pack(fill="both", expand=True)
pt = Table(frame1, dataframe=df, showtoolbar=True, showstatusbar=True)
pt.show()

tableSelBtn.trace("w", tableSelChange)

root.mainloop()
