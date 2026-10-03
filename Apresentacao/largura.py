from wcwidth import wcwidth, wcswidth

# Emojis ocupam 2 colunas no terminal, mas len() conta 1.
# Aqui tudo é medido em colunas visuais.

def largura_visual(texto):
    return max(wcswidth(texto), 0)

def centralizar(texto, largura):
    espaco = max(largura - largura_visual(texto), 0)
    esquerda = espaco // 2
    return " " * esquerda + texto + " " * (espaco - esquerda)

def para_colunas(texto):
    # Lista com uma posição por coluna da tela.
    # Caractere largo vira [caractere, ""] (o "" é a 2ª metade dele).
    colunas = []
    for c in texto:
        if wcwidth(c) == 0 and colunas:
            # Variation selector (ex: ⭐️ ⚠️) e afins grudam no anterior
            i = len(colunas) - 1
            while i > 0 and colunas[i] == "":
                i -= 1
            colunas[i] += c
            if largura_visual(colunas[i]) == 2 and (i == len(colunas) - 1):
                colunas.append("")
            continue
        colunas.append(c)
        if wcwidth(c) == 2:
            colunas.append("")
    return colunas

def recortar(colunas, inicio, largura):
    # Pega 'largura' colunas a partir de 'inicio' (circular),
    # trocando por espaço um emoji cortado ao meio nas bordas.
    total = len(colunas)
    janela = [colunas[(inicio + i) % total] for i in range(largura)]
    if janela and janela[0] == "":
        janela[0] = " "
    if janela and janela[-1] != "" and largura_visual(janela[-1]) == 2:
        janela[-1] = " "
    return "".join(janela)
