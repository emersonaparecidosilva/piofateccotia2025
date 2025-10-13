# pages/6_🤖_Análise_Não_Supervisionada.py
import streamlit as st
from utils import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Análise Não Supervisionada", page_icon="🤖", layout="wide")
st.title("🤖 Análise de Algoritmos Não Supervisionados")
st.markdown("---")
st.info("Esta seção está em desenvolvimento.")
st.write("O objetivo aqui será aplicar técnicas de clusterização (como K-Means) para identificar grupos e tópicos emergentes no conjunto completo de 3.500 tweets, sem utilizar as avaliações manuais.")