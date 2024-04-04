from web3 import Web3
import json
import os

from dotenv import load_dotenv
load_dotenv()

abi_path = './abi.json'
wss_url = os.getenv('wss_url')

router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"  # Uniswap v3 SwapRouter

with open(abi_path) as f:
    abi = json.load(f)

interface = Web3().eth.contract(abi=abi)


def main():
    provider = Web3(Web3.WebsocketProvider(wss_url))
    provider.eth.subscribe('pending_transactions', handle_transaction)


def handle_transaction(tx_hash):
    txn_data = provider.eth.get_transaction(tx_hash)
    if txn_data:
        gas = txn_data['gasPrice']
        if txn_data['to'] == router_address and "0x414bf389" in txn_data['input']:
            print("hash: ", tx_hash)
            decoded = interface.decode_function_input(
                "exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))", txn_data['input'])
            log_txn(decoded, gas)


def log_txn(data, gas):
    print("tokenIn: ", data['params']['tokenIn'])
    print("tokenOut: ", data['params']['tokenOut'])
    print("amount: ", data['params']['amountOutMinimum'])
    print("gasPrice: ", gas)
    print("-------------")


main()
