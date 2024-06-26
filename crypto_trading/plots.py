from crypto_trading.clients import BinanceClient
import plotly.graph_objects as go


def plot_chart(symbol, timeframe, limit=None):
    binance = BinanceClient()
    df = binance.get_ohlcv(symbol, timeframe, limit=limit)
    fig = go.Figure(data=[go.Candlestick(x=df['datetime'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])
    fig.update_layout(title=f'{symbol}_{timeframe}_{
                      limit}', xaxis_rangeslider_visible=False)
    fig.show()


def style(s, style):
    return style + s + '\033[0m'


def green(s):
    return style(s, '\033[92m')


def blue(s):
    return style(s, '\033[94m')


def yellow(s):
    return style(s, '\033[93m')


def red(s):
    return style(s, '\033[91m')


def pink(s):
    return style(s, '\033[95m')


def bold(s):
    return style(s, '\033[1m')


def underline(s):
    return style(s, '\033[4m')


def dump(*args):
    print(' '.join([str(arg) for arg in args]))

# dump(green(balance['info']['totalAssetOfBtc']), 'balance', balance)
