import streamlit as st
import pandas as pd

# Define o título principal da página
st.title("🌎 Painel de Controle do PIB")

# Mensagem informativa sobre a fonte dos dados
st.info("Consulte os dados do PIB no site do Banco Mundial. Atenção: os dados disponíveis atualmente vão apenas até 2022.")

# Supondo que 'gdp_df' é o seu DataFrame já carregado
# Substitua esta parte pela sua função de carregar dados, se necessário
# gdp_df = obter_dados_gdp()

if 'gdp_df' in locals():
    # Define os anos mínimo e máximo disponíveis nos dados
    valor_minimo = int(gdp_df['Ano'].min())
    valor_maximo = int(gdp_df['Ano'].max())

    # Controlo deslizante (Slider) para selecionar o intervalo de anos
    anos_selecionados = st.slider(
        "Em quais anos você tem interesse?",
        min_value=valor_minimo,
        max_value=valor_maximo,
        value=(valor_minimo, valor_maximo)
    )

    # Obter a lista de países
    paises = gdp_df['Código do país'].unique()

    # Seleção múltipla de países
    paises_selecionados = st.multiselect(
        "Quais países você gostaria de ver?",
        options=paises,
        default=["DEU", "FRA", "GBR", "PRT", "USA"]
    )

    if not paises_selecionados:
        st.warning("Selecione pelo menos um país para visualizar os dados.")