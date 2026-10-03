import os
import sys
import threading

from CasosDeUso.montar_letreiro import buscar_dados_e_montar_letreiro
from Apresentacao.letreiro import animar_letreiro_multiplo

# Ativa códigos ANSI no Windows
os.system('')

if __name__ == "__main__":
    t = threading.Thread(target=buscar_dados_e_montar_letreiro, daemon=True)
    t.start()
    try:
        animar_letreiro_multiplo(velocidade=0.25)
    except KeyboardInterrupt:
        sys.stdout.write("\n\n\n\n\n\n")
        print("Radar encerrado.")
