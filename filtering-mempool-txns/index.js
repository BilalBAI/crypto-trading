const ethers = require("ethers");
const fs = require("fs");
const abi = require('./abi.json');

const wssUrl = "wss://patient-green-putty.quiknode.pro/c5a9ecc0ebed8eb70f75d3e7e8b3737e2fcabe06/";
const router = "0xE592427A0AEce92De3Edee1F18E0157C05861564"; //Uniswap v3 SwapRouter

const interface = new ethers.Interface(abi);

async function main() {
    const provider = new ethers.WebSocketProvider(wssUrl);
    provider.on('pending', async (tx) => {
        const txnData = await provider.getTransaction(tx);
        if (txnData) {
            let gas = txnData['gasPrice'];
            if (txnData.to == router && txnData['data'].includes("0x414bf389")) {
                console.log("hash: ", txnData['hash']);
                let decoded = interface.decodeFunctionData("exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))", txnData['data']);
                logTxn(decoded, gas);
                saveToJson(decoded, gas);
            }
        }
    })
}

async function logTxn(data, gas) {
    console.log("tokenIn: ", data['params']['tokenIn']);
    console.log("tokenOut: ", data['params']['tokenOut']);
    console.log("amount: ", data['params']['amountOutMinimum'].toString());
    console.log("gasPrice: ", gas.toString());
    console.log("-------------");
}

function saveToJson(decoded, gas) {
    const currentTime = new Date().toISOString().replace(/:/g, '-');
    const filename = `decoded_${currentTime}.json`;

    // Convert BigInt values to strings
    const decodedAsString = convertBigIntToString(decoded);
    const gasAsString = gas.toString();

    const data = { decoded: decodedAsString, gas: gasAsString };

    fs.writeFile(filename, JSON.stringify(data, null, 2), (err) => {
        if (err) {
            console.error("Error writing JSON file:", err);
        } else {
            console.log(`Data saved to ${filename}`);
        }
    });
}

// Function to recursively convert BigInt values to strings
function convertBigIntToString(obj) {
    if (typeof obj === 'bigint') {
        return obj.toString();
    } else if (Array.isArray(obj)) {
        return obj.map(convertBigIntToString);
    } else if (typeof obj === 'object' && obj !== null) {
        return Object.fromEntries(
            Object.entries(obj).map(([key, value]) => [key, convertBigIntToString(value)])
        );
    }
    return obj;
}

main();