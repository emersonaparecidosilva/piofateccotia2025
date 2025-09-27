import streamlit as st
import psycopg2
import bcrypt  # Biblioteca para senhas
from psycopg2.extras import DictCursor

# --- Configuração da Página ---
st.set_page_config(
    page_title="Avaliação de Tweets",
    page_icon="🔒",
    layout="wide"
)

# --- FUNÇÃO DE LOGIN ---
def check_password():
    """Retorna `True` se o usuário estiver logado, `False` caso contrário."""

    # Se o usuário já está logado, não faz nada
    if st.session_state.get("logged_in", False):
        return True

    # --- Layout da Tela de Login ---
    st.title("🔒 Acesso Restrito")
    st.write("Por favor, insira a senha para continuar.")

    # Pega o hash da senha dos segredos da aplicação
    try:
        hashed_password = st.secrets["credentials"]["hashed_password"].encode('utf-8')
    except (KeyError, AttributeError):
        st.error("ERRO CRÍTICO: A senha não foi configurada nos segredos da aplicação.")
        return False
    
    # Cria o formulário de login
    with st.form("login_form"):
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            # Verifica se a senha inserida corresponde ao hash guardado
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                st.session_state["logged_in"] = True
                st.rerun()  # Recarrega o app para mostrar a tela principal
            else:
                st.error("Senha incorreta. Tente novamente.")
    
    return False

# --- FUNÇÕES DE BANCO DE DADOS (sem alteração) ---
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

# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---

# 1. Verifica a senha. Se não estiver logado, para a execução aqui.
if not check_password():
    st.stop()

# 2. Se a senha estiver correta, o código abaixo é executado.
st.sidebar.success("Acesso liberado!")
st.title("📊 Dashboard e Ferramenta de Avaliação de Tweets")

conn = init_connection()

if conn:
    # Seção de Indicadores (Dashboard)
    stats = fetch_evaluation_stats(conn)
    if stats:
        total_geral, total_avaliados, total_true, total_false = stats.values()
        percent_avaliados = (total_avaliados / total_geral * 100) if total_geral > 0 else 0
        percent_true = (total_true / total_avaliados * 100) if total_avaliados > 0 else 0
        percent_false = (total_false / total_avaliados * 100) if total_avaliados > 0 else 0
        
        st.markdown("### Resumo das Avaliações")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("1. Total de Tweets", f"{total_geral:,}".replace(",", "."))
        col2.metric("2. Total Avaliados", f"{total_avaliados:,}".replace(",", "."))
        col3.metric("3. % Avaliados", f"{percent_avaliados:.1f}%")
        col4.metric("4. % Positivos", f"{percent_true:.1f}%")
        col5.metric("5. % Negativos", f"{percent_false:.1f}%")

    st.markdown("---")

    # Seção de Ferramenta de Avaliação
    st.header("Área de Avaliação")
    
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