import re
import sqlite3
import unicodedata
from datetime import datetime
from pathlib import Path

# Arquivo do banco fica na raiz do projeto
CAMINHO_BANCO = Path(__file__).resolve().parent.parent / "historico_carteiras.db"

def nome_sem_emoji(nome_carteira):
    # "⭐️ Carteira Principal" -> "Carteira Principal"
    texto = "".join(c for c in nome_carteira if not unicodedata.category(c).startswith("S")
                    and unicodedata.category(c) != "Mn")
    return " ".join(texto.split())

def nome_da_tabela(nome_carteira):
    # "⭐️ Carteira Principal" -> "carteira_principal" (sem emoji, acento ou pontuação)
    texto = unicodedata.normalize("NFKD", nome_carteira).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return texto or "carteira"

def conectar():
    return sqlite3.connect(CAMINHO_BANCO)

def criar_tabelas(carteiras):
    with conectar() as conexao:
        for nome, endereco in carteiras.items():
            conexao.execute(f"""
                CREATE TABLE IF NOT EXISTS {nome_da_tabela(nome)} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    endereco TEXT NOT NULL,
                    nome_carteira TEXT,
                    colateral_usd REAL,
                    divida_usd REAL,
                    apy_sup REAL,
                    apy_emp REAL,
                    apy_liquido REAL,
                    hf REAL
                )
            """)

def salvar_registros(registros):
    # registros: lista de dicts com as chaves usadas abaixo; taxas em %, hf None = sem dívida
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conectar() as conexao:
        for r in registros:
            conexao.execute(f"""
                INSERT INTO {nome_da_tabela(r['nome'])}
                        (data_hora, endereco, nome_carteira, colateral_usd, 
                        divida_usd, apy_sup, apy_emp, apy_liquido, hf)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               """, (data_hora, r['endereco'], nome_sem_emoji(r['nome']), r['colateral_usd'],
                         r['divida_usd'], r['apy_sup'], r['apy_emp'], r['apy_liquido'], r['hf']))

