import streamlit as st


def aplicar_filtros_sidebar(df,modo=None):
    # Injetar CSS
    css = """
    <style>
        [data-testid="stSidebar"] {
            min-width: 250px;
            max-width: 350px;
            background-color: #f8f9fa;
            padding: 1rem;
            border-right: 1px solid #dee2e6;
            background: linear-gradient(to left , #cbd3d6 ,#137ea8);
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
            background: linear-gradient(to left , #137ea8, #cbd3d6);
        }

        [data-testid="stSidebar"] h2 {
            font-size: 20px;
            color: white;
            font-weight: bold;
            text-align: left;
            margin-bottom: 20px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Título da sidebar
    st.sidebar.markdown("## Filtros")

    # Limpeza da coluna "Visão"
    df['Visão'] = df['Visão'].astype(str).str.strip().str.replace('\u200b', '').str.replace('\xa0', '').str.normalize('NFKD')

    # Filtros
   
    
    ano_selecionado = None
<<<<<<< HEAD
    if modo == '📊Previsões':
=======
    if modo == 'Previsões':
>>>>>>> 10c95e3664101517b9ce91af0984c91a60efbd53
        anos = sorted(df['Ano'].unique(), reverse=True)
        ano_selecionado = st.sidebar.selectbox("Seleciona o ano", anos, key='ano_previsoes')
           
    tipo_selecionado = None
<<<<<<< HEAD
    if modo == '📊Previsões':
=======
    if modo == 'Previsões':
>>>>>>> 10c95e3664101517b9ce91af0984c91a60efbd53
        tipos = df['Visão'].unique()
        tipo_selecionado = st.sidebar.selectbox("Seleciona o tipo de previsão", tipos, key='tipo_previsoes')

    distritos = sorted(df['Distrito'].unique())
    distrito_selecionado = st.sidebar.selectbox("Seleciona o distrito", distritos, key='distrito_previsoes')
    
    #tipo_selecionado = st.sidebar.selectbox("Seleciona o tipo de previsão", tipos, key='tipo_previsoes')
    #distrito_selecionado = st.sidebar.selectbox("Seleciona o distrito", distritos, key='distrito_previsoes')

    return ano_selecionado, tipo_selecionado, distrito_selecionado



