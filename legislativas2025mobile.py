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
import unicodedata
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def normalizar(texto):
    return unicodedata.normalize('NFC', texto)

	
def formatar_em_k(numero):
    # Dividir por 1.000, formatar com uma casa decimal e adicionar o sufixo K
    return f"{numero / 1000:.1f}K"
	
# Configurações iniciais
st.set_page_config(page_title="Eleições em Portugal", layout="wide")
st.title("Legislativas 2025")

# CSS para personalizar a sidebar
css = """
<style>
    [data-testid="stSidebar"] {
        min-width: 200px;
        max-width: 250px;
        background-color: #f8f9fa;
        padding: 1rem;
        border-right: 1px solid #dee2e6;
        background: linear-gradient(to right, #cbd3d6 ,#0c495f  );
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        font-family: 'Arial', sans-serif;
    }
    
    .stSelectbox label {
        font-size: 16px;
        font-weight: bold;
        color: #02394e;
        margin-bottom: 5px;
       
    }
    
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 5px;
    }
    .stApp {
        background: linear-gradient(to right, #0c495f   , #cbd3d6  );
    }
    /* Título da sidebar */
    [data-testid="stSidebar"] h2 {
        font-size: 20px;
        color: white;
        font-weight: bold;
        text-align: left;
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

    resultados = pd.read_csv('data/previsoes.csv', sep='|', decimal=',')    
    partidos = pd.read_csv('data/dados_partidos.csv', sep=';', decimal=',')    
    simbolos = pd.read_csv('data/siglas_partidos.csv', sep=';', decimal=',')
    return resultados, partidos, simbolos

resultados, partidos, simbolos = carregar_dados()

# Converter os tipos de dados para garantir compatibilidade
resultados['Ano'] = resultados['Ano'].astype(str)
partidos['Ano'] = partidos['Ano'].astype(str)

# Junção com dados dos partidos (inclui cores, nomes, etc.)
df = pd.merge(resultados, simbolos, on=['Partido'], how='inner')

# Filtros
df['Visão'] = df['Visão'].astype(str).str.strip().str.replace('\u200b', '').str.replace('\xa0', '').str.normalize('NFKD')
anos = sorted(df['Ano'].unique(), reverse=True)
tipos = df['Visão'].unique()
distritos = sorted(df['Distrito'].unique())
print(tipos)
ano_selecionado = st.sidebar.selectbox("Seleciona o ano", anos)
tipo_selecionado = st.sidebar.selectbox("Seleciona o tipo de previsão", tipos)
distrito_selecionado = st.sidebar.selectbox("Seleciona o distrito", distritos)

df['Previsão (%)']=df['Previsão (%)']*100

df_filtrado   = df[(df['Ano'] == ano_selecionado) & (df['Visão'] == tipo_selecionado) & (df['Distrito'] == distrito_selecionado)]
df_filtrado24 = df[(df['Ano'] == '2024') & (df['Visão'] == tipo_selecionado) & (df['Distrito'] == distrito_selecionado)]
df_filtrado25 = df[(df['Ano'] == '2025') & (df['Visão'] == tipo_selecionado) & (df['Distrito'] == distrito_selecionado)]

df_filtradoH = df[(df['Ano'] == '2025') & (df['Visão'] != 'Sondagens') & (df['Visão'] != 'Expetativas') & (df['Distrito'] == ' Totais')]
df_filtradoS = df[(df['Ano'] == '2025') & (df['Visão'] == 'Sondagens') & (df['Distrito'] == ' Totais')]
df_filtradoE = df[(df['Ano'] == '2025') & (df['Visão'] == 'Expetativas') & (df['Distrito'] == ' Totais')]

# Tabs para diferentes gráficos
tabs = st.tabs(["Previsões", "2024-2025","% - tipo previsão","Mandatos - tipo previsão","Parlamento","Evolução"])

with tabs[0]:
    
    custom_font_css = """
    <style>
        .custom-subheader {
            font-family: 'Arial', sans-serif;
            font-size: 18px !important;
            font-weight: bold;
            text-align: left !important;
            color: white !important;
            /* Adicione outras propriedades de estilo conforme necessário */
        }
    </style>
    """

    # Injetando o CSS
    st.markdown(custom_font_css, unsafe_allow_html=True)

    # Usando uma div com a classe personalizada em vez de st.subheader()
    
    df_ord = df_filtrado.sort_values(by="Previsão (%)", ascending=False)
    col1, col2 , col3 = st.columns([5,1,1])
    # Primeiro o gráfico     
    
    with col1:
        st.markdown('<div class="custom-subheader">    % por Partido</div>', unsafe_allow_html=True)
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
        st.pyplot(fig, transparent=True)
       
    
    # Gráfico de Mandatos (Pie Chart)
    colsub1, colsub2,colsub3 = st.columns([0.001,4.5,2])
    with colsub2:


        #---------------------
        st.markdown('<div class="custom-subheader">Assentos parlamentares</div>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(4, 2))

        df_pie = df_ord[df_ord['Mandatos'] > 0]
        num_partidos = len(df_pie)
        explode = [0.25] * num_partidos
        df_pie['Cor_limpa'] = df_pie['Cor'].str.strip()

        # Primeiro, criar o gráfico sem labels (isso é importante)
        wedges, _ = ax2.pie(
            df_pie['Mandatos'],
            colors=df_pie['Cor'],
            explode=explode,
            startangle=140,
            shadow=True,
            radius=1.0,  # Usar raio 1.0 como base
            labels=None  # Sem labels iniciais
            #wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
)

        # Adicionar linhas e labels manualmente
        for i, wedge in enumerate(wedges):
            # Obter o ângulo médio da fatia em graus
            ang = (wedge.theta1 + wedge.theta2) / 2
            # Converter para radianos para cálculos
            ang_rad = np.deg2rad(ang)
            
            # Raio aumentado para a posição do texto
            # Considerar o explode na posição inicial
            x1 = (1.0 + explode[i]) * np.cos(ang_rad)
            y1 = (1.0 + explode[i]) * np.sin(ang_rad)
            
            # Posição final da linha (mais afastada)
            x2 = 1.35 * np.cos(ang_rad)
            y2 = 1.35 * np.sin(ang_rad)
            
            # Texto da label
            partido = df_pie.iloc[i]['Partido']
            mandatos = int(df_pie.iloc[i]['Mandatos'])
            label = f"{partido} ({mandatos})"
            
            # Determinar o alinhamento do texto
            horizontalalignment = "left" if x2 >= 0 else "right"
            
            # Adicionar a linha diretamente
            ax2.plot([x1, x2], [y1, y2], color='black', linewidth=0.5)
            
            # Adicionar o texto
            ax2.text(
                x2 * 1.05,  # Pequeno ajuste adicional
                y2 * 1.05,
                label,
                horizontalalignment=horizontalalignment,
                verticalalignment='center',
                fontsize=5,
                fontweight='bold',
                fontfamily='Arial'
            )

        ax2.axis('equal')
        ax2.set_xlim(-1.5, 1.5)  # Aumentar os limites para acomodar os textos
        ax2.set_ylim(-1.5, 1.5)
        st.pyplot(fig2, transparent=True)

        abstencao = df_filtrado['Abstenção'].values[0] * 100  # Supondo que você tenha uma coluna de abstenção no DataFrame
        brancos = df_filtrado['Brancos'].values[0] 
        
        brancos_formatado = f"{brancos / 1000:.1f}K"
        st.markdown(f"""

        <div style=" padding:6px 6px; border-radius:0 0 5px 5px; width:300px; text-align:center; ">
            <span style="color:white; font-weight:bold; font-size:12px;">Abstenção: {abstencao:.2f}%</span>
            <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span> 
            <span style="color:white; font-weight:bold; font-size:12px;">Brancos: {brancos_formatado}</span>
        </div>
        """, unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="custom-subheader">Resultados por Partido</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])

    with col1:
        # Ordenar DataFrames
        df_ord24 = df_filtrado24.sort_values(by="Previsão (%)", ascending=False)
        df_ord25 = df_filtrado25.sort_values(by="Previsão (%)", ascending=False)

        # Função para criar gráfico de barras
        def plot_grafico_partidos(df, ano):
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar(df["Partido"], df["Previsão (%)"], color=df["Cor"])
            ax.set_ylabel("% de Votos")
            ax.set_xticks(range(len(df["Partido"])))
            ax.set_xticklabels(df["Partido"], rotation=45, ha='right')
            ax.bar_label(bars, fmt="%.2f%%", padding=3, fontsize=14)

            legend = ax.legend(title=str(ano), title_fontsize=20)
            legend.get_title().set_color("white")
            for text in legend.get_texts():
                text.set_color("white")
            legend.get_frame().set_facecolor('none')
            legend.get_frame().set_edgecolor('none')
            
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig, transparent=True)

        # Função para mostrar dados de abstenção e brancos
        def mostrar_abstencao_brancos(df):
            abstencao = df['Abstenção'].values[0] * 100
            brancos = df['Brancos'].values[0]
            brancos_formatado = f"{brancos / 1000:.1f}K"

            st.markdown(f"""
            <div style="padding:6px; border-radius:5px; width:300px; text-align:center;">
                <span style="color:white; font-weight:bold; font-size:12px;">Abstenção: {abstencao:.2f}%</span>
                <span style="margin: 0 20px;"></span>
                <span style="color:white; font-weight:bold; font-size:12px;">Brancos: {brancos_formatado}</span>
            </div>
            """, unsafe_allow_html=True)

        # Gráfico e cartão para 2025
        plot_grafico_partidos(df_ord25, 2025)
        mostrar_abstencao_brancos(df_filtrado25)

        # Gráfico e cartão para 2024
        plot_grafico_partidos(df_ord24, 2024)
        mostrar_abstencao_brancos(df_filtrado24)

with tabs[2]:
    # CSS personalizado
    custom_font_css = """
    <style>
        .custom-subheader {
            font-family: 'Arial', sans-serif;
            font-size: 24px;
            font-weight: bold;
            color: #1E88E5;
        }
    </style>
    """
    st.markdown(custom_font_css, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        # Ordenar os DataFrames
        dfs_ordenados = {
            "Histórico": df_filtradoH.sort_values(by="Previsão (%)", ascending=False),
            "Sondagens": df_filtradoS.sort_values(by="Previsão (%)", ascending=False),
            "Expetativas": df_filtradoE.sort_values(by="Previsão (%)", ascending=False)
        }

        def plot_grafico_com_legenda(df, titulo_legenda):
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar(df["Partido"], df["Previsão (%)"], color=df["Cor"])
            ax.set_ylabel("% de Votos")
            ax.set_xticks(range(len(df["Partido"])))
            ax.set_xticklabels(df["Partido"], rotation=45, ha='right')
            ax.bar_label(bars, fmt="%.2f%%", padding=3, fontsize=14)

            legend = ax.legend(title=titulo_legenda, title_fontsize=20)
            legend.get_title().set_color("white")
            for text in legend.get_texts():
                text.set_color("white")
            legend.get_frame().set_facecolor('none')
            legend.get_frame().set_edgecolor('none')

            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig, transparent=True)

        # Mostrar os três gráficos
        for titulo, df_ord in dfs_ordenados.items():
            plot_grafico_com_legenda(df_ord, titulo)

        # Mostrar abstenção e brancos (ainda referente a df_filtrado25)
        abstencao = df_filtrado25['Abstenção'].values[0] * 100
        brancos = df_filtrado25['Brancos'].values[0]
        brancos_formatado = f"{brancos / 1000:.1f}K"

        st.markdown(f"""
        <div style="padding:6px; border-radius:5px; width:300px; text-align:center;">
            <span style="color:white; font-weight:bold; font-size:12px;">Abstenção: {abstencao:.2f}%</span>
            <span style="margin: 0 20px;"></span>
            <span style="color:white; font-weight:bold; font-size:12px;">Brancos: {brancos_formatado}</span>
        </div>
        """, unsafe_allow_html=True)

with tabs[3]:
    # CSS personalizado para título
    custom_font_css = """
    <style>
        .custom-subheader {
            font-family: 'Arial', sans-serif;
            font-size: 24px;
            font-weight: bold;
            color: #1E88E5;
        }
    </style>
    """
    st.markdown(custom_font_css, unsafe_allow_html=True)

    # Ordenação dos dados
    df_ordH = df_filtradoH.sort_values(by="Mandatos", ascending=False)
    df_ordS = df_filtradoS.sort_values(by="Mandatos", ascending=False)
    df_ordE = df_filtradoE.sort_values(by="Mandatos", ascending=False)

    # Função reutilizável para gráficos de barras
    def plot_bar_chart(df, titulo_legenda):
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(df["Partido"], df["Mandatos"], color=df["Cor"])
        ax.set_ylabel("Mandatos")
        ax.set_xticks(range(len(df["Partido"])))
        ax.set_xticklabels(df["Partido"], rotation=45, ha='right')
        ax.bar_label(bars, fmt="%d", padding=3, fontsize=14)

        # Personalizar legenda
        legend = ax.legend(title=titulo_legenda, fontsize=14, title_fontsize=20)
        legend.get_title().set_color("white")
        for text in legend.get_texts():
            text.set_color("white")
        legend.get_frame().set_facecolor('none')
        legend.get_frame().set_edgecolor('none')

        # Remover moldura e adicionar grid
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        return fig

    # Coluna principal com os gráficos
    col1, col2 = st.columns([3, 2])
    with col1:
        st.pyplot(plot_bar_chart(df_ordH, "Histórico"), transparent=True)
        st.pyplot(plot_bar_chart(df_ordS, "Sondagens"), transparent=True)
        st.pyplot(plot_bar_chart(df_ordE, "Expetativas"), transparent=True)

    # Exibição de abstenção e brancos
    abstencao = df_filtrado25['Abstenção'].values[0] * 100
    brancos = df_filtrado25['Brancos'].values[0]
    brancos_formatado = f"{brancos / 1000:.1f}K"

    st.markdown(f"""
    <div style="padding:6px; border-radius:5px; width:300px; text-align:center;">
        <span style="color:white; font-weight:bold; font-size:12px;">Abstenção: {abstencao:.2f}%</span>
        <span style="margin: 0 20px;"></span>
        <span style="color:white; font-weight:bold; font-size:12px;">Brancos: {brancos_formatado}</span>
    </div>
    """, unsafe_allow_html=True)

with tabs[4]:
    
    #st.title("Previsões Legislativas 2025 ")
    col1, col2 = st.columns([4, 1])
    # Ordenar para manter consistência de layout
    with col1:
        st.markdown('<div class="custom-subheader">Assentos parlamentares</div>', unsafe_allow_html=True)
        ordem_partidos = ["BE","CDU","L","PS","PAN","AD", "IL", "CH"]
        df_filtrado["Ordem"] = df_filtrado["Partido"].apply(lambda x: ordem_partidos.index(x) if x in ordem_partidos else len(ordem_partidos))
        df_filtrado = df_filtrado.sort_values("Ordem").reset_index(drop=True)
        # Gráfico
        fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))
        #ax = fig.add_axes([0.05, 0.25, 0.9, 0.7])  # [esquerda, baixo, largura, altura]
        
        #plt.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)  # Deixa espaço à esquerda

        # Dados para gráfico
        valores = df_filtrado["Mandatos"]
        #valores=valores/valores.sum()*100  # Normalizar para percentagem
        #valores = valores.round(1)  # Arredondar para 1 decimal

        partidos = df_filtrado["Partido"]
        cores = df_filtrado["Cor"]
        logos_base64 = df_filtrado["Simbolo"]  # já em formato base64

        # Semicírculo
        angle_start = 180
        angle_span = 180
        total = sum(valores)
        angles = np.cumsum([0] + list(valores / total * angle_span))
        r = 1.5
        inner_r = 0.8

        # Lista com fatores de ajuste (um por partido)
        # 1.0 é a distância padrão. Aumenta para afastar, diminui para aproximar.
        ajustes_distancia = {
            'BE': 1.1,
            'CDU': 1.1,
            'L': 1.1,
            'PS': 1.1,
            'PAN': 1.1,
            'AD': 1.1,
            'IL': 1.1,
            'CH': 1.1
        }

        for i, (v, p, c, logo_b64) in enumerate(zip(valores, partidos, cores, logos_base64)):
            if v == 0:
                continue  # Ignorar partidos com 0 mandatos
            
            theta1 = angle_start - angles[i]
            theta2 = angle_start - angles[i+1]
            wedge = plt.matplotlib.patches.Wedge((0, 0), r, theta2, theta1, width=r-inner_r, facecolor=c, edgecolor='white')
            ax.add_patch(wedge)

            angle = np.deg2rad((theta1 + theta2) / 2)
            x_middle, y_middle = r * np.cos(angle), r * np.sin(angle)

            # Ajuste individual da distância
            fator = ajustes_distancia.get(p, 1.0)
            x_outer, y_outer = fator * r * np.cos(angle), fator * r * np.sin(angle)

            #ax.plot([x_middle, x_outer], [y_middle, y_outer], color='gray', linewidth=0.6)

            # Inserir imagem fora da fatia
            # try:
            #     logo_data = base64.b64decode(logo_b64.split(",")[1])
            #     img = Image.open(BytesIO(logo_data)).convert("RGBA")
            #     im = OffsetImage(img, zoom=0.3)
            #     ab = AnnotationBbox(im, (x_outer, y_outer + 0.05), frameon=False, box_alignment=(0.3, 0.3))
            #     ax.add_artist(ab)
            # except Exception as e:
            #     print(f"Erro ao carregar símbolo de {p}: {e}")
            

            ax.text(x_outer, y_outer - 0.02, f"{p}", ha='center', va='center', fontsize=9, fontweight='bold',color='white')
            # Gerar gráfico (sem símbolos nem texto dentro do semicírculo)

        # Desenhar legenda personalizada
        for i, (v, p, c, logo_b64) in enumerate(zip(valores, partidos, cores, logos_base64)):
            if v == 0:
                continue  # Ignorar partidos com 0 mandatos
            x_legenda = 1.9  # ou outro valor mais à direita do gráfico
            y_legenda = 1.5 - i * 0.15

            # Desenhar símbolo
            try:
                logo_data = base64.b64decode(logo_b64.split(",")[1])
                img = Image.open(BytesIO(logo_data)).convert("RGBA")
                im = OffsetImage(img, zoom=0.3)
                ab = AnnotationBbox(im, (x_legenda, y_legenda), frameon=False, box_alignment=(0, 0.5))
                ax.add_artist(ab)
            except Exception as e:
                print(f"Erro ao carregar símbolo de {p}: {e}")

            # Texto com partido e valor
            ax.text(x_legenda + 0.15, y_legenda, f"{p}: {int(round(v))}", fontsize=9, va='center')
            #fig.text(0.1, y_legenda, f"{p}: {int(round(v))}%", fontsize=9, va='center')

            # Texto com valor (sem casas decimais)
        
            ax.set_xlim(-2, 2)
            ax.set_ylim(0, 2)
            ax.axis("off")

        st.pyplot(fig, transparent=True)

with tabs[5]:
    dataset = pd.read_csv('data/evolucao.csv', sep=';',encoding='utf-8-sig')
    
    # Definir as cores para cada partido
    dataset['Visão'] = dataset['Visão'].apply(normalizar)
    tipo_selecionado = normalizar(tipo_selecionado)
    dataset = dataset[dataset['Visão'] == tipo_selecionado]

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
            
        dados_partido = dataset[dataset['Partido'] == partido].sort_values(['Ano','Partido'])
        
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
            linewidth=2 , # Espessura da linha
            marker='o' 
        )
        
        # Configurações do gráfico
        axs[i].tick_params(axis='x', rotation=45)
        axs[i].set_ylabel('Percentual (%)')
        #axs[i].set_xlabel('Ano')
        axs[i].set_ylim(0, 45)  # Fixar a escala do eixo y entre 0 e 45
        axs[i].grid(True, linestyle='--', alpha=0.5)
        axs[i].set_title(partido, pad=40)  # Adicionar espaço para a imagem

        for x, y in zip(dados_partido['Ano'], dados_partido['Percentual']):
            axs[i].text(
            x, y + 1,  # Posição acima do ponto
            f"{y:.1f}%",  # Formato do texto
            ha='center', va='bottom', fontsize=8
    )
    # Esconder subplots vazios se houver menos de 9 partidos
    
    for j in range(len(partidos), len(axs)):
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
    st.pyplot(fig5, transparent=True)
