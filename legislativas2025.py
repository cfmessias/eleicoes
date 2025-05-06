import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import os   
from io import BytesIO
import base64
from PIL import Image
import matplotlib.colors as mcolors

# Configurações iniciais
st.set_page_config(page_title="Eleições em Portugal", layout="wide")
st.title("Dashboard Eleitoral - Portugal")

def formatar_em_k(numero):
    # Dividir por 1.000, formatar com uma casa decimal e adicionar o sufixo K
    return f"{numero / 1000:.1f}K"

# CSS para personalizar a sidebar
css = """
<style>
    [data-testid="stSidebar"] {
        min-width: 200px;
        max-width: 250px;
        background-color: #f8f9fa;
        padding: 1rem;
        border-right: 1px solid #dee2e6;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        font-family: 'Arial', sans-serif;
    }
    
    .stSelectbox label {
        font-size: 16px;
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 5px;
    }
    
    /* Título da sidebar */
    [data-testid="stSidebar"] h2 {
        font-size: 20px;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
"""

# Injetar o CSS
st.markdown(css, unsafe_allow_html=True)

# Agora adicione um título na sidebar antes dos filtros
st.sidebar.markdown("## Filtros")
# Leitura dos dados
@st.cache_data
def carregar_dados():
    resultados = pd.read_csv('data/Pervisoes.csv', sep=';', decimal=',')
    partidos = pd.read_csv('data/dados_partidos.csv', sep=';', decimal=',')
    Simbolos = pd.read_csv('data/Siglas_partidos.csv', sep=';', decimal=',')
    return resultados, partidos, Simbolos

resultados, partidos, Simbolos = carregar_dados()

# Converter os tipos de dados para garantir compatibilidade
resultados['Ano'] = resultados['Ano'].astype(str)
partidos['Ano'] = partidos['Ano'].astype(str)

# Junção com dados dos partidos (inclui cores, nomes, etc.)
df = pd.merge(resultados, Simbolos, on=['Partido'], how='inner')


# Filtros
anos = sorted(df['Ano'].unique(), reverse=True)
tipos = df['Visão'].unique()
distritos = sorted(df['Distrito'].unique())

# Seus elementos da sidebar
ano_selecionado = st.sidebar.selectbox("Seleciona o ano", anos)
tipo_selecionado = st.sidebar.selectbox("Seleciona o tipo de previsão", tipos)
distrito_selecionado = st.sidebar.selectbox("Seleciona o distrito", distritos)

df['Previsão (%)']=df['Previsão (%)']*100

df_filtrado = df[(df['Ano'] == ano_selecionado) & (df['Visão'] == tipo_selecionado) & (df['Distrito'] == distrito_selecionado)]
df_filtrado24 = df[(df['Ano'] == '2024') & (df['Visão'] == tipo_selecionado) & (df['Distrito'] == distrito_selecionado)]
df_filtrado25 = df[(df['Ano'] == '2025') & (df['Visão'] == tipo_selecionado) & (df['Distrito'] == distrito_selecionado)]

# Tabs para diferentes gráficos
tabs = st.tabs(["Previsões", "Comparativo","Evolução"])

with tabs[0]:
    
    st.subheader("Resultados por Partido")

    df_ord = df_filtrado.sort_values(by="Previsão (%)", ascending=False)
    col1, col2 = st.columns([3, 2])
    # Primeiro o gráfico     
    
    with col1:
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(df_ord["Partido"], df_ord["Previsão (%)"], color=df_ord["Cor"])
        
        plt.xticks(rotation=45, ha='right')
        ax.set_ylabel("% de Votos")
        #ax.set_xlabel("Partido")
        ax.bar_label(bars, fmt="%.2f%%", padding=3, fontsize=14)  # Tamanho 14 é apenas um exemplo

        # Remover a moldura
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Adicionar grid lines horizontais
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        st.pyplot(fig)
   
    with col2:
        # Exemplo de visualização ao estilo "cartão"
        abstencao = df_filtrado['Abstenção'].values[0] * 100  # Supondo que você tenha uma coluna de abstenção no DataFrame
        brancos = df_filtrado['Brancos'].values[0] 
        #brancos_formatado = f"{brancos:,}".replace(",", ".")
        brancos_formatado = f"{brancos / 1000:.1f}K"
        st.markdown(f"""
        <div style="background-color:#0072CE; padding:6px 6px; border-radius:5px; width:100px; text-align:center">
            <span style="color:white; font-weight:bold; font-size:14px;">Abstenção</span>
        </div>
        <div style="background-color:white; padding:6px 6px; border-radius:0 0 5px 5px; width:100px; text-align:center; border:1px solid #ccc;">
            <span style="color:#0072CE; font-weight:bold; font-size:20px;">{abstencao:.2f}%</span>
        </div>
        <div><br></div>
        <div style="background-color:#0072CE; padding:6px 6px; border-radius:5px; width:100px; text-align:center">
            <span style="color:white; font-weight:bold; font-size:14px;">Brancos</span>
        </div>
        <div style="background-color:white; padding:6px 6px; border-radius:0 0 5px 5px; width:100px; text-align:center; border:1px solid #ccc;">
            <span style="color:#0072CE; font-weight:bold; font-size:20px;">{brancos_formatado}</span>
        </div>
        """, unsafe_allow_html=True)


       # Gráfico de Mandatos (Pie Chart)
    st.subheader("Distribuição de Mandatos")

    colsub1, colsub2,colsub3 = st.columns([0.5,2,2.5])
    with colsub2:

        fig2, ax2 = plt.subplots(figsize=(5, 5))

        df_pie = df_ord[df_ord['Mandatos'] > 0]
        # Calcular corretamente o número de partidos
        num_partidos = len(df_pie)  # Conta o número de linhas no DataFrame filtrado

        # Criar explode com o tamanho correto
        explode = [0] * num_partidos  # Cria uma lista de zeros do tamanho correto
        if num_partidos > 0:  # Verificar se há pelo menos um partido
            explode[0] = 0.1  # Destacar o primeiro partido

        explode = [0.15] * num_partidos

        # Limpar os valores de cor (remover espaços extras)
        df_pie['Cor_limpa'] = df_pie['Cor'].str.strip()
        ax2.pie(
            df_pie['Mandatos'],
            labels=[f"{row['Partido']} ({row['Mandatos']})" for _, row in df_pie.iterrows()],
            colors=df_pie['Cor'],
            #autopct='%1.1f%%',
            startangle=140,
            shadow=True,
            radius=1.2,
            explode=explode  # Destaque para fatias específicas (afastamento)
        )
        ax2.axis('equal')  # Igual proporção para manter o círculo
        st.pyplot(fig2)




with tabs[1]:
    st.subheader("Resultados por Partido")

    col1, col2 = st.columns([3, 2])
    with col1:
        df_ord24 = df_filtrado24.sort_values(by="Previsão (%)", ascending=False)
        df_ord25 = df_filtrado25.sort_values(by="Previsão (%)", ascending=False)

        # Primeiro o gráfico     
        fig3, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(df_ord25["Partido"], df_ord25["Previsão (%)"], color=df_ord25["Cor"])
        plt.xticks(rotation=45, ha='right')
        ax.legend(title="2025",title_fontsize=24)
        ax.set_ylabel("% de Votos")
        #ax.set_xlabel("Partido")
        ax.bar_label(bars, fmt="%.2f%%", padding=3, fontsize=14)  # Tamanho 14 é apenas um exemplo

                # Remover a moldura
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Adicionar grid lines horizontais
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        st.pyplot(fig3)

                   
        fig4, ax = plt.subplots(figsize=(12, 6))
        bars2 = ax.bar(df_ord24["Partido"], df_ord24["Previsão (%)"], color=df_ord24["Cor"])
        plt.xticks(rotation=45, ha='right')               
        # Configurações do gráfico
        ax.set_xticks(range(len(df_ord24["Partido"])))
        ax.set_xticklabels(df_ord24["Partido"], rotation=45, ha='right')
        ax.set_ylabel("% de Votos")
        #ax.set_xlabel("Partido")
        ax.legend(title="2024",fontsize=30,title_fontsize=24)
        ax.bar_label(bars2, fmt="%.2f%%", padding=3, fontsize=14)  # Tamanho 14 é apenas um exemplo

        # Remover a moldura
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Adicionar grid lines horizontais
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig4)    
        
           
    with col2:
        # Exemplo de visualização ao estilo "cartão"
        abstencao = df_filtrado25['Abstenção'].values[0] * 100  # Supondo que você tenha uma coluna de abstenção no DataFrame
        brancos = df_filtrado25['Brancos'].values[0] 
        #brancos_formatado = f"{brancos:,}".replace(",", ".")
        brancos_formatado = f"{brancos / 1000:.1f}K"
        st.markdown(f"""
        <div style="background-color:#0072CE; padding:6px 6px; border-radius:5px; width:100px; text-align:center">
            <span style="color:white; font-weight:bold; font-size:14px;">Abstenção</span>
        </div>
        <div style="background-color:white; padding:6px 6px; border-radius:0 0 5px 5px; width:100px; text-align:center; border:1px solid #ccc;">
            <span style="color:#0072CE; font-weight:bold; font-size:20px;">{abstencao:.2f}%</span>
        </div>
        <div><br></div>
        <div style="background-color:#0072CE; padding:6px 6px; border-radius:5px; width:100px; text-align:center">
            <span style="color:white; font-weight:bold; font-size:14px;">Brancos</span>
        </div>
        <div style="background-color:white; padding:6px 6px; border-radius:0 0 5px 5px; width:100px; text-align:center; border:1px solid #ccc;">
            <span style="color:#0072CE; font-weight:bold; font-size:20px;">{brancos_formatado}</span>
        </div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        <div><br></div>
        """, unsafe_allow_html=True)


       
        # Exemplo de visualização ao estilo "cartão"
        abstencao = df_filtrado24['Abstenção'].values[0] * 100  # Supondo que você tenha uma coluna de abstenção no DataFrame
        brancos = df_filtrado24['Brancos'].values[0] 
        #brancos_formatado = f"{brancos:,}".replace(",", ".")
        brancos_formatado = f"{brancos / 1000:.1f}K"
        st.markdown(f"""
        <div style="background-color:#0072CE; padding:6px 6px; border-radius:5px; width:100px; text-align:center">
            <span style="color:white; font-weight:bold; font-size:14px;">Abstenção</span>
        </div>
        <div style="background-color:white; padding:6px 6px; border-radius:0 0 5px 5px; width:100px; text-align:center; border:1px solid #ccc;">
            <span style="color:#0072CE; font-weight:bold; font-size:20px;">{abstencao:.2f}%</span>
        </div>
        <div><br></div>
        <div style="background-color:#0072CE; padding:6px 6px; border-radius:5px; width:100px; text-align:center">
            <span style="color:white; font-weight:bold; font-size:14px;">Brancos</span>
        </div>
        <div style="background-color:white; padding:6px 6px; border-radius:0 0 5px 5px; width:100px; text-align:center; border:1px solid #ccc;">
            <span style="color:#0072CE; font-weight:bold; font-size:20px;">{brancos_formatado}</span>
        </div>
        """, unsafe_allow_html=True)
    
with tabs[2]:
    dataset = pd.read_csv('data/dados_partidos.csv', sep=';', decimal=',')
    # Definir as cores para cada partido
    cores_partidos = {
        'AD': '#ff7d0e',
        'PS': '#de2226',
        'L': '#b3d179',
        'CH': '#232154',
        'IL': '#019ee4',
        'B.E.': '#c00436',
        'CDU': '#02389c',
        'PAN': '#077697',
        'Outros': '#888888'  # cor neutra para "Outros", caso exista
    }

    # Função para converter o base64 em imagem PIL
    def base64_para_imagem(base64_string):
        if pd.isna(base64_string):
            return None
        # Remover o prefixo, se existir
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        img_data = base64.b64decode(base64_string)
        img = Image.open(BytesIO(img_data))
        return img

    partidos = dataset['Partido'].unique()
    n_partidos = len(partidos)

    fig5, axs = plt.subplots(3, 3, figsize=(18, 12))  # Criar subplots para até 9 gráficos
    axs = axs.flatten()

    # Primeiro criamos todos os gráficos para garantir que suas posições estejam definidas
    for i, partido in enumerate(partidos):
        if i >= len(axs):
            break
            
        dados_partido = dataset[dataset['Partido'] == partido].sort_values('Ano')
        
        # Preencher a área com cor esbatida
        axs[i].fill_between(
            dados_partido['Ano'], 
            dados_partido['Percentual'], 
            color=cores_partidos.get(partido, '#888888'), 
            alpha=0.3  # Cor esbatida (transparente)
        )
        
        # Adicionar a linha superior sólida
        axs[i].plot(
            dados_partido['Ano'], 
            dados_partido['Percentual'], 
            color=cores_partidos.get(partido, '#888888'), 
            linewidth=2  # Espessura da linha
        )
        
        # Configurações do gráfico
        axs[i].tick_params(axis='x', rotation=45)
        axs[i].set_ylabel('Percentual (%)')
        #axs[i].set_xlabel('Ano')
        axs[i].set_ylim(0, 45)  # Fixar a escala do eixo y entre 0 e 45
        axs[i].grid(True, linestyle='--', alpha=0.5)
        axs[i].set_title(partido, pad=40)  # Adicionar espaço para a imagem

    # Esconder subplots vazios se houver menos de 9 partidos
    for j in range(min(i+1, len(axs)), len(axs)):
        fig5.delaxes(axs[j])

    # Agora adicionamos as imagens depois que as posições dos gráficos estão definidas
    for i, partido in enumerate(partidos):
        if i >= len(axs) or axs[i] not in fig5.axes:
            continue
            
        dados_partido = dataset[dataset['Partido'] == partido].sort_values('Ano')
        
        # Obter imagem do partido
        imagem_base64 = dados_partido['Simbolo'].iloc[0]
        img = base64_para_imagem(imagem_base64)
        
        if img:
            # Obter posição do gráfico
            pos = axs[i].get_position()
            
            # Definir tamanho consistente para todas as imagens
            img_width = 0.06  # Tamanho horizontal da imagem
            img_height = 0.06  # Tamanho vertical da imagem
            
            # Ajustar a posição vertical com base na linha
            if i < 3:  # Primeira linha
                img_y = pos.y1 - 0.05
            elif i < 6:  # Segunda linha
                img_y = pos.y1 - 0.07
            else:  # Terceira linha
                img_y = pos.y1 - 0.09
            
            # Centralizar a imagem horizontalmente
            img_x = pos.x0 + (pos.width - img_width) / 2
            
            # Criar eixo para a imagem
            ax_img = fig5.add_axes([img_x, img_y, img_width, img_height])
            ax_img.imshow(img)
            ax_img.axis('off')  # Esconder os eixos da imagem

    # Ajustar espaço no topo e entre linhas para acomodar as imagens
    plt.subplots_adjust(top=0.85, hspace=0.9)  # Espaçamento atualizado
    st.pyplot(fig5)