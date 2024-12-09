from requests.auth import to_native_string
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
from solders.pubkey import Pubkey
import asyncio
from tabulate import tabulate
import aiohttp
from datetime import datetime
import requests
from decimal import Decimal
import csv
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# Your CoinMarketCap API key
API_KEY = os.getenv('COINMARKETCAP_APIKEY')
# CoinMarketCap API endpoint
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# Solana, Sui, and Aptos configuration
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
APTOS_RPC = "https://aptos-mainnet.nodereal.io"
SUI_RPC = "https://rpc.mainnet.sui.io"

# Add any network token symbol, iff any network balance is needed to be fetched
NETWORK_TOKEN_SYMBOLS = {
    "ethereum": "ETH",
    "arbitrum": "ETH_ARB",
    "binance": "BNB",
    "base": "ETH_BASE",
    "polygon": "POL",
    "avalanche": "AVAX"
}

# Add any new network to any of the accounts
ACCOUNT1_NETWORKS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "arbitrum": "https://arb-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "binance": "https://bsc-dataseed.binance.org/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "avalanche": "https://avax-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y"
}
ACCOUNT2_NETWORKS = {
    "ethereum": "https://eth-mainnet.g.alchemy.com/v2/UrggOgGebZS0QmIEHRa1Kvg521x9Uy2Y",
    "base": "https://base-mainnet.g.alchemy.com/v2/tGa9jt4SO9YCrQ_rHBv1o76oBWoJW8Rr"
}

# Give path and column name of csv file
FILE_PATH = 'Investments.csv' 
COLUMN_NAME = 'Ticker' 

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
    return [balance, 10**decimals]

def get_eth_balance(node_url, wallet_address):  
    try:
        web3 = Web3(Web3.HTTPProvider(node_url))
        balance_wei = web3.eth.get_balance(wallet_address)
        return balance_wei
    except Exception as e:
        print(f"Error fetching balance: {e}")

def get_sol_balance(wallet_address):
    client = SolanaClient(SOLANA_RPC)
    result = client.get_balance(Pubkey.from_string(wallet_address))
    bal = result.value
    return bal

# async def fetch_price(session, symbol):
#     """Fetch the price of a single cryptocurrency symbol."""
#     headers = {
#         "Accepts": "application/json",
#         "X-CMC_PRO_API_KEY": API_KEY,
#     }
#     params = {"symbol": symbol}
    
#     try:
#         async with session.get(COINMARKETCAP_URL, headers=headers, params=params) as response:
#             data = await response.json()
#             if response.status == 200:
#                 price = data["data"][symbol]["quote"]["USD"]["price"]
#                 print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {symbol}: ${price:,.2f}")
#             else:
#                 print(f"Error fetching {symbol}: {data.get('status', {}).get('error_message', 'Unknown error')}")
#     except Exception as e:
#         print(f"Exception while fetching {symbol}: {e}")

# async def fetch_prices_periodically():
#     """Fetch cryptocurrency prices every 10 seconds."""
#     async with aiohttp.ClientSession() as session:
#         while True:
#             tasks = [fetch_price(session, symbol) for symbol in SYMBOLS]
#             await asyncio.gather(*tasks)
#             await asyncio.sleep(10)

def fetch_prices(symbols):
    """Fetch cryptocurrency prices from CoinMarketCap."""
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "symbol": ",".join(symbols),
        "convert": "USD"
    }

    prices = {}
    
    try:
        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
        data = response.json()
        if response.status_code == 200:
            for symbol in symbols:
                price = data["data"][symbol]["quote"]["USD"]["price"]
                prices[symbol] = Decimal(price)
        else:
            print("Error:", data.get("status", {}).get("error_message", "Unknown error"))
    except Exception as e:
        print(f"Exception occurred: {e}")
    return prices

def find_row_details(search_value):
    try:
        with open(FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            found = False
            # print(f"Rows containing '{search_value}' in column '{COLUMN_NAME}':")
            # print("-" * 50)
            for row in reader:
                if row[COLUMN_NAME] == search_value:
                    found = True
                    return(row)
            
            if not found:
                print(f"No rows found with '{search_value}' in column '{COLUMN_NAME}'.")
    except FileNotFoundError:
        print(f"Error: The file '{FILE_PATH}' was not found.")
    except KeyError:
        print(f"Error: The column '{COLUMN_NAME}' does not exist in the file.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_balances():
    eth_wallet_address_1 = "0x0076437A9385cDAd65FA6D6e80676e37F63AEF80"
    eth_wallet_address_2 = "0x0015e6E05487FE5369e9fBF60D10B566de31170c"
    sol_wallet_address = "DDWygtA7rmyjxFC5etGrw5jh7VUt58PWT2GXFawbvDGc"
    aptos_wallet_address = "0x6709e2de15a1e8d40adbcd812e6cad33e9c13f6582c738ef833e90981c1ceb31"
    sui_wallet_address = "0xffc23cf6e2e51f4cde3f69cdb72bd1877addf49757b28db59c01143f51ea6a3e"
    ARB_token_addresses = {
        "KIMA": "0x94fCD9c18f99538C0f7C61c5500cA79F0D5C4dab",
        # "AAVE": "0xba5DdD1f9d7F570dc94a51479a000E3BCE967196", # Removed investment
        "GRT": "0x9623063377AD1B27544C965cCd7342f7EA7e88C7",
        "LINK": "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",
        "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
        "UNI": "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0",
        "LDO": "0x13Ad51ed4F1B7e9Dc168d8a00cB3f4dDD85EfA60",
        "WBTC": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
    } 
    BNB_token_addresses = {
        "AGI": "0x818835503f55283cd51a4399f595e295a9338753",
        "TRX": "0x85EAC5Ac2F758618dFa09bDbe0cf174e7d574D5B",
        "EGO": "0x44a21B3577924DCD2e9C81A3347D204C36a55466",
        "BEAM": "0x62D0A8458eD7719FDAF978fe5929C6D342B0bFcE",
        "BONK": "0xA697e272a73744b343528C3Bc4702F2565b2F422",
        "FET": "0x031b41e504677879370e9DBcF937283A8691Fa7f",
        "PEPE": "0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
        "TON": "0x76A797A59Ba2C17726896976B7B3747BfD1d220f",
        "AAVE": "0xfb6115445Bff7b52FeB98650C87f44907E58f802",
        "BCH": "0x8fF795a6F4D97E7887C79beA79aba5cc76444aDf",
        "DOT": "0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402",
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        # "MATIC": "0xCC42724C6683B7E57334c4E856f4c9965ED682bD", # Removed investment
        "NEAR": "0x1Fa4a73a3F0133f0025378af00236f3aBDEE5D63",
        "SHIB": "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
        "XRP": "0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
        "ADA": "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47"
    } 
    BASE_token_addresses = {
        "BRETT" : "0x532f27101965dd16442E59d40670FaF5eBB142E4",
        "AERO" : "0x940181a94A35A4569E4529A3CDfB74e38FD98631",
        "CHAMP" : "0xEb6d78148F001F3aA2f588997c5E102E489Ad341",
        "PRIME" : "0xfa980ced6895ac314e7de34ef1bfae90a5add21b",
        "MORPHO" : "0xBAa5CC21fd487B8Fcc2F632f3F4E8D37262a0842"
    }
    POLYGON_token_addresses = {
        "RENDER" : "0x61299774020da444af134c82fa83e3810b309991", # NOT AVAILABLE ON COINMARKETCAP
        "OM" : "0xc3ec80343d2bae2f8e680fdadde7c17e71e114ea",
    }
    AVALANCHE_token_addresses = {
        "COQ" : "0x420fca0121dc28039145009570975747295f2329",
    }

    # If network tokens are added add it here as well
    NETWORK_TOKEN_MAPPING = {
        "arbitrum": ARB_token_addresses,
        "binance": BNB_token_addresses,
        "base": BASE_token_addresses,
        "polygon": POLYGON_token_addresses,
        "avalanche": AVALANCHE_token_addresses
    }

    balances = {}
    unique_symbols = []

    # To fetch balance of network tokens
    for account_network in [ACCOUNT1_NETWORKS, ACCOUNT2_NETWORKS]:
        account_balances = {}
        wallet_address = eth_wallet_address_1
        for network in account_network:
            if(account_network == ACCOUNT2_NETWORKS):
                wallet_address = eth_wallet_address_2

            # For network balances    
            account_balances[NETWORK_TOKEN_SYMBOLS[network]] = {'network' : network, 'balance' : get_eth_balance(account_network[network], wallet_address), 'decimal' : 10**18}

            # For tokens of network balances
            if network in NETWORK_TOKEN_MAPPING:
                # Add unique symbols
                if network == "arbitrum" or network == "base":
                    unique_symbols.append("ETH")
                else:
                    unique_symbols.append(NETWORK_TOKEN_SYMBOLS[network])
                
                # Now fetch tokens of network
                token_addresses = NETWORK_TOKEN_MAPPING[network]
                for symbol, token_address in token_addresses.items():
                    if symbol not in unique_symbols:
                        unique_symbols.append(symbol)
                    [bal, decimal] = get_erc20_balance(account_network[network], wallet_address, token_address)
                    account_balances[symbol] = {'network' : network, 'balance' : bal, 'decimal' : decimal}
        balances[wallet_address] = account_balances

    bal_solana = get_sol_balance(sol_wallet_address)
    balances[sol_wallet_address] = {"SOL": {'network' : 'solana', 'balance' : bal_solana, 'decimal' : 10**9}}
    unique_symbols.append("SOL")

    #fetch prices of all tokens
    prices = fetch_prices(unique_symbols)

    for v in balances.values():
        nested_keys_list = list(v.keys())
        for symbol in nested_keys_list:

            if symbol in prices.keys():
                v[symbol].update({'price' : prices[symbol]})
            elif symbol == "ETH_ARB" or symbol == "ETH_BASE":
                v[symbol].update({'price' : prices["ETH"]})
            
            if(symbol == "WBTC"):
                row_details = find_row_details("BTC")
            elif(symbol == "ETH_ARB"):
                row_details = find_row_details("ETH")
            else:
                row_details = find_row_details(symbol) # here key is symbol

            if(isinstance(row_details, dict)):
                v[symbol].update({'investedAmount' : int(row_details['Amount'])})
                if(symbol == "ETH"):
                        v[symbol].update({'investedAmount' : 0})
            else:
                v[symbol].update({'investedAmount' : 0})

    table_data = []
    total_invested_value = 0
    row_no = 1
    total_current_value = 0
    total_pnl = 0

    for wallet, symbols in balances.items():
        for network, details in symbols.items():
            invested_value = details['investedAmount']
            current_value = round((details['price'] * details['balance']) / details['decimal'], 10)
            pnl = round((details['price'] * details['balance']) / details['decimal'], 10) - details['investedAmount']
            percentage = 100
            invested_times_current = 0
            if invested_value != 0:
                percentage = round((pnl / invested_value) * 100, 2)
                invested_times_current = round(current_value / invested_value, 2)
            table_data.append([
                row_no,    # Wallet Address
                network,      # Network Name
                details['network'],  # Token Name
                round(details['price'], 10), # Token Price
                invested_value, # Invested value
                current_value, # Total current value
                pnl, # Total PNL
                str(percentage) + " %",
                str(invested_times_current) + " x"
            ])
            row_no += 1
            total_invested_value += invested_value
            total_current_value += current_value
            total_pnl += pnl

    table_data.append(["Total Value----", "", "", "", total_invested_value, total_current_value, total_pnl, str(round((total_pnl / total_invested_value) * 100, 2)) + " %", str(round(total_current_value / total_invested_value, 2)) + " x"])

    # Define table headers
    headers = ["S.No.", "Token Symbol", "Network", "Price (USD)", "Invested Value (USD)", "Current Value (USD)", "CML. PNL (USD)", "Percentage I/D", "Invested Times Current"]

    # Print table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    get_balances()