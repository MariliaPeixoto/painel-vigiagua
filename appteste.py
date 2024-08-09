import pandas as pd
import streamlit as st
import plotly.express as px
import geopandas as gpd
from unidecode import unidecode

# Configurações da página
st.set_page_config(
    page_title="VIGIAGUA RS",
    page_icon=":potable_water:",
    layout="wide",
    initial_sidebar_state='collapsed'
)
col1, col2, col3 = st.columns([1,4,1])

col3.image('https://github.com/andrejarenkow/csv/blob/master/logo_cevs%20(2).png?raw=true', width=150)
col2.title('VIGIAGUA RS')
col1.image('https://github.com/andrejarenkow/csv/blob/master/logo_estado%20(3)%20(1).png?raw=true', width=230)

# Função para carregar dados
@st.cache_data
def load_data():
    dados_2024 = pd.read_csv('https://drive.google.com/uc?export=download&id=1aFmCeDug7eJRhTxSwIXxqw_hYHeUwKGC', sep=';')
    dados_nao_validadas = pd.read_excel('https://drive.google.com/uc?export=download&id=1-DGZAo4cCk0jIVnmDkKRBVWDtWfaBAF2')
    muni = gpd.read_file('https://raw.githubusercontent.com/andrejarenkow/geodata/main/municipios_rs_CRS/RS_Municipios_2021.json')
    ref_muni = pd.read_csv('https://raw.githubusercontent.com/andrejarenkow/csv/master/Munic%C3%ADpios%20RS%20IBGE6%20Popula%C3%A7%C3%A3o%20CRS%20Regional%20-%20P%C3%A1gina1.csv')
    
    return dados_2024, dados_nao_validadas, muni, ref_muni

dados_2024, dados_nao_validadas, muni, ref_muni = load_data()

# Processar dados
def preprocess_data(dados_2024, dados_nao_validadas, muni, ref_muni):
    dados_2024['Regional de Saúde'] = dados_2024['Regional de Saúde'].str.zfill(7)
    dados_nao_validadas['Regional de Saúde'] = dados_nao_validadas['Regional de Saúde'].astype(str).str.zfill(7)
    dados_nao_validadas['Data da coleta'] = pd.to_datetime(dados_nao_validadas['Data da coleta'], errors='coerce')
    dados_nao_validadas['Ano'] = dados_nao_validadas['Data da coleta'].dt.year

    muni['NM_MUN'] = muni['NM_MUN'].apply(lambda x: unidecode(x).upper())
    ref_muni['CRS'] = (ref_muni['CRS'].astype(str).str.zfill(2) + 'ª CRS')
    ref_muni['Município'] = ref_muni['Município'].apply(lambda x: unidecode(x).upper())

    return dados_2024, dados_nao_validadas, muni, ref_muni

dados_2024, dados_nao_validadas, muni, ref_muni = preprocess_data(dados_2024, dados_nao_validadas, muni, ref_muni)

# Função para atualizar filtro
def update_filters(dados_2024, ref_muni, muni, parametro):
    opcoes_crs = sorted(dados_2024['Regional de Saúde'].unique())
    opcoes_crs.insert(0, 'Todas')
    crs_selecionada = st.selectbox(label='Selecione a CRS', options=opcoes_crs)

    ano_selecionado = st.multiselect(
        label='Selecione o ano',
        options=sorted(dados_2024['Ano'].unique()),
        default=sorted(dados_2024['Ano'].unique())
    )

    forma_abastecimento_selecionada = st.multiselect(
        label='Selecione o tipo da forma',
        options=sorted(dados_2024['Tipo da Forma de Abastecimento'].unique()),
        default=sorted(dados_2024['Tipo da Forma de Abastecimento'].unique())
    )

    parametro = st.selectbox(label='Selecione o parâmetro', options=dados_2024['Parâmetro'].unique(), index=3)

    return crs_selecionada, ano_selecionado, forma_abastecimento_selecionada, parametro

crs_selecionada, ano_selecionado, forma_abastecimento_selecionada, parametro = update_filters(dados_2024, ref_muni, muni, parametro)

# Filtrar dados
def filter_data(dados_2024, ref_muni, muni, crs_selecionada):
    if crs_selecionada != 'Todas':
        dados_2024 = dados_2024[dados_2024['Regional de Saúde'] == crs_selecionada]
        lista_municipios_muni = ref_muni[ref_muni['CRS'] == crs_selecionada]['Município']
        muni = muni[muni['NM_MUN'].isin(lista_municipios_muni)]
        zoom_ini = 7
    else:
        zoom_ini = 5.5

    return dados_2024, muni, zoom_ini

dados_2024, muni, zoom_ini = filter_data(dados_2024, ref_muni, muni, crs_selecionada)

# Cálculo porcentagem de insatisfatórios
def calculate_metrics(dados_2024, dados_nao_validadas):
    total_rows = len(dados_2024)
    inadequate_rows = len(dados_2024[dados_2024['Status'] == 'Inadequado'])
    percentage = round(inadequate_rows / total_rows * 100, 2)

    amostras_nao_validadas_total = len(dados_nao_validadas)
    numero_de_amostras = dados_2024['Número da amostra'].nunique()

    return percentage, amostras_nao_validadas_total, numero_de_amostras

percentage, amostras_nao_validadas_total, numero_de_amostras = calculate_metrics(dados_2024, dados_nao_validadas)

# Exibição de métricas
with col2:
    st.metric(label='Análises insatisfatórias', value=f'{percentage}%')

with col3:
    st.metric(label='Total de amostras', value=f'{numero_de_amostras}')

with col4:
    st.metric(label='Amostras não validadas', value=f'{amostras_nao_validadas_total}')

# Ajuste de estilo CSS
st.markdown(
    """
    <style>
    .stMetric {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cálculo porcentagem de insatisfatórios
def categorize_data(dados):
    dados['Insatisfatório %'] = ((dados['Inadequado'] / (dados['Adequado'] + dados['Inadequado'])) * 100).round(2)

    def categorizar(i):
        if i == 0:
            return '0 %'
        elif 0 < i <= 10:
            return '1 % - 10 %'
        elif 10 < i <= 20:
            return '11 % - 20 %'
        elif 20 < i <= 30:
            return '21 % - 30 %'
        else:
            return 'mais que 30 %'

    dados['Categorias'] = dados['Insatisfatório %'].apply(categorizar)
    return dados

# Juntar tabelas e preparar para o mapa
def prepare_map_data(muni, dados):
    tabela_mapa = muni.merge(dados, left_on='NM_MUN', right_on='Município', how='left').fillna('Sem dados')
    min_x, min_y, max_x, max_y = tabela_mapa.total_bounds
    centro_x = (min_x + max_x) / 2
    centro_y = (min_y + max_y) / 2
    return tabela_mapa, centro_x, centro_y

dados = pd.pivot_table(dados_2024[dados_2024['Parâmetro'] == parametro], index='Município', columns='Status', aggfunc='size').reset_index().fillna(0)
dados = categorize_data(dados)
tabela_mapa, centro_x, centro_y = prepare_map_data(muni, dados)

# Paleta de cores
cores = {
    'Cloro residual livre (mg/L)': {
        'Sem dados': '#d2d2d2',
        '0 %': '#EEF3AD',
        '1 % - 10 %': '#ADEBBE',
        '11 % - 20 %': '#75B79E',
        '21 % - 30 %': '#74BEC1',
        'mais que 30 %': '#516091'
    },
    'Escherichia coli': {
        'Sem dados': '#d2d2d2',
        '0 %': '#F7C623',
        '1 % - 10 %': '#de8531',
        '11 % - 20 %': '#b32900',
        '21 % - 30 %': '#6c1305',
        'mais que 30 %': '#330a04'
    },
    'Fluoreto (mg/L)': {
        'Sem dados': '#d2d2d2',
        '0 %': '#B2C9D7',
        '1 % - 10 %': '#9BC3DC',
        '11 % - 20 %': '#6596B4',
        '21 % - 30 %': '#317197',
        'mais que 30 %': '#00517E'
    },
    'Turbidez (uT)': {
        'Sem dados': '#d2d2d2',
        '0 %': '#DCC595',
        '1 % - 10 %': '#B68E56',
        '11 % - 20 %': '#A37940',
        '21 % - 30 %': '#90682F',
        'mais que 30 %': '#5F021F'
    }
}

# Gráfico do mapa
def plot_map(tabela_mapa, centro_x, centro_y, zoom_ini, parametro):
    px.set_mapbox_access_token('pk.eyJ1IjoiYW5kcmUtamFyZW5rb3ciLCJhIjoiY2xkdzZ2eDdxMDRmMzN1bnV6MnlpNnNweSJ9.4_9fi6bcTxgy5mGaTmE4Pw')
    mapa_fig = px.choropleth_mapbox(
        tabela_mapa,
        geojson=tabela_mapa.geometry,
        locations=tabela_mapa.index,
        color='Categorias',
        color_discrete_map=cores[parametro],
        center={'lat': centro_y, 'lon': centro_x},
        zoom=zoom_ini,
        mapbox_style="open-street-map",
        hover_name='NM_MUN',
        hover_data='Insatisfatório %',
        category_orders={'Categorias': ['Sem dados', '0 %', '1 % - 10 %', '11 % - 20 %', '21 % - 30 %', 'mais que 30 %']},
        width=800,
        height=700,
        title=f'{parametro} Insatisfatório %'
    )
    mapa_fig.update_traces(marker_line_width=0.3)
    mapa_fig.update_layout(
        margin={"r": 0, "t": 25, "l": 0, "b": 0},
        mapbox_layers=[dict(
            sourcetype='geojson',
            source='https://raw.githubusercontent.com/andrejarenkow/geodata/main/RS_por_CRS/RS_por_CRS.json',
            color='black',
            type='line',
            line=dict(width=1)
        )]
    )
    st.plotly_chart(mapa_fig)

plot_map(tabela_mapa, centro_x, centro_y, zoom_ini, parametro)

# Gráfico de dispersão
def plot_scatter(dados_crs, parametro):
    fig = px.strip(
        dados_crs.sort_values('Regional de Saúde'),
        x="Regional de Saúde",
        y="Insatisfatório %",
        color="Regional de Saúde",
        hover_name="Município",
        range_y=[-5, 105],
        title='Porcentagem de amostras insatisfatórias por CRS'
    )
    fig.update_layout(
        title={
            'text': f'Porcentagem de amostras insatisfatórias de {parametro} por CRS',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Regional de Saúde',
        yaxis_title='Insatisfatório %',
        showlegend=False
    )
    col2.plotly_chart(fig)

dados_crs = dados_2024[dados_2024['Parâmetro'] == parametro].groupby(['Município', 'Regional de Saúde', 'Status']).size().unstack(fill_value=0).reset_index()
dados_crs = categorize_data(dados_crs)
plot_scatter(dados_crs, parametro)
