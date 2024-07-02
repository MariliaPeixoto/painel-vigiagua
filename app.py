# Importação das bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px

# Configurações da página
st.set_page_config(
    page_title="VIGIAGUA RS",
    page_icon="	:potable_water:",
    layout="wide",
    initial_sidebar_state='collapsed'
)
col1, col2, col3 = st.columns([1,4,1], vertical_alignment="center")

col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=150)
col2.title('VIGIAGUA RS')
col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=230)

# Amostras dos dados abertos
dados_2024 = pd.read_csv('https://drive.google.com/uc?export=download&id=1aFmCeDug7eJRhTxSwIXxqw_hYHeUwKGC', sep=';')

# Cálculo da porcentagem para amostras inadequadas GERAL
total_rows = len(dados_2024)
inadequate_rows = len(dados_2024[dados_2024['Status'] == 'Inadequado'])
percentage = round(inadequate_rows / total_rows * 100, 2)
st.metric(label = 'Análises insatisfatórias', value=f'{percentage}%')

# Número de análises feitas
numero_de_amostras = dados_2024['Número da amostra'].nunique()
st.metric(label = 'Total de amostras', value=f'{numero_de_amostras}')

