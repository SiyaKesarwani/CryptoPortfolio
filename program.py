from flask import Flask, request, jsonify
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
from aptos_sdk.async_client import RestClient as AptosClient
from solders.pubkey import Pubkey
# from pysui import AsyncClient as SuiClient
import asyncio
import json

# Solana, Sui, and Aptos configuration
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
APTOS_RPC = "https://aptos-mainnet.nodereal.io"
SUI_RPC = "https://sui-mainnet-endpoint.blockvision.org"

# Ethereum-compatible networks
ACCOUNT1_NETWORKS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "binance": "https://bsc-dataseed.binance.org/"
}

ACCOUNT2_NETWORKS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "base": "https://base-mainnet.g.alchemy.com/v2/tGa9jt4SO9YCrQ_rHBv1o76oBWoJW8Rr"
}

# Helper Functions
# def get_erc20_balance(node_url, wallet_address, token_address):
#     web3 = Web3(Web3.HTTPProvider(node_url))
#     contract = web3.eth.contract(
#         address=Web3.to_checksum_address(token_address),
#         abi=[
#             {"constant": True, "inputs": [], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
#         ],
#     )
#     balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
#     return web3.from_wei(balance, 'ether')

def get_eth_balance(node_url, wallet_address):  
    try:
        web3 = Web3(Web3.HTTPProvider(node_url))
        balance_wei = web3.eth.get_balance(wallet_address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
    except Exception as e:
        print(f"Error fetching balance: {e}")
    return balance_eth

def get_sol_balance(wallet_address):
    client = SolanaClient(SOLANA_RPC)
    result = client.get_balance(Pubkey.from_string(wallet_address))
    bal = result.value
    return bal

# def get_sui_balance(wallet_address):
#     client = SuiClient(SUI_RPC)
#     balance = client.get_account_balances(wallet_address)
#     print(balance)

# async def get_aptos_balance(wallet_address):
#     client = AptosClient(APTOS_RPC)
#     balances = await client.account_balance(wallet_address)
#     print(balances)
#     for resource in balances:
#         if "coin" in resource['type']:
#             return resource['data']['coin']['value']
#     print(balances) 

async def get_balances():
    eth_wallet_address_1 = "0x0076437A9385cDAd65FA6D6e80676e37F63AEF80"
    eth_wallet_address_2 = "0x0015e6E05487FE5369e9fBF60D10B566de31170c"
    sol_wallet_address = "DDWygtA7rmyjxFC5etGrw5jh7VUt58PWT2GXFawbvDGc"
    aptos_wallet_address = "0x6709e2de15a1e8d40adbcd812e6cad33e9c13f6582c738ef833e90981c1ceb31"
    sui_wallet_address = "0xffc23cf6e2e51f4cde3f69cdb72bd1877addf49757b28db59c01143f51ea6a3e"

    balances = {}
    for account in [ACCOUNT1_NETWORKS, ACCOUNT2_NETWORKS]:
        account_balances = {}
        wallet_address = eth_wallet_address_1
        for network in account:
            if(account == ACCOUNT2_NETWORKS):
                wallet_address = eth_wallet_address_2
            account_balances[network] = get_eth_balance(account[network], wallet_address)
        balances[wallet_address] = account_balances

    bal_solana = get_sol_balance(sol_wallet_address)
    balances[sol_wallet_address] = {"solana": bal_solana / 10 ** 9}

    # bal_aptos = await get_aptos_balance(aptos_wallet_address)
    # print(bal_aptos)
    # balances["aptos"] = bal_aptos
    # bal_sui = get_sui_balance(sui_wallet_address)
    print(balances)

loop = asyncio.get_event_loop()
loop.run_until_complete(get_balances())
loop.close()