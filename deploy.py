import json
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import dotenv_values

config = dotenv_values(".env")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

NETWORK = {
    "M": "MAIN",
    "L": "GANACHE",
    "T": "RINKEBY",
}

network = NETWORK[input("Use Main(M), Test(T) or Local(L): ").upper()]
# compiling the solidity code
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file, indent=4)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# w3 = Web3(Web3.HTTPProvider(os.getenv("GOERLI_RPC_URL")))
# chain_id = 4

# For connecting to ganache
w3 = Web3(Web3.HTTPProvider(config[f"{network}_RPC_CODE"]))
chain_id = int(config[f"{network}_CHAIN_ID"])
my_address = config[f"{network}_ADDRESS"]
private_key = config[f"{network}_PRIVATE_KEY"]
# Create the contract in Python
SimpleStorage = w3.eth.contract(
    abi=abi,
    bytecode=compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"],
)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# Wait for the transaction to be mined, and get the transaction receipt
# # Send it!
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")


# Working with deployed Contracts
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
greeting_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=private_key
)
tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
print("Updating stored Value...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)

print(simple_storage.functions.retrieve().call())
