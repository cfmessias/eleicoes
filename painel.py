from dash import Dash, html, dcc
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.graph_objects as go

def carregar_dados():
    resultados = pd.read_csv('C:/PythonProjects/Legislativas2025/VersaoAtual/Pervisoes.csv', sep=';', decimal=',')    
    Simbolos = pd.read_csv('C:/PythonProjects/Legislativas2025/VersaoAtual/partidos_siglas_nomes.csv', sep=';', decimal=',')
    return resultados, Simbolos

resultados, Simbolos = carregar_dados()

df = pd.merge(resultados, Simbolos, on=['Partido'], how='inner')
df=df[df['Distrito'] == ' Totais']

df_filtrado25V1 = df[(df['Ano'] == 2025) & (df['Visão'] == 'Histórico') & (df['Distrito'] == ' Totais')]
df_filtrado25V2 = df[(df['Ano'] == 2025) & (df['Visão'].str.contains('Sondagens', case=False, na=False)) & (df['Distrito'] == ' Totais')]

df_filtrado25V1 = df_filtrado25V1.rename(columns={'Previsão (%)': 'Min (%)'})
df_filtrado25V2 = df_filtrado25V2.rename(columns={'Previsão (%)': 'Max (%)'})
df_filtrado25V1 = df_filtrado25V1[['Partido','Nome', 'Min (%)', 'Cor', 'Abstenção','Simbolo']]
df_filtrado25V2 = df_filtrado25V2[['Partido', 'Max (%)']]
df_filtrado25 = pd.merge(
    df_filtrado25V1[['Partido','Nome', 'Min (%)', 'Cor', 'Abstenção','Simbolo']], 
    df_filtrado25V2[['Partido', 'Max (%)']],
    on=['Partido'], 
    how='inner'
)

# Construir o dicionário de dados
dados = {
    "Partido": df_filtrado25['Nome'].tolist(),
    "Min (%)": df_filtrado25['Min (%)'].tolist(),
    "Max (%)": df_filtrado25['Max (%)'].tolist(),
    "Cor": df_filtrado25['Cor'].tolist(),
    "Simbolo": df_filtrado25['Simbolo'].tolist()
}
print(dados)
abstencao = df_filtrado25['Abstenção'].values[0] * 100  

# Criar DataFrame
df_painel = pd.DataFrame(dados)
# fig2 = go.Figure(data=[
#     go.Table(
#         columnwidth=[100, 50, 50],
#         header=dict(
#             values=["<b>Partido</b>", "<b>Min.</b>", "<b>Max.</b>"],
#             fill_color="#E1E1E1",
#             align=["left", "center", "center"],
#             font=dict(color="white", size=14, family="Arial"),
#             height=30
#         ),
#         cells=dict(
#             values=[
#                 [
#                     f'<img src="{simbolo}" height="20" style="vertical-align:middle; margin-right:6px;"> <b>{partido}</b>'
#                     for simbolo, partido in zip(df_painel["Simbolo"], df_painel["Partido"])
#                 ],
#                 [f"{min_ * 100:.2f}%" for min_ in df_painel["Min (%)"]],
#                 [f"{max_ * 100:.2f}%" for max_ in df_painel["Max (%)"]]
#             ],
#             fill_color=[df_painel["Cor"], "#F7F7F7", "#F7F7F7"],
#             align=["left", "center", "center"],
#             font=dict(color="black", size=12),
#             height=28
#         )
#     )
# ])



fig2 = go.Figure(data=[
    go.Table(
        columnwidth=[50, 20, 20],  # Ajusta as larguras relativas
        header=dict(
            values=["<b>Partido</b>", "<b>Min.</b>", "<b>Max.</b>"],
            fill_color="#E1E1E1",
            align="center",
            font=dict(color="white", size=20),
            line_color='white',
            line_width=2,
            height=35,
            font_family="Arial",
            font_size=20

        ),
        cells=dict(
            values=[
                df_painel["Partido"],
                [f"{min_ * 100:.2f}%" for min_ in df_painel["Min (%)"]],
                [f"{max_ * 100:.2f}%" for max_ in df_painel["Max (%)"]]
                
            ],

            fill_color=[df_painel["Cor"], "#F7F7F7", "#F7F7F7"],
            align=["left", "center", "center"],  # Alinhamento por coluna
            font=dict(color=["white", "black", "black"], size=20),
            line_color='white',
            line_width=2,
            height=40
        )
    )
])

fig2.update_layout(margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig2, use_container_width=True)