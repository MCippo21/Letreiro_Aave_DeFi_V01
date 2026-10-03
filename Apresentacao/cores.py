
VERDE = '\033[92m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
AZUL = '\033[96m' # Ciano para os nomes
RESET = '\033[0m'

def aplicar_cores(texto, mapa):
    colorido = texto
    for cru, cor in mapa.items():
        colorido = colorido.replace(cru, cor)
    return colorido