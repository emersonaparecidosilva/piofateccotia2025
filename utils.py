import streamlit as st
import psycopg2
import bcrypt
from psycopg2.extras import DictCursor
import re
import unicodedata
import nltk
from nltk.corpus import stopwords

# --- FUNÇÃO DE LOGIN (SEGURANÇA) ---
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

# --- FUNÇÕES DE BANCO DE DADOS (CONEXÃO) ---
@st.cache_resource
def init_connection():
    """Inicializa e cacheia a conexão com o banco de dados."""
    try:
        return psycopg2.connect(st.secrets["database"]["url"])
    except (psycopg2.OperationalError, KeyError):
        st.error("Erro ao conectar ao banco de dados. Verifique os segredos.")
        return None

# --- FUNÇÕES DE BANCO DE DADOS (QUERIES) ---
def fetch_evaluation_stats(_connection):
    """Busca as estatísticas agregadas de avaliação."""
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
    """Busca tweets pendentes de avaliação (onde avaliacao IS NULL)."""
    if not _connection: return []
    with _connection.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id_tweet, texto_tweet FROM tweets_avaliacao WHERE avaliacao IS NULL;")
        return cur.fetchall()

def update_tweet_evaluation(_connection, tweet_id, evaluation: bool):
    """Atualiza a avaliação de um tweet específico no banco."""
    if not _connection: return
    with _connection.cursor() as cur:
        cur.execute(
            "UPDATE tweets_avaliacao SET avaliacao = %s, data_atualizacao = NOW() WHERE id_tweet = %s;",
            (evaluation, tweet_id)
        )
        _connection.commit()

# --- FUNÇÕES DE PRÉ-PROCESSAMENTO DE TEXTO (para o Assistente de IA) ---

@st.cache_data
def get_stopwords_pt():
    """
    Baixa (se necessário) e retorna a lista customizada de stopwords em português.
    Remove palavras de negação da lista padrão.
    """
    try:
        stop_words_pt = set(stopwords.words('portuguese'))
    except LookupError:
        # Se não tiver baixado, baixa automaticamente
        st.info("Baixando pacotes NLTK (stopwords)...")
        nltk.download('stopwords')
        stop_words_pt = set(stopwords.words('portuguese'))
        
    negations = {'não', 'nem', 'nunca'}
    return stop_words_pt - negations

def remove_accents(input_str):
    """Normaliza o texto, removendo os acentos (ex: "depressão" -> "depressao")."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def preprocess_text_improved(text, stop_words):
    """
    Função aprimorada para limpar e pré-processar um texto.
    Recebe a lista de stopwords como argumento.
    """
    text = remove_accents(text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    words = [word for word in text.split() if word not in stop_words]
    return ' '.join(words)