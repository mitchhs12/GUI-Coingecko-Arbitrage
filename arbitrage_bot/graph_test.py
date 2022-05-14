from datetime import datetime, timedelta
import pandas as pd
import pandas_datareader as pdr
import plotly.graph_objects as go

CRYPTO = "LINK"
CURRENCY = "USD"


def getData(cryptocurrency):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    last_year_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")

    start = pd.to_datetime(last_year_date)
    end = pd.to_datetime(current_date)

    data = pdr.get_data_yahoo(f"{cryptocurrency}-{CURRENCY}", start, end)

    return data


if __name__ == "__main__":
    crypto_data = getData(CRYPTO)

    # Candlestick
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=crypto_data.index,
                open=crypto_data.Open,
                high=crypto_data.High,
                low=crypto_data.Low,
                close=crypto_data.Close,
            ),
            go.Scatter(
                x=crypto_data.index,
                y=crypto_data.Close.rolling(window=20).mean(),
                mode="lines",
                name="20SMA",
                line={"color": "#ff006a"},
            ),
            go.Scatter(
                x=crypto_data.index,
                y=crypto_data.Close.rolling(window=50).mean(),
                mode="lines",
                name="50SMA",
                line={"color": "#1900ff"},
            ),
        ]
    )
fig.update_layout(
    title=f"The Candlestick graph for {CRYPTO}",
    xaxis_title="Date",
    yaxis_title=f"Price ({CURRENCY})",
    xaxis_rangeslider_visible=False,
)
fig.update_yaxes(tickprefix="$")

fig.show()
