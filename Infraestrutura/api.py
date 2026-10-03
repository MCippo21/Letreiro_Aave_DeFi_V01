import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

THE_GRAPH_URL = 'https://gateway.thegraph.com/api/subgraphs/id/GQFbb95cE6d8mV989mL5figjaGaKCQB3xqYrr1bRyXqF'
API_KEY = os.getenv('API_KEY')

MAPA_COINGECKO = {
    "WETH": "ethereum", "USDC": "usd-coin", "USDbC": "usd-coin",
    "DAI": "dai", "USDT": "tether", "WBTC": "wrapped-bitcoin", 
    "cbBTC": "coinbase-wrapped-btc", "wstETH": "wrapped-steth", 
    "EURC": "euro-coin", "WMATIC": "matic-network", "AAVE": "aave"
}

def obter_precos_coingecko():
    ids = ",".join(MAPA_COINGECKO.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    try:
        return requests.get(url, timeout=10).json()
    except Exception:
        return {}

def buscar_reservas(enderecos):
    query_graphql = """
    query {
        users(where: {id_in: %s}) {
            id
            reserves {
                currentATokenBalance
                currentVariableDebt
                currentStableDebt
                usageAsCollateralEnabledOnUser
                reserve {
                    symbol
                    decimals
                    liquidityRate
                    variableBorrowRate
                    stableBorrowRate
                }
            }
        }
    }
    """ % json.dumps(enderecos)

    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    resposta = requests.post(THE_GRAPH_URL, json={'query': query_graphql}, headers=headers)
    return resposta.json()
