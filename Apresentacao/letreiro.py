import os
import sys
import time
import shutil

from Apresentacao.cores import aplicar_cores
from Apresentacao.largura import para_colunas, recortar
from Compartilhado import estado

def animar_letreiro_multiplo(velocidade=0.15):
    indice = 0

    # Limpa a tela antes de começar
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" * 6) # Dá espaço para o bloco subir e descer

    while True:
        # Pega a largura do terminal AO VIVO a cada frame
        largura_tela = shutil.get_terminal_size().columns - 1

        # Trabalha em colunas da tela (emoji = 2 colunas), não em caracteres
        c1 = para_colunas(estado.linha1_global)
        c2 = para_colunas(estado.linha2_global)
        c3 = para_colunas(estado.linha3_global)
        c4 = para_colunas(estado.linha4_global)
        c5 = para_colunas(estado.linha5_global)

        disp1 = recortar(c1, indice, largura_tela)
        disp2 = recortar(c2, indice, largura_tela)
        disp3 = recortar(c3, indice, largura_tela)
        disp4 = recortar(c4, indice, largura_tela)
        disp5 = recortar(c5, indice, largura_tela)

        mapa_de_cores = estado.mapa_de_cores
        disp1_cor = aplicar_cores(disp1, mapa_de_cores)
        disp2_cor = aplicar_cores(disp2, mapa_de_cores)
        disp3_cor = aplicar_cores(disp3, mapa_de_cores)
        disp4_cor = aplicar_cores(disp4, mapa_de_cores)
        disp5_cor = aplicar_cores(disp5, mapa_de_cores)

        # \033[2K limpa a linha inteira, \r volta para o começo
        sys.stdout.write(f"\033[2K\r{disp1_cor}\n")
        sys.stdout.write(f"\033[2K\r{disp2_cor}\n")
        sys.stdout.write(f"\033[2K\r{disp3_cor}\n")
        sys.stdout.write(f"\033[2K\r{disp4_cor}\n")
        sys.stdout.write(f"\033[2K\r{disp5_cor}\n")

        # \033[5A move o cursor 5 linhas para cima
        sys.stdout.write("\033[5A")
        sys.stdout.flush()

        indice = (indice + 1) % len(para_colunas(estado.linha1_global))
        time.sleep(velocidade)
