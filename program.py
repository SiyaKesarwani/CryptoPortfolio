from flask import Flask, request, jsonify
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
from aptos_sdk.async_client import RestClient as AptosClient
from solders.pubkey import Pubkey
# from pysui import AsyncClient as SuiClient
import asyncio
import json
from tabulate import tabulate

# Solana, Sui, and Aptos configuration
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
APTOS_RPC = "https://aptos-mainnet.nodereal.io"
SUI_RPC = "https://sui-mainnet-endpoint.blockvision.org"

NETWORK_TOKEN_SYMBOLS = {
    "ethereum": "ETHEREUM",
    "arbitrum": "ARBITRUM",
    "binance": "BSC",
    "base": "BASE"
}

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
def get_erc20_balance(node_url, wallet_address, token_address):
    web3 = Web3(Web3.HTTPProvider(node_url))
    erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function",
            },
        ]
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=erc20_abi
    )
    # Fetch the token decimals
    decimals = contract.functions.decimals().call()
    balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    return balance / (10 ** decimals)

def get_eth_balance(node_url, wallet_address):  
    try:
        web3 = Web3(Web3.HTTPProvider(node_url))
        balance_wei = web3.eth.get_balance(wallet_address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
        return balance_eth
    except Exception as e:
        print(f"Error fetching balance: {e}")

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
    ARB_token_addresses = {
        "KIMA": "0x94fCD9c18f99538C0f7C61c5500cA79F0D5C4dab",
        "AAVE": "0xba5DdD1f9d7F570dc94a51479a000E3BCE967196",
        "GRT": "0x9623063377AD1B27544C965cCd7342f7EA7e88C7",
        "LINK": "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
        "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
        "UNI": "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0",
        "LDO": "0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60",
        "WBTC": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
    } 
    BSC_token_addresses = {
        "TRX": "0x85EAC5Ac2F758618dFa09bDbe0cf174e7d574D5B",
        "EGO": "0x44a21B3577924DCD2e9C81A3347D204C36a55466",
        "BEAM": "0x62D0A8458eD7719FDAF978fe5929C6D342B0bFcE",
        "BONK": "0xA697e272a73744b343528C3Bc4702F2565b2F422",
        "FET": "0x031b41e504677879370e9DBcF937283A8691Fa7f",
        "PEPE": "0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
        "TONCOIN": "0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
        "AAVE": "0xfb6115445Bff7b52FeB98650C87f44907E58f802",
        "BCH": "0x8fF795a6F4D97E7887C79beA79aba5cc76444aDf",
        "DOT": "0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402",
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        "MATIC": "0xCC42724C6683B7E57334c4E856f4c9965ED682bD",
        "NEAR": "0x1Fa4a73a3F0133f0025378af00236f3aBDEE5D63",
        "SHIB": "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
        "XRP": "0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
        "ADA": "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47"
    } 
    BASE_token_addresses = {
        "BRETT" : "0x532f27101965dd16442E59d40670FaF5eBB142E4",
        "AERO" : "0x940181a94A35A4569E4529A3CDfB74e38FD98631",
        "CHAMP" : "0xEb6d78148F001F3aA2f588997c5E102E489Ad341"
    }

    balances = {}

    # To fetch balance of network tokens
    for account_network in [ACCOUNT1_NETWORKS, ACCOUNT2_NETWORKS]:
        account_balances = {}
        wallet_address = eth_wallet_address_1
        for network in account_network:
            if(account_network == ACCOUNT2_NETWORKS):
                wallet_address = eth_wallet_address_2
            account_balances[NETWORK_TOKEN_SYMBOLS[network]] = {'network' : network, 'balance' : get_eth_balance(account_network[network], wallet_address)}
            if(network == "arbitrum"):
                for symbol, token_address in ARB_token_addresses.items():
                    account_balances[symbol] = {'network' : network, 'balance' : get_erc20_balance(account_network[network], wallet_address, token_address)}
            if(network == "binance"):
                for symbol, token_address in BSC_token_addresses.items():
                    account_balances[symbol] = {'network' : network, 'balance' : get_erc20_balance(account_network[network], wallet_address, token_address)}
            if(network == "base"):
                for symbol, token_address in BASE_token_addresses.items():
                    account_balances[symbol] = {'network' : network, 'balance' : get_erc20_balance(account_network[network], wallet_address, token_address)}
        balances[wallet_address] = account_balances

    bal_solana = get_sol_balance(sol_wallet_address)
    balances[sol_wallet_address] = {"SOL": {'network' : 'solana', 'balance' :bal_solana / 10 ** 9}}

    # bal_aptos = await get_aptos_balance(aptos_wallet_address)
    # bal_sui = get_sui_balance(sui_wallet_address)

    # print(balances)
    table_data = []

    for wallet, symbols in balances.items():
        for network, details in symbols.items():
            table_data.append([
                wallet,       # Wallet Address
                network,      # Network Name
                details['network'],  # Token Name
                float(details['balance'])  # Balance
            ])

    # Define table headers
    headers = ["Wallet Address", "Token Symbol", "Network", "Balance"]

    # Print table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


loop = asyncio.get_event_loop()
loop.run_until_complete(get_balances())
loop.close()