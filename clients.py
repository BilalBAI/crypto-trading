import ccxt  # noqa: E402
import json

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
                'defaultType': 'margin', # spot, future, margin
            },
        })

    def fetch_balance(self):
        # remove 0 balances
        balance = self.con.fetch_balance() # time consuming 7s
        balance['info']['userAssets'] = [i for i in balance['info']['userAssets'] if i['netAsset']!= '0']
        for i in balance.keys():
            if  i not in ['info','timestamp', 'datetime']:
                balance[i]={i:balance[i][j] for j in balance[i].keys() if balance[i][j]!=0.0}
        self.balance = balance = {i:balance[i] for i in balance.keys() if balance[i]!={}}
        # output json
        with open('./data/balances.json', 'w') as f:
            json.dump(balance, f)
