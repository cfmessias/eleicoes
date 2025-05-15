import streamlit as st

def aplicar_estilos():
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
