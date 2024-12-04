from flask import Flask, request, jsonify
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
from aptos_sdk.async_client import RestClient as AptosClient
# from pysui import SuiConfig
# from pysui import AsyncClient as SuiClient
import requests

app = Flask(__name__)

# Ethereum-compatible networks
NETWORKS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "binance": "https://bsc-dataseed.binance.org/",
    "base": "https://base-mainnet.g.alchemy.com/v2/tGa9jt4SO9YCrQ_rHBv1o76oBWoJW8Rr",
    "solana": "https://solana-mainnet.g.alchemy.com/v2/_PmB1kSGOTiFY5nbo-F1YxoJPSeJffRe",
    "aptos": "https://aptos-mainnet.nodereal.io",
    "sui": "https://sui-mainnet-endpoint.blockvision.org"
}

# Solana, Sui, and Aptos configuration
SOLANA_RPC = "https://solana-mainnet.g.alchemy.com/v2/_PmB1kSGOTiFY5nbo-F1YxoJPSeJffRe"
APTOS_RPC = "https://aptos-mainnet.nodereal.io"
SUI_RPC = "https://sui-mainnet-endpoint.blockvision.org"

# Helper Functions
def get_erc20_balance(network, wallet_address, token_address):
    web3 = Web3(Web3.HTTPProvider(NETWORKS[network]))
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=[
            {"constant": True, "inputs": [], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
        ],
    )
    balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    return web3.from_wei(balance, 'ether')

def get_eth_balance(wallet_address):  
    try:
        web3 = Web3(Web3.HTTPProvider(NETWORKS["ethereum"]))
        balance_wei = web3.eth.get_balance(wallet_address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
    except Exception as e:
        print(f"Error fetching balance: {e}")
    return balance_eth

def get_sol_balance(wallet_address):
    client = SolanaClient(NETWORKS["solana"])
    result = client.get_balance(pubkey=wallet_address)
    return result['result']['value'] / 10**9  # Convert lamports to SOL

# def get_sui_balance(wallet_address):
#     client = SuiClient(SUI_RPC)
#     balance = client.get_account_balances(wallet_address)
#     return balance

def get_aptos_balance(wallet_address):
    client = AptosClient(APTOS_RPC)
    balances = client.account_resources(wallet_address)
    print(balances)
    # for resource in balances:
    #     if "coin" in resource['type']:
    #         return resource['data']['coin']['value']
    return balances

# API Endpoint
@app.route("/get_balances", methods=["GET"])
def get_balances():
    # data = request.json
    eth_wallet_address_1 = "0x0076437A9385cDAd65FA6D6e80676e37F63AEF80"
    sol_wallet_address = "DDWygtA7rmyjxFC5etGrw5jh7VUt58PWT2GXFawbvDGc"
    aptos_wallet_address = "0x6709e2de15a1e8d40adbcd812e6cad33e9c13f6582c738ef833e90981c1ceb31"
    balances = {}
    bal_ethereum = get_eth_balance(eth_wallet_address_1)
    balances["ethereum"] = bal_ethereum
    # bal_solana = get_sol_balance(sol_wallet_address)
    # balances["solana"] = bal_solana
    bal_aptos = get_aptos_balance(aptos_wallet_address)
    print(bal_aptos)
    # balances["aptos"] = bal_aptos
    return jsonify(balances)

if __name__ == "__main__":
    app.run(debug=True)
