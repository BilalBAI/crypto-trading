import ccxt  # noqa: E402
import json
import datetime
import pandas as pd
from web3.auto import Web3

import os
from dotenv import load_dotenv
load_dotenv()

BINANCE_API_KEY = os.getenv('apiKey')
BINANCE_API_SECRET = os.getenv('secret')
WSS = os.getenv('wss')


class BinanceClient:
    def __init__(self) -> None:
        self.con = ccxt.binance()  # General con without account api key, for price fetching etc
        self.risk_whitelist = ['USDT']

    # login a binance account for trading. use with cautious
    def con_trading_login(self):
        apiKey = os.getenv('apiKey')
        secret = os.getenv('secret')
        self.con_trading = ccxt.binance({
            'apiKey': apiKey,
            'secret': secret,
            'options': {
                'defaultType': 'margin',  # spot, future, margin
            },
        })  # connect to a binance margin account for trading

    def fetch_balance(self):
        # remove 0 balances
        balance = self.con_trading.fetch_balance()  # time consuming 7s
        balance['info']['userAssets'] = [
            i for i in balance['info']['userAssets'] if i['netAsset'] != '0']
        for i in balance.keys():
            if i not in ['info', 'timestamp', 'datetime']:
                balance[i] = {i: balance[i][j]
                              for j in balance[i].keys() if balance[i][j] != 0.0}
        self.balance = balance = {i: balance[i]
                                  for i in balance.keys() if balance[i] != {}}
        # output json
        with open('./data/balances.json', 'w') as f:
            json.dump(balance, f)
        self.positions = pd.DataFrame(balance['info']['userAssets']).rename(
            columns={'asset': 'symbol', 'netAsset': 'delta'})
        self.positions.delta = self.positions.delta.astype(float)

    def get_ohlcv(self, symbol, timeframe, since=None, limit=None):
        ohlcv = self.con.fetch_ohlcv(
            symbol, timeframe, since=since, limit=limit)
        df = pd.DataFrame(ohlcv).rename(
            {0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, axis=1)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'].dt.tz_localize(
            'UTC').dt.tz_convert('US/Eastern')  # convert to UTC to EST
        df['datetime'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df

    def rms(self, positions, total_invest):
        df = pd.DataFrame(positions)
        df['price'] = df.apply(lambda row: self.con.fetch_ticker(
            f'{row['symbol']}/USDT')['last'] if row['symbol'] != 'USDT' else 1, axis=1)
        df['mv'] = df['delta'] * df['price']
        risk_whitelist = self.risk_whitelist
        self.df_risk_exp = df_risk_exp = df.loc[~df.symbol.isin(
            risk_whitelist)]
        self.df_cash = df_cash = df.loc[df.symbol.isin(risk_whitelist)]
        # Terminal output
        print(f"GMV: {df_risk_exp.mv.abs().sum():,.2f}")
        print(f"NMV: {df_risk_exp.mv.sum():,.2f}")

        print()
        long = df.loc[df.mv > 0, 'mv'].sum()
        short = df.loc[df.mv < 0, 'mv'].sum()
        print(f"Total Balance: {long:,.2f}")
        print(f"Total Liability: {short:,.2f}")
        print(f"Net Liq: {long+short:,.2f}")
        print(f"PNL: {long+short-total_invest:,.2f}")
        print(f"ML: {long/abs(short):,.2f}")


class EthClient:
    """
    https://medium.com/coinmonks/discovering-the-secrets-of-an-ethereum-transaction-64febb00935c
    """

    def __init__(self) -> None:
        wss = os.getenv('wss')
        self.web3 = Web3(Web3.WebsocketProvider(wss))
        print(self.web3.is_connected())
        self._load_uniswapv3_router()

    def _load_uniswapv3_router(self):
        # Load Uniswap v3 SwapRouter address
        address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        self.uniswapv3_router_add = address = self.web3.to_checksum_address(
            address)
        # Load Uniswap v3 SwapRouter ABI
        with open('./abi/uniswapv3_router.json', 'r') as f:
            abi = json.load(f)
        self.uniswap_v3_router = self.web3.eth.contract(
            address=address, abi=abi)

    def get_pending_tx_uniswap(self):
        pending_block = self.web3.eth.get_block(
            block_identifier='pending', full_transactions=True)
        pending_transactions = pending_block['transactions']
        tx = [i for i in pending_transactions if i['to']
              == self.uniswapv3_router_add]
        if tx == []:
            return [], []
        results = []
        # Decode
        for t in tx:
            func_obj, func_params = self.uniswap_v3_router.decode_function_input(
                t["input"])
            func_params['timestamp'] = datetime.datetime.now().isoformat()
            results.append(func_params)
        return func_obj, results
