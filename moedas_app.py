import streamlit as st
import requests #busca dados das moedas
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
#streamlit run moedas_app.py

#função buscar dados na api requests
def buscar_dados(moeda_escolhida, periodo):

    resposta = requests.get(f'https://economia.awesomeapi.com.br/json/daily/{moeda_escolhida}/{periodo}')
    dados = resposta.json()
    return dados

#função criar tabela usando 
def criar_tabela(dados):
    tabela_limpa = []
    for item in dados:
        if "timestamp" in item and "bid" in item and "ask" in item and "high" in item and "low" in item:
            nova_linha = {
                "timestamp": int(item["timestamp"]),
                "bid": float(item["bid"]),
                "ask": float(item["ask"]),
                "high": float(item["high"]),
                "low": float(item["low"])
            }
            tabela_limpa.append(nova_linha)

    df = pd.DataFrame(tabela_limpa)  # CORRIGIDO AQUI
    df["data"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.sort_values("data")
    tabela = df[["data", "bid", "ask", "high", "low"]].tail(30)
    return tabela

#função formatar tabela
def formatar_tabela_em_reais(tabela):
    colunas_para_formatar = ["bid", "ask", "high", "low"]
    for coluna in colunas_para_formatar:
        tabela[coluna] = tabela[coluna].apply(lambda x: f"R$ {x:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    return tabela

#função criar gradico usando mtplotlib
def criar_grafico(tabela, periodo, moeda_escolhida):
    
    plt.figure(figsize=(10, 5))
    
    plt.plot(tabela["data"], tabela["bid"], marker='o', linestyle='-')

    plt.title(f"Variação da moeda {moeda_escolhida} nos ultimos {periodo} dias")
    plt.xlabel("data")
    plt.ylabel("bid")

    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()
    st.pyplot(plt)

#função salvar dados usando StringIO
def gerar_csv_download(tabela):
    csv = StringIO()
    tabela.to_csv(csv, index=False, encoding='utf-8-sig')
    return csv.getvalue()


#Solicitando moedas e passando moedas para api 
moedas = ['USD-BRL','EUR-BRL','BTC-BRL']
moeda_escolhida = st.selectbox('Qual moeda você deseja consultar?', moedas)

#solictando dias desejados para ser apresentado
periodo = st.slider('Quantos dias deseja visualizar? (minimo 1 e máximo 30)', min_value=1, max_value=30)
st.write(f'Você escolheu a moeda {moeda_escolhida} para os últimos {periodo} dias')


#chamda função dados API
dados = buscar_dados(moeda_escolhida, periodo)

# Cria gráfico com dados numéricos
criar_grafico(tabela, periodo, moeda_escolhida)

#Chamada função criar tabela
tabela = criar_tabela(dados)

# Exibe tabela formatada (com R$)
tabela_formatada = formatar_tabela_em_reais(tabela.copy())  # usa .copy() para evitar conflitos
st.dataframe(tabela_formatada)


# Gera CSV com dados numéricos
csv = gerar_csv_download(tabela)
st.download_button(
    label="📥 Baixar CSV",
    data=csv,
    file_name=f"cotacao_{moeda_escolhida}_{periodo}dias.csv",
    mime="text/csv",
    help="Clique para baixar o histórico da moeda selecionada"
)