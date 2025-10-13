import streamlit as st
from utils import (
    check_password, init_connection, fetch_evaluation_stats, 
    fetch_tweets_to_evaluate, update_tweet_evaluation
)

if not check_password():
    st.stop()

st.set_page_config(page_title="Avaliação de Tweets", page_icon="🗳️", layout="wide")
st.title("🗳️ Ferramenta de Avaliação de Tweets")
st.markdown("---")

conn = init_connection()

if conn:
    stats = fetch_evaluation_stats(conn)
    if stats:
        total_geral, total_avaliados, total_true, total_false = stats.values()
        percent_avaliados = (total_avaliados / total_geral * 100) if total_geral > 0 else 0
        percent_true = (total_true / total_avaliados * 100) if total_avaliados > 0 else 0
        percent_false = (total_false / total_avaliados * 100) if total_avaliados > 0 else 0
        
        st.subheader("Resumo das Avaliações")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total de Tweets", f"{total_geral:,}".replace(",", "."))
        col2.metric("Avaliados", f"{total_avaliados:,}".replace(",", "."))
        col3.metric("% Avaliados", f"{percent_avaliados:.1f}%")
        col4.metric("% Positivos", f"{percent_true:.1f}%")
        col5.metric("% Negativos", f"{percent_false:.1f}%")

    st.markdown("---")

    st.subheader("Área de Avaliação")
    
    if 'tweets' not in st.session_state:
        st.session_state.tweets = fetch_tweets_to_evaluate(conn)
        st.session_state.current_index = 0

    if not st.session_state.tweets or st.session_state.current_index >= len(st.session_state.tweets):
        st.success("✨ Parabéns! Nenhum tweet pendente de avaliação.")
        if st.button("Buscar novos tweets"):
            st.session_state.pop('tweets', None)
            st.rerun()
    else:
        current_tweet = st.session_state.tweets[st.session_state.current_index]
        
        st.markdown(f"> {current_tweet['texto_tweet']}")
        
        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("Positivo 👍", use_container_width=True, type="primary"):
            update_tweet_evaluation(conn, current_tweet['id_tweet'], True)
            st.session_state.current_index += 1
            st.rerun()

        if btn_col2.button("Negativo 👎", use_container_width=True):
            update_tweet_evaluation(conn, current_tweet['id_tweet'], False)
            st.session_state.current_index += 1
            st.rerun()
    
