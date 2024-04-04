import ccxt  # noqa: E402
import json
import datetime
import pandas as pd
from web3.auto import Web3

import os
from dotenv import load_dotenv
load_dotenv()

apiKey = os.getenv('apiKey')
secret = os.getenv('secret')


class BinanceClient:
    def __init__(self) -> None:
        apiKey = os.getenv('apiKey')
        secret = os.getenv('secret')
        self.con = ccxt.binance({
            'apiKey': apiKey,
            'secret': secret,
            'options': {
                'defaultType': 'margin',  # spot, future, margin
            },
        })

    def fetch_balance(self):
        # remove 0 balances
        balance = self.con.fetch_balance()  # time consuming 7s
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

    def get_ohlc(self, symbol, timeframe):
        ohlcv = self.con.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(ohlcv).rename(
            {0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'}, axis=1)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'].dt.tz_localize(
            'UTC').dt.tz_convert('US/Eastern')  # convert to UTC to EST
        df['datetime'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df


class EthClient:
    """
    https://medium.com/coinmonks/discovering-the-secrets-of-an-ethereum-transaction-64febb00935c
    """
    def __init__(self) -> None:
        wss = "wss://patient-green-putty.quiknode.pro/c5a9ecc0ebed8eb70f75d3e7e8b3737e2fcabe06/"
        self.web3 = Web3(Web3.WebsocketProvider(wss))
        print(self.web3.is_connected())
        self._load_uniswapv3_router()

    def _load_uniswapv3_router(self):
        # Load Uniswap v3 SwapRouter address
        address = "0xE592427A0AEce92De3Edee1F18E0157C05861564" 
        self.uniswapv3_router_add = address = self.web3.to_checksum_address(address)
        # Load Uniswap v3 SwapRouter ABI
        with open('./abi/uniswapv3_router.json', 'r') as f:
            abi = json.load(f)
        self.uniswap_v3_router = self.web3.eth.contract(address=address, abi=abi)
        
    def get_pending_tx_uniswap(self):
        pending_block= self.web3.eth.get_block(block_identifier='pending', full_transactions=True)
        pending_transactions= pending_block['transactions']
        tx=[i for i in pending_transactions if i['to']==self.uniswapv3_router_add]
        if tx == []:
            return [], []
        results = []
        # Decode
        for t in tx:
            func_obj, func_params = self.uniswap_v3_router.decode_function_input(t["input"])
            func_params['timestamp'] = datetime.datetime.now().isoformat()
            results.append(func_params)
        return func_obj, results
        
    