from Infraestrutura.api import MAPA_COINGECKO

MAPA_LT = {
    "WETH": 0.825, "USDC": 0.78, "USDbC": 0.78, "cbBTC": 0.78,
    "wstETH": 0.825, "EURC": 0.80, "DAI": 0.0, "USDT": 0.0,
    "WBTC": 0.0, "WMATIC": 0.0, "AAVE": 0.0, "AERO": 0.0
}

RAY = 10 ** 27
SEGUNDOS_POR_ANO = 31536000

def ray_para_apy(taxa_ray):
    # A Aave guarda a taxa anual (APR) em "ray" (1e27); aqui vira APY com juros compostos por segundo
    apr = float(taxa_ray or 0) / RAY
    return (1 + apr / SEGUNDOS_POR_ANO) ** SEGUNDOS_POR_ANO - 1

def calcular_totais(reservas, precos):
    col_total = 0.0
    col_ajustado = 0.0
    div_total = 0.0
    ganho_anual = 0.0
    custo_anual = 0.0

    for item in reservas:
        simbolo = item['reserve']['symbol']
        dec = int(item['reserve']['decimals'])
        lt = MAPA_LT.get(simbolo, 0.0)
        usar_garantia = item.get('usageAsCollateralEnabledOnUser', False)

        saldo_c = float(item.get('currentATokenBalance', 0)) / (10 ** dec)
        saldo_d_variavel = float(item.get('currentVariableDebt', 0)) / (10 ** dec)
        saldo_d_estavel = float(item.get('currentStableDebt', 0)) / (10 ** dec)
        saldo_d = saldo_d_variavel + saldo_d_estavel

        apy_deposito = ray_para_apy(item['reserve'].get('liquidityRate'))
        apy_emp_variavel = ray_para_apy(item['reserve'].get('variableBorrowRate'))
        apy_emp_estavel = ray_para_apy(item['reserve'].get('stableBorrowRate'))

        id_cg = MAPA_COINGECKO.get(simbolo)
        preco = precos.get(id_cg, {}).get('usd', 0.0) if id_cg else 0.0

        if preco > 0:
            valor_c = saldo_c * preco
            valor_d = saldo_d * preco
            col_total += valor_c
            div_total += valor_d
            if usar_garantia:
                col_ajustado += (valor_c * lt)

            ganho_anual += valor_c * apy_deposito
            custo_anual += (saldo_d_variavel * apy_emp_variavel + saldo_d_estavel * apy_emp_estavel) * preco

    return col_total, col_ajustado, div_total, ganho_anual, custo_anual

def calcular_taxas_medias(ganho_anual, custo_anual, col_total, div_total):
    # Média ponderada pelo valor em dólar de cada ativo
    apy_sup = ganho_anual / col_total if col_total > 0 else None
    apy_emp = custo_anual / div_total if div_total > 0 else None
    return apy_sup, apy_emp

def calcular_apy_liquido(ganho_anual, custo_anual, col_total, div_total):
    # Mesma conta do "Net APY" do app da Aave: rendimento líquido / patrimônio líquido
    patrimonio = col_total - div_total
    if patrimonio <= 0:
        return None
    return (ganho_anual - custo_anual) / patrimonio

def calcular_hf(col_ajustado, div_total, hf_antigo):
    hf = col_ajustado / div_total

    seta = "-"
    if hf_antigo is not None:
        if hf - hf_antigo > 0.005: seta = "↑"
        elif hf_antigo - hf > 0.005: seta = "↓"

    return hf, seta
