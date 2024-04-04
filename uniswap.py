from web3.auto import Web3
# https://ethereum.stackexchange.com/questions/155869/getting-uniswap-v2-latest-price-and-interpreting-values-using-python
# Initialize Web3
wss = "wss://patient-green-putty.quiknode.pro/c5a9ecc0ebed8eb70f75d3e7e8b3737e2fcabe06/"
w3 = Web3(Web3.WebsocketProvider(wss))
# Pair contract address
pair_address = "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852"  # WETH/USDT in this example
pair_address = w3.to_checksum_address(pair_address)

# Minimal ABI for Uniswap V2 Pair contract, only including methods used
pair_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"},
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

# Minimal ABI for ERC20 token contract, only including methods used
erc20_token_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

# Initialize pair contract
pair_contract = w3.eth.contract(address=pair_address, abi=pair_abi)

# Fetch reserves
reserves = pair_contract.functions.getReserves().call()
reserve0 = reserves[0]
reserve1 = reserves[1]

# Fetch token addresses from the pair contract
token0_address = pair_contract.functions.token0().call()
token1_address = pair_contract.functions.token1().call()

# Initialize tokens contracts
token0_contract = w3.eth.contract(address=token0_address, abi=erc20_token_abi)
token1_contract = w3.eth.contract(address=token1_address, abi=erc20_token_abi)

# Fetch name and symbol for each token
name0 = token0_contract.functions.name().call()
symbol0 = token0_contract.functions.symbol().call()
name1 = token1_contract.functions.name().call()
symbol1 = token1_contract.functions.symbol().call()

# Fetch decimals for each token
decimals0 = token0_contract.functions.decimals().call()
decimals1 = token1_contract.functions.decimals().call()

# Adjust reserves for decimals
adjusted_reserve0 = reserve0 / (10**decimals0)
adjusted_reserve1 = reserve1 / (10**decimals1)

# Calculate adjusted price for Token0 in terms of Token1
if adjusted_reserve1 > 0:
    price0_in_terms_of_1 = adjusted_reserve0 / adjusted_reserve1
else:
    price0_in_terms_of_1 = "Infinite or Undefined"

# Calculate adjusted price for Token1 in terms of Token0
if adjusted_reserve0 > 0:
    price1_in_terms_of_0 = adjusted_reserve1 / adjusted_reserve0
else:
    price1_in_terms_of_0 = "Infinite or Undefined"

print(f"Price of 1 {name0} ({symbol0}) in {name1} ({symbol1}): {price1_in_terms_of_0}")
print(f"Price of 1 {name1} ({symbol1}) in {name0} ({symbol0}): {price0_in_terms_of_1}")