import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Recupera a API Key do CoinMarketCap
API_KEY = os.getenv('CMC_API_KEY')

# Mapeamento de símbolos CoinMarketCap → CoinGecko
CMC_TO_COINGECKO = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
    "BNB": "binancecoin",
    "SOL": "solana",
    "USDC": "usd-coin",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "TRX": "tron",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "XLM": "stellar",
    "AVAX": "avalanche-2",
    "SUI": "sui",
    "HBAR": "hedera-hashgraph",
    "SHIB": "shiba-inu",
    "LEO": "leo-token",
    "TON": "the-open-network",
    "HYPE": "hype",
    "DOT": "polkadot",
    "OM": "mantra",
    "BCH": "bitcoin-cash",
    "USDE": "ethena-usde",
    "BGB": "bitget-token",
    "UNI": "uniswap",
    "DAI": "dai",
    "XMR": "monero",
    "PEPE": "pepe",
    "AAVE": "aave",
    "ONDO": "ondo-finance",
    "APT": "aptos",
    "NEAR": "near",
    "MNT": "mantle",
    "TAO": "bittensor",
    "TRUMP": "maga",
    "ICP": "internet-computer",
    "ETC": "ethereum-classic",
    "OKB": "okb",
    "KAS": "kaspa",
    "POL": "polygon-ecosystem-token",
    "VET": "vechain",
    "CRO": "crypto-com-chain",
    "ALGO": "algorand",
    "RENDER": "render-token",
    "S": "s",
    "FIL": "filecoin",
    "ARB": "arbitrum",
    "FDUSD": "first-digital-usd",
    "GT": "gatechain-token",
    "JUP": "jupiter-exchange",
    "OP": "optimism",
    "ATOM": "cosmos",
    "FET": "fetch-ai",
    "TIA": "celestia",
    "DEXE": "dexe",
    "LDO": "lido-dao",
    "INJ": "injective-protocol",
    "KCS": "kucoin-shares",
    "XDC": "xdce-crowd-sale",
    "STX": "stacks",
    "IMX": "immutable-x",
    "GRT": "the-graph",
    "THETA": "theta-token",
    "ENA": "ethena",
    "RAY": "raydium",
    "BONK": "bonk",
    "FLR": "flare-networks",
    "MOVE": "move-network",
    "WLD": "worldcoin",
    "QNT": "quant-network",
    "JASMY": "jasmycoin",
    "SEI": "sei-network",
    "MKR": "maker",
    "EOS": "eos",
    "FLOKI": "floki-inu",
    "ENS": "ethereum-name-service",
    "XTZ": "tezos",
    "SAND": "the-sandbox",
    "NEXO": "nexo",
    "BTT": "bittorrent",
    "GALA": "gala",
    "FLOW": "flow",
    "IOTA": "iota",
    "KAIA": "kairos",
    "JTO": "jito",
    "RON": "ronin",
    "NEO": "neo",
    "BSV": "bitcoin-sv",
    "PYTH": "pyth-network",
    "XAUT": "tether-gold",
    "BERA": "bera",
    "CAKE": "pancakeswap-token",
    "IP": "ipor",
    "XCN": "chain",
    "AXS": "axie-infinity",
    "PYUSD": "paypal-usd",
    "CRV": "curve-dao-token",
    "MELANIA": "melania-trump",
    "FTT": "ftx-token",
    "HNT": "helium",
    "VIRTUAL": "virtual",
    "MANA": "decentraland",
    "WIF": "dogwifhat",
    "EGLD": "elrond",
    "PAXG": "pax-gold",
    "AR": "arweave",
    "SPX": "spx",
    "STRK": "starknet",
    "MATIC": "matic-network",
    "ZEC": "zcash",
    "AERO": "aerodrome-finance",
    "DYDX": "dydx",
    "CFX": "conflux-token",
    "PENDLE": "pendle",
    "AIOZ": "aioz-network",
    "XEC": "ecash",
    "APE": "apecoin",
    "CHZ": "chiliz",
    "PENGU": "penguin-finance",
    "CORE": "core",
    "MORPHO": "morpho",
    "KAVA": "kava",
    "TUSD": "trueusd",
    "COMP": "compound-governance-token",
    "BEAM": "beam",
    "W": "wormhole",
    "GNO": "gnosis",
    "RSR": "reserve-rights-token",
    "AXL": "axelar",
    "NFT": "nft",
    "AMP": "amp",
    "AKT": "akash-network",
    "TWT": "trust-wallet-token",
    "DEEP": "deep",
    "GRASS": "grass",
    "MINA": "mina-protocol",
    "RUNE": "thorchain",
    "LUNC": "terra-classic",
    "EIGEN": "eigenlayer",
    "ZK": "zkspace",
    "BRETT": "brett",
    "1INCH": "1inch",
    "QTUM": "qtum",
    "AI16Z": "ai16z",
    "WEMIX": "wemix",
    "JST": "just",
    "TFUEL": "theta-fuel",
    "BNX": "binaryx",
    "CTC": "creditcoin",
    "SUPER": "superfarm",
    "SNX": "synthetix-network-token",
    "ZRO": "zero",
    "SFP": "safepal",
    "MX": "mxc",
    "DASH": "dash",
    "KSM": "kusama",
    "FARTCOIN": "fartcoin",
    "SAFE": "safe",
    "ASTR": "astar",
    "BLUR": "blur",
    "ACH": "alchemy-pay",
    "VTHO": "vechainthor-energy",
    "NOT": "notcoin",
    "ROSE": "oasis-network",
    "GLM": "golem",
    "CKB": "nervos-network",
    "MOG": "mog-coin",
    "ZIL": "zilliqa",
    "HOT": "holo",
    "LPT": "livepeer",
    "ID": "space-id",
    "BABYDOGE": "baby-doge-coin",
    "ZRX": "0x",
    "ORDI": "ordi",
    "BAT": "basic-attention-token",
    "TOSHI": "toshi",
    "SATS": "sats",
    "ETHFI": "ethereum-finance",
    "GAS": "gas",
    "MEW": "mew",
    "CELO": "celo",
    "TRAC": "origintrail",
    "MOCA": "monacoin",
    "ATH": "ath",
    "ZKJ": "zkj",
    "SC": "siacoin",
    "SUSHI": "sushi",
    "CVX": "convex-finance",
    "ANKR": "ankr",
    "POPCAT": "popcat",
    "OSMO": "osmosis",
    "TURBO": "turbo",
    "DCR": "decred",
    "WOO": "woo-network",
    "MASK": "mask-network",
    "XYO": "xyo-network",
    "T": "threshold",
    "ENJ": "enjincoin",
    "ONE": "harmony"
}

CMC_TO_BINANCE = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "XRP": "XRPUSDT",
    "BNB": "BNBUSDT",
    "SOL": "SOLUSDT",
    "USDC": "USDCUSDT",
    "DOGE": "DOGEUSDT",
    "ADA": "ADAUSDT",
    "TRX": "TRXUSDT",
    "LINK": "LINKUSDT",
    "LTC": "LTCUSDT",
    "XLM": "XLMUSDT",
    "AVAX": "AVAXUSDT",
    "SUI": "SUIUSDT",
    "HBAR": "HBARUSDT",
    "SHIB": "SHIBUSDT",
    # "LEO": "LEOUSDT",
    # "TON": "TONUSDT",
    # "HYPE": "HYPEUSDT",
    "DOT": "DOTUSDT",
    "OM": "OMUSDT",
    "BCH": "BCHUSDT",
    # "USDE": "USDEUSDT",
    # "BGB": "BGBUSDT",
    "UNI": "UNIUSDT",
    # "DAI": "DAIUSDT",
    # "XMR": "XMRUSDT",
    "PEPE": "PEPEUSDT",
    "AAVE": "AAVEUSDT",
    # "ONDO": "ONDOUSDT",
    "APT": "APTUSDT",
    "NEAR": "NEARUSDT",
    # "MNT": "MNTUSDT",
    "TAO": "TAOUSDT",
    # "TRUMP": "TRUMPUSDT",
    "ICP": "ICPUSDT",
    "ETC": "ETCUSDT",
    # "OKB": "OKBUSDT",
    # "KAS": "KASUSDT",
    # "POL": "POLUSDT",
    "VET": "VETUSDT",
    # "CRO": "CROUSDT",
    "ALGO": "ALGOUSDT",
    "RENDER": "RENDERUSDT",
    "FIL": "FILUSDT",
    "ARB": "ARBUSDT",
    "FDUSD": "FDUSDUSDT",
    # "GT": "GTUSDT",
    "JUP": "JUPUSDT",
    "OP": "OPUSDT",
    "ATOM": "ATOMUSDT",
    "FET": "FETUSDT",
    "TIA": "TIAUSDT",
    "DEXE": "DEXEUSDT",
    "LDO": "LDOUSDT",
    "INJ": "INJUSDT",
    "KCS": "KCSUSDT",
    "XDC": "XDCUSDT",
    "STX": "STXUSDT",
    "IMX": "IMXUSDT",
    "GRT": "GRTUSDT",
    "THETA": "THETAUSDT",
    "ENA": "ENAUSDT",
    "RAY": "RAYUSDT",
    "BONK": "BONKUSDT",
    "FLR": "FLRUSDT",
    "MOVE": "MOVEUSDT",
    "WLD": "WLDUSDT",
    "QNT": "QNTUSDT",
    "JASMY": "JASMYUSDT",
    "SEI": "SEIUSDT",
    "MKR": "MKRUSDT",
    "EOS": "EOSUSDT",
    "FLOKI": "FLOKIUSDT",
    "ENS": "ENSUSDT",
    "XTZ": "XTZUSDT",
    "SAND": "SANDUSDT",
    "NEXO": "NEXOUSDT",
    "BTT": "BTTUSDT",
    "GALA": "GALAUSDT",
    "FLOW": "FLOWUSDT",
    "IOTA": "IOTAUSDT",
    "KAIA": "KAIAUSDT",
    "JTO": "JTOUSDT",
    "RON": "RONUSDT",
    "NEO": "NEOUSDT",
    "BSV": "BSVUSDT",
    "PYTH": "PYTHUSDT",
    "XAUT": "XAUTUSDT",
    "BERA": "BERAUSDT",
    "CAKE": "CAKEUSDT",
    "IP": "IPUSDT",
    "XCN": "XCNUSDT",
    "AXS": "AXSUSDT",
    "PYUSD": "PYUSDUSDT",
    "CRV": "CRVUSDT",
    "MELANIA": "MELANIAUSDT",
    "FTT": "FTTUSDT",
    "HNT": "HNTUSDT",
    "VIRTUAL": "VIRTUALUSDT",
    "MANA": "MANAUSDT",
    "WIF": "WIFUSDT",
    "EGLD": "EGLDUSDT",
    "PAXG": "PAXGUSDT",
    "AR": "ARUSDT",
    "SPX": "SPXUSDT",
    "STRK": "STRKUSDT",
    "MATIC": "MATICUSDT",
    "ZEC": "ZECUSDT",
    "AERO": "AEROUSDT",
    "DYDX": "DYDXUSDT",
    "CFX": "CFXUSDT",
    "PENDLE": "PENDLEUSDT",
    "AIOZ": "AIOZUSDT",
    "XEC": "XECUSDT",
    "APE": "APEUSDT",
    "CHZ": "CHZUSDT",
    "PENGU": "PENGUUSDT",
    "CORE": "COREUSDT",
    "MORPHO": "MORPHOUSDT",
    "KAVA": "KAVAUSDT",
    "TUSD": "TUSDUSDT",
    "COMP": "COMPUSDT",
    "BEAM": "BEAMUSDT",
    "W": "WUSDT",
    "GNO": "GNOUSDT",
    "RSR": "RSRUSDT",
    "AXL": "AXLUSDT",
    "NFT": "NFTUSDT",
    "AMP": "AMPUSDT",
    "AKT": "AKTUSDT",
    "TWT": "TWTUSDT",
    "DEEP": "DEEPUSDT",
    "GRASS": "GRASSUSDT",
    "MINA": "MINAUSDT",
    "RUNE": "RUNEUSDT",
    "LUNC": "LUNCUSDT",
    "EIGEN": "EIGENUSDT",
    "ZK": "ZKUSDT",
    "BRETT": "BRETTUSDT",
    "1INCH": "1INCHUSDT",
    "QTUM": "QTUMUSDT",
    "AI16Z": "AI16ZUSDT",
    "WEMIX": "WEMIXUSDT",
    "JST": "JSTUSDT",
    "TFUEL": "TFUELUSDT",
    "BNX": "BNXUSDT",
    "CTC": "CTCUSDT",
    "SUPER": "SUPERUSDT",
    "SNX": "SNXUSDT",
    "ZRO": "ZROUSDT",
    "SFP": "SFPUSDT",
    "MX": "MXUSDT",
    "DASH": "DASHUSDT",
    "KSM": "KSMUSDT",
    "FARTCOIN": "FARTCOINUSDT",
    "SAFE": "SAFEUSDT",
    "ASTR": "ASTRUSDT",
    "BLUR": "BLURUSDT",
    "ACH": "ACHUSDT",
    "VTHO": "VTHOUSDT",
    "NOT": "NOTUSDT",
    "ROSE": "ROSEUSDT",
    "GLM": "GLMUSDT",
    "CKB": "CKBUSDT",
    "MOG": "MOGUSDT",
    "ZIL": "ZILUSDT",
    "HOT": "HOTUSDT",
    "LPT": "LPTUSDT",
    "ID": "IDUSDT",
    "BABYDOGE": "BABYDOGEUSDT",
    "ZRX": "ZRXUSDT",
    "ORDI": "ORDIUSDT",
    "BAT": "BATUSDT",
    "TOSHI": "TOSHIUSDT",
    "SATS": "SATSUSDT",
    "ETHFI": "ETHFIUSDT",
    "GAS": "GASUSDT",
    "MEW": "MEWUSDT",
    "CELO": "CELOUSDT",
    "ANKR": "ANKRUSDT",
}


# Função para obter as 30 moedas principais com base no market cap
def get_top_50_coins():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        "X-CMC_PRO_API_KEY": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "start": 1,
        "limit": 50,
        "convert": "USD",
        "sort": "market_cap",
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        symbols = [coin["symbol"].upper() for coin in data["data"]]

        binance_symbols = [f"{CMC_TO_BINANCE[symbol]}" for symbol in symbols if symbol in CMC_TO_BINANCE]
        coingecko_symbols = [CMC_TO_COINGECKO.get(symbol, symbol.lower()) for symbol in symbols]

        return {
            "binance": binance_symbols,
            "coingecko": coingecko_symbols
        }
    else:
        print(f"Error: {response.status_code}")
        return {"binance": [], "coingecko": []}

# top_30_coins = get_top_30_coins()
# print(top_30_coins)