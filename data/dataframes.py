import streamlit as st
import pandas as pd

@st.cache_data
def carregar_dados():

    resultados = pd.read_csv('data/previsoes.csv', sep='|', decimal=',')    
    partidos = pd.read_csv('data/dados_partidos.csv', sep=';', decimal=',')    
    simbolos = pd.read_csv('data/siglas_partidos.csv', sep=';', decimal=',')
    dataset = pd.read_csv('data/evolucao.csv', sep=';',encoding='utf-8-sig')
    dataset2025 =pd.read_csv('data/evolucao_resultados.csv', sep=';',encoding='utf-8-sig',decimal=',')
    return resultados, partidos, simbolos, dataset, dataset2025


