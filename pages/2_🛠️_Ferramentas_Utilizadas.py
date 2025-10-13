import streamlit as st
from utils import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Ferramentas Utilizadas", page_icon="🛠️", layout="wide")
st.title("🛠️ Ferramentas e Tecnologias Utilizadas")
st.markdown("---")

st.subheader("Linguagem e Ecossistema")
st.markdown("- **Python:** Linguagem principal para desenvolvimento, análise de dados e machine learning.")
st.markdown("- **Jupyter Notebook (no VS Code):** Ambiente para exploração de dados e treinamento dos modelos.")

st.subheader("Interface e Aplicação Web")
st.markdown("- **Streamlit:** Framework utilizado para construir e implantar a interface web de avaliação e apresentação do projeto.")

st.subheader("Banco de Dados e Coleta")
st.markdown("- **PostgreSQL (no Render):** Banco de dados relacional para armazenar os tweets coletados e suas avaliações.")
st.markdown("- **APIs do Twitter/X:** Utilizadas para a coleta programática dos tweets.")

st.subheader("Análise de Dados e Machine Learning")
st.markdown("- **Pandas:** Biblioteca para manipulação e análise dos dados em formato de DataFrame.")
st.markdown("- **Scikit-learn:** Principal biblioteca para pré-processamento de dados, treinamento e avaliação dos modelos de machine learning.")
st.markdown("- **NLTK (Natural Language Toolkit):** Utilizada para o pré-processamento de texto, como a remoção de stopwords.")
st.markdown("- **Matplotlib & Seaborn:** Bibliotecas para a criação de gráficos e visualizações, como a matriz de confusão.")