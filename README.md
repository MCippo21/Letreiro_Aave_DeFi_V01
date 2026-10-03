# Radar Aave: letreiro de posições no terminal

Bot em Python que monitora posições na **Aave V3** de várias carteiras ao mesmo tempo. Ele mostra, num **letreiro animado no terminal**, o colateral, a dívida, as taxas, o APY líquido e o **Health Factor (HF)** de cada carteira. A cada atualização, ele também **salva um histórico em SQLite**, com uma tabela por carteira.

```
      ⭐️ Carteira Principal         ||     📈 Carteira Investimentos     ||       💳 Carteira Pagamentos
   Col: $1000.00 | Emp: $400.00     ||     Col: $500.00 | Emp: $0.00     ||     Col: $250.00 | Emp: $200.00
     Sup: 3.50% | Emp: 5.00%        ||       Sup: 2.00% | Emp: --        ||       Sup: 1.00% | Emp: 6.00%
            APY: 2.50%              ||            APY: 2.00%             ||            APY: -19.00%
            HF: 1.85 ↑              ||      HF: Seguro (Sem Dívida)      ||         HF: 1.05 ↓ ⚠️ RISCO
```

O texto rola da direita para a esquerda sem parar, e os valores são atualizados a cada 60 segundos.

---

## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Instalação passo a passo](#2-instalação-passo-a-passo)
3. [Configuração](#3-configuração)
4. [Rodando o bot](#4-rodando-o-bot)
5. [Entendendo o letreiro](#5-entendendo-o-letreiro)
6. [Como os números são calculados](#6-como-os-números-são-calculados)
7. [Histórico no banco de dados (SQLite)](#7-histórico-no-banco-de-dados-sqlite)
8. [Como o programa funciona por dentro](#8-como-o-programa-funciona-por-dentro)
9. [Estrutura de pastas](#9-estrutura-de-pastas)
10. [Personalizando](#10-personalizando)
11. [Solução de problemas](#11-solução-de-problemas)
12. [Limitações conhecidas](#12-limitações-conhecidas)
13. [Segurança](#13-segurança)
14. [Licença](#14-licença)

---

## 1. Pré-requisitos

| O quê | Por quê | Como conferir |
|---|---|---|
| **Python 3.9 ou mais novo** | O bot é escrito em Python | `python3 --version` |
| **pip** | Para instalar as bibliotecas | `python3 -m pip --version` |
| **Git** (opcional) | Para clonar o repositório | `git --version` |
| **Chave de API do The Graph** | Para buscar as posições na Aave | Veja o [passo 3.1](#31-chave-da-api-do-the-graph-env) |
| **Terminal com suporte a cores e emoji** | Para desenhar o letreiro | Terminal do macOS, iTerm2, terminal do VS Code, Windows Terminal |

> No Windows, use `python` no lugar de `python3` em todos os comandos abaixo, caso `python3` não exista.

---

## 2. Instalação passo a passo

### 2.1. Baixe o projeto

Com Git:
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

Sem Git: no GitHub, clique em **Code → Download ZIP**, extraia o arquivo e abra um terminal **dentro da pasta extraída**.

> Todos os comandos daqui em diante devem ser rodados **na raiz do projeto**, a pasta onde está o `main.py`.

### 2.2. (Recomendado) Crie um ambiente virtual

O ambiente virtual isola as bibliotecas deste projeto das do resto do computador.

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Quando o ambiente estiver ativo, o terminal mostra `(.venv)` no começo da linha. Você precisa ativá-lo **toda vez** que abrir um terminal novo para rodar o bot.

### 2.3. Instale as dependências

```bash
pip install -r requirements.txt
```

Bibliotecas que serão instaladas:

| Biblioteca | Para que serve aqui |
|---|---|
| `requests` | Fazer as chamadas HTTP ao The Graph e ao CoinGecko |
| `wcwidth` | Medir quantas colunas cada caractere ocupa na tela (emojis ocupam 2) |
| `python-dotenv` | Ler a chave da API do arquivo `.env` |

---

## 3. Configuração

Dois arquivos com dados pessoais **não vêm no repositório**. Você precisa criá-los a partir dos exemplos.

### 3.1. Chave da API do The Graph (`.env`)

**a) Consiga uma chave:**
1. Acesse <https://thegraph.com/studio/> e entre com sua carteira ou e-mail.
2. Vá em **API Keys** e clique em **Create API Key**.
3. Copie a chave gerada.

O plano gratuito tem uma cota mensal de consultas. O bot faz cerca de **1 consulta por minuto**, ou seja, uns 43 mil por mês.

**b) Crie o arquivo `.env` a partir do exemplo:**

macOS / Linux:
```bash
cp .env.exemplo .env
```
Windows:
```powershell
copy .env.exemplo .env
```

**c) Abra o `.env` e cole a sua chave:**
```
API_KEY=sua_chave_aqui
```
Não use aspas nem espaços em volta do `=`.

### 3.2. Suas carteiras (`Compartilhado/carteiras.py`)

**a) Crie o arquivo a partir do exemplo:**

macOS / Linux:
```bash
cp Compartilhado/carteiras.exemplo.py Compartilhado/carteiras.py
```
Windows:
```powershell
copy Compartilhado\carteiras.exemplo.py Compartilhado\carteiras.py
```

**b) Edite o `Compartilhado/carteiras.py`** com os seus nomes e endereços:
```python
CARTEIRAS = {
    "⭐️ Carteira Principal": "0xSEU_ENDERECO_1",
    "📈 Carteira Investimentos": "0xSEU_ENDERECO_2",
}
```

Regras:
- **Chave** (à esquerda): o nome que aparece no letreiro. Pode ter emoji.
- **Valor** (à direita): o endereço da carteira na rede do subgraph configurado. Maiúsculas e minúsculas tanto faz.
- A **ordem** do dicionário é a ordem em que as carteiras aparecem no letreiro.
- O nome também define o **nome da tabela no banco**. Se você renomear uma carteira, uma tabela nova será criada (veja a [seção 7](#7-histórico-no-banco-de-dados-sqlite)).

---

## 4. Rodando o bot

Há duas formas de abrir o bot. Nas duas, o resultado é o mesmo.

### 4.1. Com dois cliques (macOS)

Na raiz do projeto existe o arquivo **`Iniciar Radar Aave.command`**. Dê **dois cliques** nele pelo Finder: o Terminal abre e o bot começa a rodar.

Ao abrir, o arquivo faz sozinho, nesta ordem:
1. Vai para a pasta do projeto, de qualquer lugar onde você abrir.
2. Escolhe o Python: usa o `.venv` se ele existir; senão, usa o `python3` do sistema.
3. Confere se o `.env` e o `Compartilhado/carteiras.py` existem. Se faltar algum, mostra o que fazer e não inicia o bot.
4. Confere as bibliotecas. **Na primeira vez**, se faltar alguma, instala o `requirements.txt` automaticamente.
5. Roda o `main.py`.
6. Se o bot fechar por erro, a janela continua aberta para você ler a mensagem. Aperte Enter para fechar.

> Com o executável, o [passo 2.3](#23-instale-as-dependências) é opcional: ele instala as dependências sozinho. A [configuração (passo 3)](#3-configuração) continua obrigatória.

**Primeira vez abrindo:**
- Se o macOS mostrar *"não pode ser aberto porque é de um desenvolvedor não identificado"*, clique com o **botão direito → Abrir → Abrir**. Só é preciso fazer isso uma vez.
- Se você baixou o projeto em **ZIP** e nada acontece no clique (ou aparece um aviso de permissão), dê permissão de execução ao arquivo. Na raiz do projeto, rode:
  ```bash
  chmod +x "Iniciar Radar Aave.command"
  ```
  Quem clonou com `git clone` não precisa disso.

**Atalhos úteis:**
- Arraste o arquivo para o **Dock** para abrir com um clique.
- Para um atalho na Mesa, arraste o arquivo segurando `Cmd + Option`. Isso cria um atalho, sem mover o original.

> No Windows e no Linux, o `.command` não funciona com dois cliques. Use a [forma 4.2](#42-pelo-terminal).

### 4.2. Pelo terminal

Na raiz do projeto, com o ambiente virtual ativo (se você criou um):

```bash
python3 main.py
```

> **Importante:** sempre rode a partir da raiz, com `python3 main.py`. Se você entrar numa subpasta e rodar algum arquivo de lá, os imports (`from Dominio...`) quebram. O executável da forma 4.1 já cuida disso.

### 4.3. O que acontece depois de abrir

1. A tela é limpa e aparece `Carregando dados...`.
2. Em poucos segundos, a primeira busca termina e as carteiras começam a rolar.
3. A cada **60 segundos** os dados são atualizados e um novo registro é salvo no banco.

**Para parar:** aperte `Ctrl + C`. Vai aparecer `Radar encerrado.`. Se abriu pelo executável, depois feche a janela do Terminal.

> Depois de alterar qualquer arquivo `.py`, **pare e abra o bot de novo**. O código só é carregado quando o programa inicia.

---

## 5. Entendendo o letreiro

Cada carteira ocupa um bloco de **5 linhas**. Os blocos são separados por `||`.

| Linha | Exemplo | Significado |
|---|---|---|
| 1 | `⭐️ Carteira Principal` | Nome da carteira (em ciano) |
| 2 | `Col: $1000.00 \| Emp: $400.00` | **Col**: total depositado (colateral) em USD. **Emp**: total da dívida em USD |
| 3 | `Sup: 3.50% \| Emp: 5.00%` | **Sup**: rendimento médio dos depósitos. **Emp**: juros médios dos empréstimos |
| 4 | `APY: 2.50%` | **APY líquido**: quanto a carteira rende (ou custa) por ano sobre o patrimônio líquido |
| 5 | `HF: 1.85 ↑` | **Health Factor**, com a seta de tendência |

### Cores e símbolos

**APY (linha 4)**
- 🟢 Verde: APY positivo (o depósito rende mais do que a dívida custa).
- 🔴 Vermelho: APY negativo (os juros da dívida custam mais do que o depósito rende).

**Health Factor (linha 5)**

| HF | Cor | Situação |
|---|---|---|
| ≥ 1.5 | 🟢 Verde | Confortável |
| entre 1.1 e 1.5 | 🟡 Amarelo | Atenção |
| < 1.1 | 🔴 Vermelho + `⚠️ RISCO` | Perto da liquidação (a Aave liquida com HF < 1.0) |

**Seta de tendência do HF**, comparada com a atualização anterior:
- `↑`: o HF subiu mais de 0.005
- `↓`: o HF caiu mais de 0.005
- `-`: estável, ou é a primeira leitura desde que o bot foi aberto

### Mensagens especiais

| Mensagem | Quando aparece |
|---|---|
| `Carregando dados...` | Logo ao abrir, antes da primeira busca terminar |
| `Sem Posição` | A carteira não tem nada na Aave |
| `HF: Seguro (Sem Dívida)` | Dívida menor que $0.01 |
| `--` | Não há como calcular a taxa (por exemplo, sem dívida não existe taxa média de empréstimo) |
| `Erro no Graph: ...` | O The Graph respondeu com erro (chave inválida, cota esgotada...). Tenta de novo em 30 s |
| `Erro: ...` | Qualquer outra falha (sem internet, erro ao salvar no banco...). Tenta de novo em 60 s |

---

## 6. Como os números são calculados

Toda a lógica fica em [`Dominio/regras.py`](Dominio/regras.py).

### 6.1. Saldos em dólar

Para cada ativo da carteira:
1. O saldo vem do The Graph em unidades inteiras (ex.: wei). Ele é dividido por `10 ^ decimals` do token.
2. O preço em USD vem do CoinGecko, usando o `MAPA_COINGECKO` (em [`Infraestrutura/api.py`](Infraestrutura/api.py)).
3. `valor = saldo × preço`.

> Ativos **sem preço** (fora do `MAPA_COINGECKO`, ou quando o CoinGecko falha) são **ignorados** em todos os cálculos.

- **Col** = soma do valor depositado de todos os ativos.
- **Emp** = soma da dívida variável + dívida estável de todos os ativos.

### 6.2. Health Factor

```
HF = Σ (valor depositado × LT do ativo)   ← só ativos marcados como garantia
     ─────────────────────────────────────
                 dívida total
```

- **LT** (Liquidation Threshold) é o percentual do depósito que conta como garantia. Os valores ficam fixos no código, no `MAPA_LT`.
- Só entram os depósitos que a carteira ativou como garantia na Aave (`usageAsCollateralEnabledOnUser`).
- Ativos com LT `0.0` ou fora do `MAPA_LT` não contam como garantia.

### 6.3. Taxas (Sup / Emp)

A Aave guarda as taxas como **APR em "ray"** (número × 10²⁷). O bot converte para **APY** com juros compostos por segundo:

```
apr = taxa_ray / 10^27
APY = (1 + apr / 31.536.000) ^ 31.536.000 − 1
```

Depois calcula, em dólar por ano:
- **ganho anual** = Σ (valor depositado × APY de depósito do ativo)
- **custo anual** = Σ (dívida variável × APY variável + dívida estável × APY estável)

E as médias exibidas na linha 3:
- **Sup** = ganho anual ÷ Col
- **Emp** = custo anual ÷ Emp

### 6.4. APY líquido

É a mesma conta do "Net APY" do app da Aave:

```
APY líquido = (ganho anual − custo anual) ÷ (Col − Emp)
```

Se o patrimônio (`Col − Emp`) for zero ou negativo, aparece `--`.

> O APY considera **só os juros da Aave**. Recompensas extras (incentivos, pontos, airdrops) não entram.

---

## 7. Histórico no banco de dados (SQLite)

### 7.1. Onde fica

Arquivo **`historico_carteiras.db`**, na raiz do projeto. Ele é criado automaticamente na primeira execução. É um banco **SQLite**: um arquivo único, sem servidor e sem instalação.

### 7.2. Uma tabela por carteira

O nome da tabela vem do nome da carteira, sem emoji, acento ou pontuação:

| Nome no `carteiras.py` | Tabela |
|---|---|
| `⭐️ Carteira Principal` | `carteira_principal` |
| `💳 Carteira Pagamentos` | `carteira_pagamentos` |

As tabelas são criadas quando o bot inicia, só se ainda não existirem.

### 7.3. Colunas

| Coluna | Tipo | Conteúdo |
|---|---|---|
| `id` | inteiro | Número sequencial do registro |
| `data_hora` | texto | Data e hora local, ex. `2026-10-02 14:17:08` |
| `endereco` | texto | Endereço da carteira (minúsculo) |
| `nome_carteira` | texto | Nome sem emoji, ex. `Carteira Principal` |
| `colateral_usd` | real | Col em USD (2 casas) |
| `divida_usd` | real | Emp em USD (2 casas) |
| `apy_sup` | real | Taxa média de depósito, **em %** (ex. `3.5`) |
| `apy_emp` | real | Taxa média de empréstimo, em % |
| `apy_liquido` | real | APY líquido, em % |
| `hf` | real | Health Factor. **Vazio (NULL)** quando a dívida é menor que $0.01 |

### 7.4. Quando um registro é salvo

- **Uma linha por carteira a cada 60 segundos**, logo depois de o letreiro ser atualizado.
- **Não** salva carteiras `Sem Posição`.
- **Não** salva nada nos ciclos que terminaram em erro.

São cerca de 1.440 linhas por carteira por dia. O SQLite lida bem com esse volume.

### 7.5. Como consultar

**Com programa visual:** abra o arquivo `.db` no [DB Browser for SQLite](https://sqlitebrowser.org/) ou numa extensão de SQLite do VS Code.

**Pelo terminal:**
```bash
sqlite3 historico_carteiras.db
```

Exemplos de consultas:
```sql
-- Listar as tabelas
.tables

-- Últimos 10 registros de uma carteira
SELECT * FROM carteira_principal ORDER BY id DESC LIMIT 10;

-- Menor HF de cada dia
SELECT date(data_hora) AS dia, MIN(hf) AS menor_hf
FROM carteira_investimentos
GROUP BY dia
ORDER BY dia;
```

Para sair do `sqlite3`, digite `.quit`.

**Para começar o histórico do zero:** pare o bot e apague o `historico_carteiras.db`. Ele será recriado vazio na próxima execução.

---

## 8. Como o programa funciona por dentro

O programa roda **duas tarefas ao mesmo tempo** (duas threads), que se comunicam pelo módulo [`Compartilhado/estado.py`](Compartilhado/estado.py):

```
                    ┌──────────────────────── main.py ────────────────────────┐
                    │                                                         │
   Thread de fundo (a cada 60 s)                         Thread principal (a cada 0,25 s)
   CasosDeUso/montar_letreiro.py                         Apresentacao/letreiro.py
                    │                                                         │
   1. Busca preços (CoinGecko)                           1. Lê as 5 linhas do estado
   2. Busca posições (The Graph)                         2. Recorta o pedaço visível
   3. Calcula Col, Emp, taxas, APY, HF                   3. Aplica as cores
   4. Monta as 5 linhas de texto                         4. Desenha na tela
   5. Grava no estado ─────────► Compartilhado/estado.py ◄─────── (lê daqui)
   6. Salva no SQLite                                    5. Avança 1 coluna
```

### Passo a passo de um ciclo de atualização

1. **`main.py`** inicia a thread de fundo com `buscar_dados_e_montar_letreiro()` e começa a animação na thread principal.
2. Ao iniciar, a thread de fundo **cria as tabelas** que faltam no banco (`criar_tabelas`).
3. **Preços:** `obter_precos_coingecko()` busca o preço em USD de todos os ativos do `MAPA_COINGECKO` numa única chamada. Se falhar, devolve vazio, e os ativos sem preço são ignorados.
4. **Posições:** `buscar_reservas()` envia **uma única consulta GraphQL** ao The Graph, com todos os endereços. Ela traz, para cada ativo, o saldo depositado, a dívida, se está marcado como garantia, os decimais e as taxas.
5. Se o The Graph responder com `errors`, a mensagem aparece no letreiro e o bot tenta de novo em 30 s.
6. **Para cada carteira** do `carteiras.py`, na ordem do arquivo:
   - `calcular_totais()` calcula Col, colateral ajustado, Emp, ganho anual e custo anual.
   - `calcular_taxas_medias()` calcula Sup e Emp em %.
   - `calcular_apy_liquido()` calcula o APY.
   - `calcular_hf()` calcula o HF e a seta, comparando com o HF guardado em `estado.historico_hf`.
   - São montadas as 5 strings da carteira. As versões coloridas vão para um "mapa de cores".
   - Cada string é centralizada na **largura visual** do bloco, com emojis contados como 2 colunas.
7. Os blocos de todas as carteiras são unidos com `  ||  ` e gravados em `estado.linha1_global` até `estado.linha5_global`.
8. **`salvar_registros()`** grava uma linha na tabela de cada carteira.
9. Espera 60 s e volta ao passo 3.

### Passo a passo de um quadro da animação

1. Lê a largura atual do terminal. Se você redimensionar a janela, o letreiro se adapta.
2. Converte cada linha numa lista de **colunas de tela** (`para_colunas`). Um emoji vira 2 colunas.
3. Recorta exatamente a largura da tela a partir da posição atual (`recortar`). Quando chega ao fim, volta ao começo. Se um emoji ficar cortado ao meio na borda, ele vira espaço, para a linha nunca estourar.
4. Troca os trechos "crus" pelos coloridos (`aplicar_cores`).
5. Escreve as 5 linhas e sobe o cursor 5 linhas (`\033[5A`), para que o próximo quadro sobrescreva o atual.
6. Avança 1 coluna e espera 0,25 s.

---

## 9. Estrutura de pastas

O código é separado em camadas, cada uma com uma responsabilidade:

```
.
├── Iniciar Radar Aave.command     # Executável: dois cliques abrem o bot no Terminal (macOS)
├── main.py                        # Ponto de entrada: inicia as duas threads
├── requirements.txt               # Bibliotecas necessárias
├── LICENSE                        # Licença Apache 2.0
├── .env.exemplo                   # Modelo do .env (sem a chave)
├── .env                           # Sua chave da API         (NÃO vai pro Git)
├── historico_carteiras.db         # Banco SQLite             (NÃO vai pro Git)
│
├── Compartilhado/                 # Dados usados por várias camadas
│   ├── carteiras.exemplo.py       #   Modelo de carteiras (endereços fictícios)
│   ├── carteiras.py               #   Suas carteiras         (NÃO vai pro Git)
│   └── estado.py                  #   Variáveis compartilhadas entre as threads
│
├── Infraestrutura/                # Comunicação com serviços externos
│   └── api.py                     #   The Graph (posições) e CoinGecko (preços)
│
├── Dominio/                       # Regras de negócio (só cálculos, sem internet)
│   └── regras.py                  #   Col/Emp, taxas, APY líquido, Health Factor
│
├── CasosDeUso/                    # Junta tudo: busca → calcula → monta → salva
│   └── montar_letreiro.py
│
├── Repositorio/                   # Persistência
│   └── banco.py                   #   Cria tabelas e salva registros no SQLite
│
└── Apresentacao/                  # Tudo o que aparece na tela
    ├── cores.py                   #   Códigos de cor ANSI e aplicação das cores
    ├── largura.py                 #   Largura visual (emoji = 2 colunas), centralizar e recortar
    └── letreiro.py                #   Loop da animação
```

Cada pasta tem um `__init__.py` vazio, que marca a pasta como pacote Python.

---

## 10. Personalizando

| Quero... | Onde mudar |
|---|---|
| Adicionar ou remover carteiras | `Compartilhado/carteiras.py` |
| Mudar a velocidade da animação | `main.py` → `animar_letreiro_multiplo(velocidade=0.25)` (menor = mais rápido) |
| Mudar o intervalo de atualização | `CasosDeUso/montar_letreiro.py` → `time.sleep(60)` no final |
| Mudar os limites de cor do HF | `CasosDeUso/montar_letreiro.py` → linha do `cor_hf` (1.5 e 1.1) |
| Mudar o separador entre carteiras | `CasosDeUso/montar_letreiro.py` → `separador = "  ||  "` |
| Mudar as cores | `Apresentacao/cores.py` |
| Usar outro subgraph ou rede | `Infraestrutura/api.py` → `THE_GRAPH_URL` |

### Adicionar um ativo novo

Se a carteira tiver um token que o bot ainda não conhece, ele é **ignorado** nos cálculos. Para incluir:

1. **Preço:** em `Infraestrutura/api.py`, adicione ao `MAPA_COINGECKO` o símbolo (exatamente como aparece na Aave) e o ID do CoinGecko. O ID aparece na URL da moeda, por exemplo `coingecko.com/pt/moedas/`**`ethereum`**.
   ```python
   "NOVO": "id-no-coingecko",
   ```
2. **Garantia (para o HF):** em `Dominio/regras.py`, adicione ao `MAPA_LT` o Liquidation Threshold do ativo, conforme a página do ativo no app da Aave. Por exemplo, 78% vira `0.78`.
   ```python
   "NOVO": 0.78,
   ```
3. Pare e rode o bot de novo.

---

## 11. Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'requests'` (ou `wcwidth`, `dotenv`) | Dependências não instaladas, ou o ambiente virtual não está ativo | Ative o `.venv` e rode `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'Compartilhado.carteiras'` | O `carteiras.py` não foi criado | Faça o [passo 3.2](#32-suas-carteiras-compartilhadocarteiraspy) |
| `ModuleNotFoundError: No module named 'Dominio'` | Bot rodado de dentro de uma subpasta | Rode `python3 main.py` na raiz do projeto |
| `Erro no Graph: auth error...` | Chave ausente ou inválida no `.env` | Confira o [passo 3.1](#31-chave-da-api-do-the-graph-env): o arquivo deve se chamar `.env`, ficar na raiz e conter `API_KEY=...` |
| Todas as carteiras com `Sem Posição` | Endereço errado, ou carteira em outra rede | Confira os endereços e se eles têm posição na rede do subgraph configurado |
| Col e Emp em `$0.00` mesmo havendo posição | CoinGecko fora do ar ou limitando requisições, ou ativo fora do `MAPA_COINGECKO` | Aguarde o próximo ciclo; veja [Adicionar um ativo novo](#adicionar-um-ativo-novo) |
| Linhas duplicadas ou "escorregando" na tela | Janela estreita demais, ou terminal que não mede emoji com 2 colunas | Aumente a janela; use um terminal moderno; ou tire os emojis dos nomes |
| Cores aparecem como `[92m` | Terminal sem suporte a ANSI | Use o Windows Terminal ou o terminal do VS Code |
| `Erro: database is locked` | O `.db` está aberto e travado em outro programa | Feche o outro programa ou desative a edição nele |
| Mudei o código e nada mudou | O bot antigo continua rodando | `Ctrl + C` e abra o bot de novo |
| Dois cliques no `.command` não fazem nada, ou aparece aviso de permissão | O arquivo perdeu a permissão de execução (comum em download por ZIP) | Rode `chmod +x "Iniciar Radar Aave.command"` na raiz do projeto |
| *"Desenvolvedor não identificado"* ao abrir o `.command` | Proteção do macOS (Gatekeeper) | Botão direito no arquivo → **Abrir** → **Abrir** |
| O executável mostra `❌ Arquivo .env não encontrado` ou `❌ ... carteiras.py não encontrado` | Configuração não feita | Faça o [passo 3](#3-configuração) |
| O executável mostra `❌ Não foi possível instalar as dependências` | Sem internet, ou pip com problema | Confira a internet e rode `python3 -m pip install --user -r requirements.txt` para ver o erro completo |

---

## 12. Limitações conhecidas

- **LT fixo no código:** se a Aave mudar o Liquidation Threshold de um ativo, atualize o `MAPA_LT` à mão. Caso contrário, o HF calculado vai diferir do HF do app.
- **Atraso do The Graph:** o subgraph pode estar alguns blocos atrás da blockchain, então os valores podem diferir um pouco do app da Aave.
- **Preços do CoinGecko:** a API gratuita tem limite de requisições e pode ter pequenas diferenças em relação ao oráculo de preços que a Aave usa.
- **Ativos sem mapeamento** são ignorados (veja a [seção 10](#adicionar-um-ativo-novo)).
- **Seta do HF:** compara com a leitura anterior **desde que o bot foi aberto**. Ao reiniciar, ela volta a `-`.
- **Sem alertas externos:** o aviso `⚠️ RISCO` aparece só no terminal. Não há notificação por e-mail ou celular.

---

## 13. Segurança

- **Nunca** envie o `.env` para o GitHub. Ele já está no `.gitignore`.
- O `carteiras.py` e o `historico_carteiras.db` também ficam fora do Git. Eles ligam seus endereços às suas finalidades e ao histórico dos seus saldos.
- Se a sua chave do The Graph for exposta por engano (num commit, print ou mensagem), **gere uma chave nova** no The Graph Studio e apague a antiga. O histórico do Git guarda tudo, mesmo depois que o arquivo é apagado.
- O bot **só lê** dados públicos. Ele não usa chave privada, não assina transações e não movimenta fundos.

---

## 14. Licença

Este projeto é distribuído sob a **Licença Apache 2.0**. O texto completo está no arquivo [`LICENSE`](LICENSE).

Em resumo, você pode usar, copiar, modificar e distribuir o código, inclusive para fins comerciais, desde que:
- mantenha o aviso de licença e de direitos autorais;
- informe quais arquivos você alterou, se redistribuir uma versão modificada.

O software é fornecido **"como está", sem garantias**. Os autores não se responsabilizam por decisões financeiras ou prejuízos decorrentes do uso deste bot.
