import streamlit as st
from utils import check_password, init_connection, fetch_evaluation_stats

if not check_password():
    st.stop()

st.set_page_config(page_title="Levantamento de Dados", page_icon="📊", layout="wide")
st.title("📊 Levantamento e Coleta de Dados")
st.markdown("---")

st.header("Processo de Coleta")
st.write(
    """
    A base de dados para este projeto foi construída através da coleta de tweets em português 
    utilizando as APIs oficiais da plataforma X (antigo Twitter). Foram utilizadas **29 APIs distintas**, 
    cada uma configurada para buscar tweets que continham termos específicos relacionados à saúde mental.
    """
)

st.subheader("Termos Pesquisados")
st.info("ansiedade, depressão, terapia, saúde mental, bem-estar, estresse, burnout, etc.") # Adicione/edite os termos

st.header("Resumo Quantitativo")
conn = init_connection()
if conn:
    stats = fetch_evaluation_stats(conn)
    total_coletado = stats.get('total_geral', 0)
    total_avaliado = stats.get('total_avaliados', 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de APIs Utilizadas", "29")
    col2.metric("Total de Tweets Coletados", f"{total_coletado:,}".replace(",", "."))
    col3.metric("Total de Tweets Avaliados", f"{total_avaliado:,}".replace(",", "."))

