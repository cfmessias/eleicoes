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
from matplotlib.patches import Patch
# =======================
# Gráficos
# =======================import matplotlib.pyplot as plt


def plot_hemiciclo_parlamentar(df, ordem_partidos, ajustes_distancia=None):
    if ajustes_distancia is None:
        ajustes_distancia = {p: 1.1 for p in ordem_partidos}

    # Ordenar os partidos conforme lista definida
    df["Ordem"] = df["Partido"].apply(lambda x: ordem_partidos.index(x) if x in ordem_partidos else len(ordem_partidos))
    df = df.sort_values("Ordem").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))

    valores = df["Mandatos"]
    partidos = df["Partido"]
    cores = df["Cor"]
    logos_base64 = df["Simbolo"]

    angle_start = 180
    angle_span = 180
    total = sum(valores)
    angles = np.cumsum([0] + list(valores / total * angle_span))
    r, inner_r = 1.5, 0.8

    for i, (v, p, c, logo_b64) in enumerate(zip(valores, partidos, cores, logos_base64)):
        if v == 0:
            continue
        theta1 = angle_start - angles[i]
        theta2 = angle_start - angles[i + 1]

        wedge = plt.matplotlib.patches.Wedge((0, 0), r, theta2, theta1,
                                             width=r - inner_r, facecolor=c, edgecolor='white')
        ax.add_patch(wedge)

        angle = np.deg2rad((theta1 + theta2) / 2)
        fator = ajustes_distancia.get(p, 1.0)
        x_outer, y_outer = fator * r * np.cos(angle), fator * r * np.sin(angle)

        ax.text(x_outer, y_outer - 0.02, p, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

    # Legenda com símbolos e mandatos
    for i, (v, p, c, logo_b64) in enumerate(zip(valores, partidos, cores, logos_base64)):
        if v == 0:
            continue
        x_legenda = 1.9
        y_legenda = 1.5 - i * 0.15

        try:
            logo_data = base64.b64decode(logo_b64.split(",")[1])
            img = Image.open(BytesIO(logo_data)).convert("RGBA")
            im = OffsetImage(img, zoom=0.3)
            ab = AnnotationBbox(im, (x_legenda, y_legenda), frameon=False, box_alignment=(0, 0.5))
            ax.add_artist(ab)
        except Exception as e:
            print(f"Erro ao carregar símbolo de {p}: {e}")

        ax.text(x_legenda + 0.15, y_legenda, f"{p}: {int(round(v))}", fontsize=9, va='center')

    ax.set_xlim(-2, 2)
    ax.set_ylim(0, 2)
    ax.axis("off")
    plt.tight_layout()
    return fig


def desenhar_sombra_barras(ax, valores, deslocamento=0.1, cor='gray', alpha=0.4, largura=0.8):
    """
    Adiciona sombras às barras de um gráfico.

    Args:
        ax (matplotlib.axes.Axes): Eixo onde as barras serão desenhadas.
        valores (list or Series): Altura das barras.
        deslocamento (float): Deslocamento horizontal da sombra.
        cor (str): Cor da sombra.
        alpha (float): Transparência da sombra.
        largura (float): Largura da barra de sombra.
    """
    for i, v in enumerate(valores):
        ax.bar(
            i + deslocamento,
            v,
            color=cor,
            alpha=alpha,
            width=largura,
            zorder=0
        )


def plot_bar_chart_comparativo(df, coluna_valores, formato=None, legenda=None, info_extra=None, n=None, ano_ordem=2025, ano_esbatido=2024):
  

    # Converter ano para inteiro
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')

    # Obter anos únicos ordenados
    anos = sorted(df['Ano'].dropna().unique())

    # Pivot: Partido x Ano
    df_pivot = df.pivot(index='Partido', columns='Ano', values=coluna_valores).fillna(0)

    # Obter cores
    cores = df.drop_duplicates('Partido').set_index('Partido')['Cor']

    # Ordenar partidos pelo valor do ano_ordem
    if ano_ordem in df_pivot.columns:
        df_pivot = df_pivot.sort_values(by=ano_ordem, ascending=False)

    partidos = df_pivot.index.tolist()
    x = range(len(partidos))
    largura_total = 0.9
    largura_barra = largura_total / len(anos)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, ano in enumerate(anos):
        valores = df_pivot[ano].values
        posicoes = [p - largura_total/2 + i * largura_barra + largura_barra/2 for p in x]
        
        # Cores com esbatido se for ano_esbatido
        alpha = 0.5 if ano == ano_esbatido else 1.0
        cor_barras = [cores.get(p, '#888888') for p in partidos]

        barras = ax.bar(posicoes, valores, width=largura_barra,
                        label=str(int(ano)),
                        color=cor_barras,
                        alpha=alpha,
                        zorder=2)

        # Etiquetas nas barras
        if formato == "percentagem":
            ax.bar_label(barras, fmt="%.1f%%", padding=3, fontsize=11)
        else:
            ax.bar_label(barras, fmt="%.0f", padding=3, fontsize=11)

    # Eixo X
    ax.set_xticks(x)
    ax.set_xticklabels(partidos, rotation=45, ha='right')
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Estilo
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=1)

    # Legenda
    if legenda:
        legend_text = f"{legenda}"
        if info_extra:
            legend_text += f"\n{info_extra}"
        dummy_patch = Patch(color='none', label=legend_text)
        leg = ax.legend(handles=[dummy_patch], loc="upper right", fontsize=18 if n=="2" else 22)
        for text in leg.get_texts():
            text.set_color("white")
        leg.get_frame().set_facecolor('none')
        leg.get_frame().set_edgecolor('none')
    else:
        ax.legend(title="Ano", fontsize=12)

    plt.tight_layout()
    return fig

<<<<<<< HEAD
def plot_previsoes(dataset):
    # Construir dicionário de cores a partir do dataset
    cores_partidos = dict(zip(dataset['Partido'], dataset['Cor']))

    # Anos únicos
    anos = sorted(dataset['Ano'].unique())
    n_anos = len(anos)

    # Layout: máx. 3 colunas
    n_cols = min(3, n_anos)
    n_rows = -(-n_anos // n_cols)  # Arredondar para cima

    # Tamanho proporcional
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows), facecolor='#a5bbc9')
    axs = np.array(axs).flatten() if n_anos > 1 else [axs]

    for i, ano in enumerate(anos):
        ax = axs[i]
        dados_ano = dataset[dataset['Ano'] == ano].sort_values('Percentual', ascending=False)

        partidos = dados_ano['Partido']
        percentuais = dados_ano['Percentual']
        cores = [cores_partidos.get(p, '#888888') for p in partidos]

        ax.bar(partidos, percentuais, color=cores)

        # Adicionar rótulos
        for j, (x, y) in enumerate(zip(partidos, percentuais)):
            ax.text(j, y + 0.5, f"{y:.1f}%", ha='center', va='bottom', fontsize=8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(f'{ano}', fontsize=12, fontweight='bold')
        ax.set_ylim(0, max(percentuais) * 1.2)
        ax.tick_params(axis='x', rotation=45)
        ax.set_ylabel("% Voto")
        ax.set_facecolor('#f0f0f0')
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    # Esconder eixos não usados
    for j in range(len(anos), len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    st.pyplot(fig, transparent=True)
=======

>>>>>>> 10c95e3664101517b9ce91af0984c91a60efbd53

def plot_bar_chart(df, coluna_valores=None, formato=None, legenda=None, info_extra=None,n=None):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Ordenar pelo valor
    df_ord = df.sort_values(by=coluna_valores, ascending=False).reset_index(drop=True)

    # Sombra
    desenhar_sombra_barras(ax, df_ord[coluna_valores])

    # Barras principais
    bars = ax.bar(
        range(len(df_ord)), 
        df_ord[coluna_valores], 
        color=df_ord["Cor"], 
        width=0.8, 
        zorder=1
    )

    # Texto nas barras
    if formato == "percentagem":
        ax.bar_label(bars, fmt="%.2f%%", padding=3, fontsize=14)
    else:
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=14)

    # Rótulos eixo X
    ax.set_xticks(range(len(df_ord)))
    ax.set_xticklabels(df_ord["Partido"], rotation=45, ha='right')

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Legenda "falsa"
    if legenda:
        legend_text = f"{legenda}"
        if info_extra:
            legend_text += f"\n{info_extra}"
        dummy_patch = Patch(color='none', label=legend_text)
        if n=="2":
            legend = ax.legend(handles=[dummy_patch], title="", loc="upper right",fontsize=18)
        else:
            legend = ax.legend(handles=[dummy_patch], title="", loc="upper right",fontsize=22)

        for text in legend.get_texts():
            text.set_color("white")
        legend.get_frame().set_facecolor('none')
        legend.get_frame().set_edgecolor('none')

    plt.tight_layout()
    return fig

def base64_para_imagem(base64_string):
            if pd.isna(base64_string):
                return None
            # Remover o prefixo, se existir
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            img_data = base64.b64decode(base64_string)
            img = Image.open(BytesIO(img_data))
            return img

def plot_metricas_com_simbolos2(
    dataset,
    coluna_valor=None,
    titulo_eixo_y=None,
    ylim_max=None,
    max_categorias=9,
    modo=None
):
    # Inferir modo se não for fornecido
    if modo is None:
        if 'Ano' in dataset.columns:
            modo = 'previsao'
        elif 'Partido' in dataset.columns:
            modo = 'partido'
        else:
            raise ValueError("Não foi possível inferir o modo (nem 'partido' nem 'previsao').")

    # Inferir coluna_valor
    if coluna_valor is None:
        if 'Percentual' in dataset.columns:
            coluna_valor = 'Percentual'
        elif 'Votos' in dataset.columns:
            coluna_valor = 'Votos'
        else:
            raise ValueError("Não foi possível inferir a coluna de valores ('Percentual' ou 'Votos').")

    # Inferir título do eixo Y
    if titulo_eixo_y is None:
        if coluna_valor == 'Percentual':
            titulo_eixo_y = 'Percentual (%)'
        elif coluna_valor == 'Votos':
            titulo_eixo_y = 'N.º de Votos'
        else:
            titulo_eixo_y = coluna_valor

  
    #categorias = dataset[modo].unique()
    if modo == 'partido':
        coluna_categoria = 'Partido'
    elif modo == 'previsao':
        coluna_categoria = 'Ano'
    else:
        raise ValueError(f"Modo '{modo}' inválido. Use 'partido' ou 'previsao'.")

    categorias = dataset[coluna_categoria].unique()

    fig, axs = plt.subplots(3, 3, figsize=(18, 12))  # até 9 gráficos
    axs = axs.flatten()

    for i, cat in enumerate(categorias):
        if i >= max_categorias:
            break

        dados_cat = dataset[dataset[modo] == cat].sort_values(['Ano', 'Partido'])
        cor = dados_cat['Cor'].iloc[0] if 'Cor' in dados_cat.columns else '#888888'

        # Escolher eixo X e título
        eixo_x = 'Ano' if modo == 'partido' else 'Partido'
        valores = dados_cat[coluna_valor]

        barras = axs[i].bar(
            dados_cat[eixo_x],
            valores,
            color=cor if modo == 'partido' else [dados_cat[dados_cat['Partido'] == p]['Cor'].iloc[0] for p in dados_cat['Partido']],
            alpha=0.8,
            width=0.6
        )

        axs[i].tick_params(axis='x', rotation=45)
        axs[i].set_ylabel(titulo_eixo_y)
        if ylim_max:
            axs[i].set_ylim(0, ylim_max)
        axs[i].grid(True, linestyle='--', alpha=0.5, axis='y')
        axs[i].set_title(cat, pad=40)

        for bar, y_val in zip(barras, valores):
            height = bar.get_height()
            texto = f"{y_val:.1f}%" if 'Percentual' in coluna_valor else f"{int(y_val)}"
            axs[i].text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.5,
                texto,
                ha='center', va='bottom', fontsize=8
            )

    for j in range(len(categorias), len(axs)):
        fig.delaxes(axs[j])

    # Adicionar logótipos
    for i, cat in enumerate(categorias):
        if i >= max_categorias or axs[i] not in fig.axes:
            continue

        dados_cat = dataset[dataset[modo] == cat]
        if modo == 'partido':
            imagem_base64 = dados_cat['Simbolo'].iloc[0]
        else:
            imagem_base64 = dados_cat.drop_duplicates('Partido')['Simbolo'].iloc[0]

        img = base64_para_imagem(imagem_base64)

        if img:
            pos = axs[i].get_position()
            img_width = 0.06
            img_height = 0.06
            img_y = pos.y1 - 0.05 - 0.02 * (i // 3)
            img_x = pos.x0 + (pos.width - img_width) / 2
            ax_img = fig.add_axes([img_x, img_y, img_width, img_height])
            ax_img.imshow(img)
            ax_img.axis('off')

    plt.subplots_adjust(top=0.85, hspace=0.9)
    st.pyplot(fig, transparent=True)

def plot_bar_chart_comparativo_simbolos(df, coluna_valores, formato=None, legenda=None, info_extra=None, n=None, ano_ordem=2025, ano_esbatido=2024):
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
    anos = sorted(df['Ano'].dropna().unique())
    df_pivot = df.pivot(index='Partido', columns='Ano', values=coluna_valores).fillna(0)

    info_partidos = df.drop_duplicates('Partido').set_index('Partido')[['Cor', 'Simbolo']]
    cores = info_partidos['Cor']
    simbolos = info_partidos['Simbolo']

    if ano_ordem in df_pivot.columns:
        df_pivot = df_pivot.sort_values(by=ano_ordem, ascending=False)

    partidos = df_pivot.index.tolist()
    x = range(len(partidos))
    largura_total = 0.9
    largura_barra = largura_total / len(anos)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, ano in enumerate(anos):
        valores = df_pivot[ano].values
        posicoes = [p - largura_total/2 + i * largura_barra + largura_barra/2 for p in x]
        alpha = 0.5 if ano == ano_esbatido else 1.0
        cor_barras = [cores.get(p, '#888888') for p in partidos]

        barras = ax.bar(posicoes, valores, width=largura_barra,
                        label=str(int(ano)),
                        color=cor_barras,
                        alpha=alpha,
                        zorder=2)

        if formato == "percentagem":
            ax.bar_label(barras, fmt="%.1f%%", padding=3, fontsize=11)
        else:
            ax.bar_label(barras, fmt="%.0f", padding=3, fontsize=11)

    # Substituir siglas por imagens
    ax.set_xticks(x)
    ax.set_xticklabels([""] * len(partidos))  # esconde texto
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Imagens como labels
    for i, partido in enumerate(partidos):
        img = base64_para_imagem(simbolos.get(partido))
        if img:
            imagebox = OffsetImage(img, zoom=0.2)
            ab = AnnotationBbox(imagebox, (i, -0.05 * df_pivot.values.max()), frameon=False, box_alignment=(0.5, 1))
            ax.add_artist(ab)
        else:
            ax.text(i, -0.05 * df_pivot.values.max(), partido, ha='center', va='top', fontsize=8)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=1)

    if legenda:
        legend_text = f"{legenda}"
        if info_extra:
            legend_text += f"\n{info_extra}"
        dummy_patch = Patch(color='none', label=legend_text)
        leg = ax.legend(handles=[dummy_patch], loc="upper right", fontsize=18 if n == "2" else 22)
        for text in leg.get_texts():
            text.set_color("white")
        leg.get_frame().set_facecolor('none')
        leg.get_frame().set_edgecolor('none')
    else:
        ax.legend(title="Ano", fontsize=12)

    plt.tight_layout()
    return fig

def plot_metricas_com_simbolos(
    dataset,
    coluna_valor='Percentual',
    titulo_eixo_y='Percentual (%)',
    ylim_max=None,
    max_partidos=9
    ):

    partidos = dataset['Partido'].unique()
    fig, axs = plt.subplots(3, 3, figsize=(18, 12))  # até 9 partidos
    axs = axs.flatten()

    for i, partido in enumerate(partidos):
        if i >= max_partidos:
            break

        dados_partido = dataset[dataset['Partido'] == partido].sort_values(['Ano', 'Partido'])
        cor = dados_partido['Cor'].iloc[0] if 'Cor' in dados_partido.columns else '#888888'

        valores = dados_partido[coluna_valor]

        barras = axs[i].bar(
            dados_partido['Ano'],
            valores,
            color=cor,
            alpha=0.8,
            width=0.6
        )
          # Remover moldura
        #for spine in axs[i].spines.values():
        #    spine.set_visible(False)
        # OU: mudar cor
        # for spine in axs[i].spines.values():
        #     spine.set_edgecolor('#cccccc')
        #  moldura apenas em certas direções (ex: só à esquerda e em baixo)
        axs[i].spines['top'].set_visible(False)
        axs[i].spines['right'].set_visible(False)

        axs[i].tick_params(axis='x', rotation=45)
        axs[i].set_ylabel(titulo_eixo_y)
        if ylim_max:
            axs[i].set_ylim(0, ylim_max)
        axs[i].grid(True, linestyle='--', alpha=0.5, axis='y')
        axs[i].set_title(partido, pad=40)

        for bar, y_val in zip(barras, valores):
            height = bar.get_height()
            axs[i].text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.5,
                f"{y_val:.1f}%" if 'Percentual' in coluna_valor else f"{int(y_val)}", 
                ha='center', va='bottom', fontsize=8
            )

    for j in range(len(partidos), len(axs)):
        fig.delaxes(axs[j])

    # Adicionar logótipos
    for i, partido in enumerate(partidos):
        if i >= max_partidos or axs[i] not in fig.axes:
            continue

        dados_partido = dataset[dataset['Partido'] == partido]
        imagem_base64 = dados_partido['Simbolo'].iloc[0]
        img = base64_para_imagem(imagem_base64)

        if img:
            pos = axs[i].get_position()
            img_width = 0.06
            img_height = 0.06

            if i < 3:
                img_y = pos.y1 - 0.05
            elif i < 6:
                img_y = pos.y1 - 0.07
            else:
                img_y = pos.y1 - 0.09

            img_x = pos.x0 + (pos.width - img_width) / 2
            ax_img = fig.add_axes([img_x, img_y, img_width, img_height])
            ax_img.imshow(img)
            ax_img.axis('off')

    plt.subplots_adjust(top=0.85, hspace=0.9)
    st.pyplot(fig, transparent=True)


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
    <div style="height: 30px;"><br></div>
    """, unsafe_allow_html=True)

def mostrar_abstencao_brancos_texto(df):
    abstencao = df['Abstenção'].values[0] * 100
    brancos = df['Brancos'].values[0]
    brancos_formatado = f"{brancos / 1000:.1f}K"
    return f"Abstenção: {abstencao:.2f}%\nBrancos: {brancos_formatado}"

def normalizar(texto):
    return unicodedata.normalize('NFC', texto)

def mostrar_titulo_custom(texto):
    custom_font_css = """
    <style>
        .custom-subheader {
            font-family: 'Arial', sans-serif;
            font-size: 18px !important;
            font-weight: bold;
            text-align: left !important;
            text-shadow: 2px 2px 5px white !important;
            color: darkblue !important;
        }
    </style>
    """
    st.markdown(custom_font_css, unsafe_allow_html=True)
    st.markdown(f'<div class="custom-subheader">{texto}</div>', unsafe_allow_html=True)
	
def formatar_em_k(numero):
    # Dividir por 1.000, formatar com uma casa decimal e adicionar o sufixo K
    return f"{numero / 1000:.1f}K"
