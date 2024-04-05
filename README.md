# crypto-trading

## Build Python
```bash
conda create -n crypto-trading python=3.12 pip wheel
conda activate crypto-trading
pip install -r requirements.txt
pip install python-dotenv

```
### Build js
```bash
mkdir filtering-mempool-txns
cd filtering-mempool-txns
npm init -y
npm install ethers npm --cache /tmp/empty-cache # npm install ethers
echo > index.js && echo > abi.json
node index.js
```
# Create .env file
```bash
apiKey='{apiKey}'
secret='{secret}'
wss='{wss}'
```
