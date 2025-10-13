# utils.py
import streamlit as st
import psycopg2
import bcrypt
from psycopg2.extras import DictCursor

# --- FUNÇÃO DE LOGIN (COMPARTILHADA) ---
def check_password():
    """Retorna `True` se o usuário estiver logado, `False` caso contrário."""
    if st.session_state.get("logged_in", False):
        return True

    st.title("🔒 Acesso Restrito")
    st.write("Por favor, insira a senha para continuar.")

    try:
        hashed_password = st.secrets["credentials"]["hashed_password"].encode('utf-8')
    except (KeyError, AttributeError):
        st.error("ERRO CRÍTICO: A senha não foi configurada nos segredos da aplicação.")
        st.stop()
    
    with st.form("login_form"):
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    
    return False

# --- FUNÇÕES DE BANCO DE DADOS (COMPARTILHADAS) ---
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["database"]["url"])
    except (psycopg2.OperationalError, KeyError):
        st.error("Erro ao conectar ao banco de dados. Verifique os segredos.")
        return None

def fetch_evaluation_stats(_connection):
    if not _connection: return {}
    with _connection.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT
                COUNT(*) AS total_geral,
                COUNT(avaliacao) AS total_avaliados,
                SUM(CASE WHEN avaliacao = TRUE THEN 1 ELSE 0 END) AS total_true,
                SUM(CASE WHEN avaliacao = FALSE THEN 1 ELSE 0 END) AS total_false
            FROM tweets_avaliacao;
        """)
        return cur.fetchone()

def fetch_tweets_to_evaluate(_connection):
    if not _connection: return []
    with _connection.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id_tweet, texto_tweet FROM tweets_avaliacao WHERE avaliacao IS NULL;")
        return cur.fetchall()

def update_tweet_evaluation(_connection, tweet_id, evaluation: bool):
    if not _connection: return
    with _connection.cursor() as cur:
        cur.execute(
            "UPDATE tweets_avaliacao SET avaliacao = %s, data_atualizacao = NOW() WHERE id_tweet = %s;",
            (evaluation, tweet_id)
        )
        _connection.commit()