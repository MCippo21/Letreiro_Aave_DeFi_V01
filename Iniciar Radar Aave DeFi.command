#!/bin/bash
# Dê dois cliques neste arquivo para abrir o Radar Aave no Terminal.

# Vai para a pasta onde este arquivo está (a raiz do projeto)
cd "$(dirname "$0")" || exit 1

# Título da janela do Terminal
printf '\033]0;Radar Aave\007'

pausar_e_sair() {
    echo
    read -r -p "Pressione Enter para fechar..."
    exit "${1:-1}"
}

# Usa o ambiente virtual se existir; senão, o python3 do sistema
if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
    PIP_EXTRA=""
else
    PY="python3"
    PIP_EXTRA="--user"
fi

if ! command -v "$PY" >/dev/null 2>&1; then
    echo "❌ Python 3 não encontrado. Instale em https://www.python.org/downloads/"
    pausar_e_sair
fi

# Arquivos de configuração que não vêm no repositório
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado."
    echo "   Copie o .env.exemplo para .env e coloque sua API_KEY do The Graph."
    pausar_e_sair
fi

if [ ! -f "Compartilhado/carteiras.py" ]; then
    echo "❌ Arquivo Compartilhado/carteiras.py não encontrado."
    echo "   Copie o Compartilhado/carteiras.exemplo.py para carteiras.py e coloque seus endereços."
    pausar_e_sair
fi

# Instala as dependências na primeira vez (ou se alguma estiver faltando)
if ! "$PY" -c "import requests, wcwidth, dotenv" >/dev/null 2>&1; then
    echo "📦 Instalando dependências (só na primeira vez)..."
    if ! "$PY" -m pip install $PIP_EXTRA -r requirements.txt; then
        echo "❌ Não foi possível instalar as dependências."
        pausar_e_sair
    fi
fi

# Roda o bot
"$PY" main.py
CODIGO=$?

# Se o bot fechou por erro, mantém a janela aberta para dar para ler a mensagem
if [ "$CODIGO" -ne 0 ]; then
    echo
    echo "⚠️  O Radar fechou com erro (código $CODIGO)."
    pausar_e_sair "$CODIGO"
fi
