import streamlit as st
from utils import check_password 

st.set_page_config(
    page_title="PIO 3 - CD 4ºSEM - Fatec Cotia",
    page_icon="👋",
    layout="wide"
)

# A verificação de senha é a primeira coisa a ser feita
if not check_password():
    st.stop() # Bloqueia a execução do restante da página se não estiver logado

# --- Conteúdo da Página de Apresentação ---
st.sidebar.success("Navegue pelas seções do nosso trabalho pela Esquerda.")

st.title("Projeto Integrador: Análise de Sentimentos em Tweets sobre Saúde Mental")

st.markdown("---")

st.header("🎯 Objetivo do Trabalho")
st.write(
    """
    Este projeto tem como objetivo principal desenvolver uma ferramenta de inteligência artificial 
    capaz de classificar o sentimento (positivo ou negativo) expresso em tweets relacionados à 
    saúde mental. Para isso, foi criada uma aplicação para a coleta e avaliação manual dos dados, 
    que serviram de base para o treinamento de diversos algoritmos de aprendizado de máquina.
    """
)

st.markdown("---")

st.header("👥 Equipe e Orientação")
col1, col2 = st.columns(2)

with col1:
    st.subheader("👨‍🏫 Professor Orientador")
    st.write("- Rômulo ")

with col2:
    st.subheader("👩‍💻 Integrantes do Grupo")
    st.write(
        """
        - Emerson Aparecido Silva
        - Fernando Vieira
        - Henrique
        - Lucas Juan
        - Raphael Vieira
        """
    )