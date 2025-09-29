import requests
from bs4 import BeautifulSoup
import csv
import re
import os
import pandas as pd

# -----------------------------
# 1. Baixa a página web
# -----------------------------
url = 'https://shockmetais.com.br/lme'
pagina = requests.get(url)
lme = BeautifulSoup(pagina.text, 'html.parser')

# -----------------------------
# 2. Define local de saída do CSV
# -----------------------------
pasta_saida = "LME2"  # Pasta onde o CSV será salvo
arquivo_saida = os.path.join(
    pasta_saida, "acompanhamento_lme.csv")  # Caminho completo

# Cria a pasta se não existir
os.makedirs(pasta_saida, exist_ok=True)

# -----------------------------
# 3. Procura as tabelas na página
# -----------------------------
tabelas = lme.find_all(
    'table', class_="table table-hover table-sm table-striped shadow")

# Função para verificar se a primeira coluna é uma data


def is_data_row(text):
    return bool(re.match(r'\d{2}/[A-Za-z]{3}', text))


# -----------------------------
# 4. Lê o CSV existente (se houver)
# -----------------------------
if os.path.exists(arquivo_saida):
    df_existente = pd.read_csv(arquivo_saida, sep=';', dtype=str)
else:
    df_existente = pd.DataFrame()  # Cria vazio se CSV não existir

# Lista para armazenar novas linhas
novas_linhas = []

# -----------------------------
# 5. Processa cada tabela
# -----------------------------
for tabela in tabelas:
    # Pega cabeçalho
    thead = tabela.find('thead')
    if thead:
        colunas = [th.get_text(strip=True) for th in thead.find_all('th')]

    # Pega linhas da tabela
    tbody = tabela.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            dados = [td.get_text(strip=True) for td in tr.find_all('td')]
            if not dados:
                continue
            if not is_data_row(dados[0]):
                continue

            # Processa valores das colunas
            dados_tratados = [dados[0]]  # mantém a data
            for i, valor in enumerate(dados[1:], start=1):
                valor = valor.replace('"', '').strip()

                try:
                    valor_float = float(valor)
                    if i == len(dados) - 1:
                        valor_formatado = round(valor_float, 4)
                    else:
                        valor_formatado = round(valor_float, 2)
                    dados_tratados.append(valor_formatado)
                except:
                    dados_tratados.append(valor)

            # -----------------------------
            # 6. Checa se CSV está vazio ou se linha já existe
            # -----------------------------
            if df_existente.empty or df_existente.shape[1] == 0:
                novas_linhas.append(dados_tratados)
            else:
                if not ((df_existente.iloc[:, 0] == dados_tratados[0]).any()):
                    novas_linhas.append(dados_tratados)

# -----------------------------
# 7. Escreve novas linhas no CSV
# -----------------------------
if novas_linhas:
    with open(arquivo_saida, 'a', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=';')
        # Escreve cabeçalho apenas se CSV estava vazio
        if df_existente.empty or df_existente.shape[1] == 0:
            escritor.writerow(colunas)
        for linha in novas_linhas:
            escritor.writerow(linha)

print(
    f"✅ CSV atualizado com {len(novas_linhas)} novas linhas em: {arquivo_saida}")
