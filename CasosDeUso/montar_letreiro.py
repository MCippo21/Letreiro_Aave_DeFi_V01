import time

from Compartilhado import estado
from Compartilhado.carteiras import CARTEIRAS
from Infraestrutura.api import obter_precos_coingecko, buscar_reservas
from Dominio.regras import calcular_totais, calcular_hf, calcular_apy_liquido, calcular_taxas_medias
from Apresentacao.cores import VERDE, AMARELO, VERMELHO, AZUL, RESET
from Apresentacao.largura import largura_visual, centralizar
from Repositorio.banco import criar_tabelas, salvar_registros

def formatar_taxa(taxa):
    return "--" if taxa is None else f"{taxa * 100:.2f}%"

def em_porcentagem(taxa):
    return None if taxa is None else round(taxa * 100, 4)

def buscar_dados_e_montar_letreiro():
    enderecos_formatados = [endereco.lower() for endereco in CARTEIRAS.values()]
    criar_tabelas(CARTEIRAS)

    while True:
        try:
            precos = obter_precos_coingecko()
            dados = buscar_reservas(enderecos_formatados)

            if 'errors' in dados:
                estado.linha1_global = f" Erro no Graph: {dados['errors'][0]['message'][:50]} "
                estado.linha2_global = " "
                estado.linha3_global = " "
                estado.linha4_global = " "
                estado.linha5_global = " "
                time.sleep(30)
                continue

            novas_cores = {}
            registros = []
            blocos_l1, blocos_l2, blocos_l3, blocos_l4, blocos_l5 = [], [], [], [], []

            usuarios_api = dados.get('data', {}).get('users', [])
            dados_por_carteira = {user['id']: user['reserves'] for user in usuarios_api}

            for nome, endereco in CARTEIRAS.items():
                end_lower = endereco.lower()
                reservas = dados_por_carteira.get(end_lower, [])

                if not reservas:
                    str1 = f" {nome} "
                    str2 = " Sem Posição "
                    str3 = " "
                    str4 = " "
                    str5 = " "
                else:
                    col_total, col_ajustado, div_total, ganho_anual, custo_anual = calcular_totais(reservas, precos)

                    str1 = f" {nome} "
                    str2 = f" Col: ${col_total:.2f} | Emp: ${div_total:.2f} "

                    apy_sup, apy_emp = calcular_taxas_medias(ganho_anual, custo_anual, col_total, div_total)
                    str3 = f" Sup: {formatar_taxa(apy_sup)} | Emp: {formatar_taxa(apy_emp)} "

                    apy = calcular_apy_liquido(ganho_anual, custo_anual, col_total, div_total)
                    if apy is None:
                        str4 = " APY: -- "
                    else:
                        str4 = f" APY: {apy * 100:.2f}% "
                        cor_apy = VERDE if apy >= 0 else VERMELHO
                        novas_cores[str4] = f" APY: {cor_apy}{apy * 100:.2f}%{RESET} "

                    hf = None
                    if div_total < 0.01:
                        str5 = " HF: Seguro (Sem Dívida) "
                    else:
                        hf, seta = calcular_hf(col_ajustado, div_total, estado.historico_hf.get(end_lower))
                        estado.historico_hf[end_lower] = hf

                        cor_hf = VERDE if hf >= 1.5 else AMARELO if hf >= 1.1 else VERMELHO
                        alerta = " ⚠️ RISCO " if hf < 1.1 else ""

                        str5 = f" HF: {hf:.2f} {seta}{alerta} "

                        # Mapeia a string crua para a versão colorida
                        novas_cores[str5] = f" HF: {cor_hf}{hf:.2f}{RESET} {seta}{VERMELHO}{alerta}{RESET} "

                    registros.append({
                        'nome': nome,
                        'endereco': end_lower,
                        'colateral_usd': round(col_total, 2),
                        'divida_usd': round(div_total, 2),
                        'apy_sup': em_porcentagem(apy_sup),
                        'apy_emp': em_porcentagem(apy_emp),
                        'apy_liquido': em_porcentagem(apy),
                        'hf': None if hf is None else round(hf, 4),
                    })

                # Destaca o nome da carteira
                novas_cores[str1] = f"{AZUL}{str1}{RESET}"

                # Calcula o tamanho perfeito do retângulo do letreiro
                largura_maxima = max(largura_visual(s) for s in (str1, str2, str3, str4, str5)) + 4

                blocos_l1.append(centralizar(str1, largura_maxima))
                blocos_l2.append(centralizar(str2, largura_maxima))
                blocos_l3.append(centralizar(str3, largura_maxima))
                blocos_l4.append(centralizar(str4, largura_maxima))
                blocos_l5.append(centralizar(str5, largura_maxima))

            # Junta todos os blocos com um separador visual
            separador = "  ||  "
            estado.linha1_global = separador.join(blocos_l1) + separador
            estado.linha2_global = separador.join(blocos_l2) + separador
            estado.linha3_global = separador.join(blocos_l3) + separador
            estado.linha4_global = separador.join(blocos_l4) + separador
            estado.linha5_global = separador.join(blocos_l5) + separador
            estado.mapa_de_cores = novas_cores

            # Salva um registro por carteira na tabela dela
            salvar_registros(registros)

        except Exception as e:
            estado.linha1_global = f" Erro: {str(e)[:40]} "
            estado.linha2_global = " "
            estado.linha3_global = " "
            estado.linha4_global = " "
            estado.linha5_global = " "

        time.sleep(60)
