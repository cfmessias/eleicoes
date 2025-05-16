import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.colors as mcolors
import numpy as np
import os   
from io import BytesIO
import base64
from PIL import Image
from matplotlib.patches import Patch
import unicodedata
from utils.helpers import *
from utils.sidebar import aplicar_filtros_sidebar


# Configurações iniciais
st.set_page_config(page_title="Eleições em Portugal", layout="wide")
#st.title("Legislativas 2025")
# Ler imagem como binário
with open("assets/bandeira.jpeg", "rb") as image_file:
    img_bytes = image_file.read()
    encoded_img = base64.b64encode(img_bytes).decode()


# Construir HTML com a imagem embutida
st.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/jpeg;base64,{encoded_img}" alt="Bandeira" style="height: 40px; margin-right: 15px;">
        <h2 style="margin: 0;">Legislativas 2025</h2>
    </div>
    """,
    unsafe_allow_html=True
)
modo = st.radio("", ["📊Previsões", "📈Resultados"], horizontal=True)

# Leitura dos dados
@st.cache_data
def carregar_dados():

    previsoes = pd.read_csv('data/previsoes.csv', sep='|', decimal=',')    
    simbolos = pd.read_csv('data/siglas_partidos.csv', sep=';', decimal=',')
    compara_previsoes =pd.read_csv('data/compara_previsoes.csv', sep=';',encoding='utf-8-sig',decimal=',')
    resultados_partido_ano=pd.read_csv('data/resultados_partido_ano.csv', sep='|',encoding='utf-8-sig',decimal=',')
    resultados_distrito_ano=pd.read_csv('data/resultados_partido_distrito_ano.csv', sep=';',encoding='utf-8-sig',decimal=',')

    return previsoes,  simbolos, compara_previsoes,resultados_partido_ano,resultados_distrito_ano

previsoes,  simbolos, compara_previsoes,resultados_partido_ano,resultados_distrito_ano = carregar_dados()

previsoes['Ano'] = previsoes['Ano'].astype(str)
df_previsoes = pd.merge(previsoes, simbolos, on=['Partido'], how='inner')
df_previsoes['Visão'] = df_previsoes['Visão'].astype(str).str.strip().str.replace('\u200b', '').str.replace('\xa0', '').str.normalize('NFKD')
df_previsoes['Previsão (%)']=df_previsoes['Previsão (%)']*100
anos = sorted(df_previsoes['Ano'].unique(), reverse=True)
tipos = df_previsoes['Visão'].unique()
distritos = sorted(df_previsoes['Distrito'].unique())

resultados_partido_ano['Ano'] = resultados_partido_ano['Ano'].astype(str)
df_resultados_ano = pd.merge(resultados_partido_ano, simbolos, on=['Partido'], how='inner')
df_resultados_ano['Percentual'] = df_resultados_ano['Percentual'] * 100  # Converter para percentual
dataset_resultados_ano_filtrado = df_resultados_ano[(df_resultados_ano['Ano'] == '2025')]
# Filtros
ano_selecionado, tipo_selecionado, distrito_selecionado = aplicar_filtros_sidebar(df_previsoes,modo) 

resultados_distrito_ano['Ano'] = resultados_distrito_ano['Ano'].astype(str)
df_resultados_distrito_ano= pd.merge(resultados_distrito_ano, simbolos, on=['Partido'], how='inner')
#df_resultados_distrito_ano['Percentual'] = df_resultados_distrito_ano['Percentual'] * 100  # Converter para percentual



#tabs = st.tabs(["Previsões", "Resultados"])

# -----------------------------------------
# 1. PREVISÕES
# -----------------------------------------
if  modo == "📊Previsões":

    df_filtrado   = df_previsoes[(df_previsoes['Ano'] == ano_selecionado) & (df_previsoes['Visão'] == tipo_selecionado) & (df_previsoes['Distrito'] == distrito_selecionado)]
    previsao_opcao = st.radio("", [  "Tipo","Partidos","Parlamento"], horizontal=True)

    if previsao_opcao == "Tipo":
        dataset = pd.merge(compara_previsoes, simbolos, on=['Partido'], how='inner')
        dataset = dataset[dataset['Ano'] != '2024']
        dataset = dataset[dataset['Ano'] != ' Sondagens']   
 
        
        plot_previsoes(dataset)
        
        
    elif previsao_opcao == "Parlamento":
        
        col1, col2 = st.columns([3.8, 2])
        # Ordenar para manter consistência de layout
        with col1:
            #st.markdown('<div class="custom-subheader">Assentos parlamentares</div>', unsafe_allow_html=True)
            ordem_partidos = ["BE","CDU","L","PS","PAN","AD", "IL", "CH"]
            df_filtrado["Ordem"] = df_filtrado["Partido"].apply(lambda x: ordem_partidos.index(x) if x in ordem_partidos else len(ordem_partidos))
            df_filtrado = df_filtrado.sort_values("Ordem").reset_index(drop=True)
            # Gráfico
           
            fig = plot_hemiciclo_parlamentar(df_filtrado, ordem_partidos)
            st.pyplot(fig, transparent=True)

            abstencao = df_filtrado['Abstenção'].values[0] * 100  # Supondo que você tenha uma coluna de abstenção no DataFrame
            brancos = df_filtrado['Brancos'].values[0] 
            
            brancos_formatado = f"{brancos / 1000:.1f}K"
            subcol1, subcol2 = st.columns([0.6, 2])
            
            with subcol2:
                st.markdown(f"""

                <div style=" padding:6px 6px; border-radius:0 0 5px 5px; width:300px; text-align:center; ">
                    <span style="color:white; font-weight:bold; font-size:14px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Abstenção: {abstencao:.2f}%</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span> 
                    <span style="color:white; font-weight:bold; font-size:14px;">Brancos: {brancos_formatado}</span>
                </div>
                """, unsafe_allow_html=True)
    
    elif previsao_opcao == "Partidos":
        dataset = pd.merge(compara_previsoes, simbolos, on=['Partido'], how='inner')
        dataset = dataset[dataset['Ano'] != '2024']
  
        plot_metricas_com_simbolos(
            dataset,
            coluna_valor='Percentual',
            titulo_eixo_y='Percentual (%)',
            ylim_max=45
        )
# -----------------------------------------
# 2. RESULTADOS
# -----------------------------------------
elif modo == "📈Resultados":
    
    resultados_distrito_ano_filtrado = df_resultados_distrito_ano[(df_resultados_distrito_ano['Distrito'] == distrito_selecionado)]
    resultado_opcao = st.radio("", ["2025","Parlamento","% Partidos","Mandatos Partidos","2024-2025"], horizontal=True)
   
    if resultado_opcao == "2025":
     
        col1, col2 , col3 = st.columns([4,1,1])

        with col1:

            mostrar_titulo_custom(f"{distrito_selecionado}")
            resultados_distrito_filtrado=resultados_distrito_ano_filtrado[resultados_distrito_ano_filtrado['Ano'].isin(['2025'])]     
              
            #mostrar_abstencao_brancos(df_filtrado)
            info = f"Abstenção: {resultados_distrito_filtrado['Abstenção'].values[0]:.2f}%\nBrancos: {resultados_distrito_filtrado['Brancos'].values[0]/1000:.1f}K"
            fig = plot_bar_chart(resultados_distrito_filtrado, coluna_valores="Percentual", formato="percentagem", legenda="2025", info_extra=info,n="2")

            st.pyplot(fig, transparent=True)

    elif resultado_opcao == "Parlamento":
        col1, col2 = st.columns([3, 1])
        # Ordenar para manter consistência de layout
        with col1:
            #st.markdown('<div class="custom-subheader">Assentos parlamentares</div>', unsafe_allow_html=True)
            ordem_partidos = ["BE","CDU","L","PS","PAN","AD", "IL", "CH"]
            resultados_distrito_ano_filtrado["Ordem"] = resultados_distrito_ano_filtrado["Partido"].apply(lambda x: ordem_partidos.index(x) if x in ordem_partidos else len(ordem_partidos))
            resultados_distrito_ano_filtrado = resultados_distrito_ano_filtrado.sort_values("Ordem").reset_index(drop=True)
            resultados_distrito_filtrado=resultados_distrito_ano_filtrado[resultados_distrito_ano_filtrado['Ano'].isin(['2025'])] 

            fig = plot_hemiciclo_parlamentar(resultados_distrito_filtrado, ordem_partidos)
            st.pyplot(fig, transparent=True)
            # Gráfico
           
            abstencao = resultados_distrito_filtrado['Abstenção'].values[0] * 100 # Supondo que você tenha uma coluna de abstenção no DataFrame
            brancos = resultados_distrito_filtrado['Brancos'].values[0] 
            
            brancos_formatado = f"{brancos / 1000:.1f}K"

            subcol1, subcol2 = st.columns([0.85, 2])

            with subcol2:
                st.markdown(f"""

                <div style=" padding:6px 6px; border-radius:0 0 5px 5px; width:300px; text-align:center; ">
                    <span style="color:white; font-weight:bold; font-size:14px;">Abstenção: {abstencao:.2f}%</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span> 
                    <span style="color:white; font-weight:bold; font-size:14px;">Brancos: {brancos_formatado}</span>
                </div>
                """, unsafe_allow_html=True)

    elif resultado_opcao == "% Partidos":
        
        #-------------------------
        #st.subheader("Evolução de Mandatos")
        # 👉 Coloca aqui o código da comparação de resultados (por ano ou partido)
        dataset = pd.merge(resultados_partido_ano, simbolos, on=['Partido'], how='inner')
        dataset['Percentual'] = dataset['Percentual'] * 100  # Converter para percentual

        plot_metricas_com_simbolos(
            dataset,
            coluna_valor='Percentual',
            titulo_eixo_y='Percentual (%)',
            ylim_max=45
        )
        
    elif resultado_opcao == "Mandatos Partidos":
    
        #-------------------------
        #st.subheader("Evolução de Mandatos")
        # 👉 Coloca aqui o código da comparação de resultados (por ano ou partido)
        dataset = pd.merge(resultados_partido_ano, simbolos, on=['Partido'], how='inner')
        plot_metricas_com_simbolos(
            dataset,
            coluna_valor='Mandatos',
            titulo_eixo_y='Mandatos',
            ylim_max=135  # ou outro valor adequado
        )
        
    elif resultado_opcao == "2024-2025":
        
        #st.subheader("Resultados 2025-2024")
        # 👉 Coloca aqui o código da visualização 2024-2025 (pie ou barras)
        col1, col2  = st.columns([4,2])
        with col1:
            dataset_filtrados = resultados_distrito_ano_filtrado[resultados_distrito_ano_filtrado['Ano'].isin(['2025', '2024'])]
            dataset_filtrados['Mandatos'] = dataset_filtrados['Mandatos'].astype(int)  # Converter para inteiro
            dataset_filtrados2025=resultados_distrito_ano_filtrado[resultados_distrito_ano_filtrado['Ano'].isin(['2025'])]
            dataset_filtrados2024=resultados_distrito_ano_filtrado[resultados_distrito_ano_filtrado['Ano'].isin(['2024'])]
            abstencao2025 = dataset_filtrados2025['Abstenção'].values[0]  
            abstencao2024 = dataset_filtrados2024['Abstenção'].values[0] 
            brancos2025 = dataset_filtrados2025['Brancos'].values[0] 
            brancos2024 = dataset_filtrados2024['Brancos'].values[0] 

            brancos_formatado2025 = f"{brancos2025 / 1000:.1f}K"
            brancos_formatado2024 = f"{brancos2024 / 1000:.1f}K"
            legenda = (
                f"2025\nAbstenção: {abstencao2025:.2f}%\nBrancos: {brancos_formatado2025}\n\n"
                f"2024\nAbstenção: {abstencao2024:.2f}%\nBrancos: {brancos_formatado2024}"
            )
            mostrar_titulo_custom(f"{distrito_selecionado}")
            fig = plot_bar_chart_comparativo(
                df=dataset_filtrados,
                #coluna_valores='Mandatos',         # ou 'Percentual'
                coluna_valores='Percentual',   
                formato='percentagem',                      # ou 'percentagem'
                legenda=legenda,
                info_extra="",
                n="2",
                ano_ordem=2025,
                ano_esbatido=2024
            )
            st.pyplot(fig, transparent=True)
            
            
