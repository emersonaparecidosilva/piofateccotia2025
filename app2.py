import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Avaliação de Tweets",
    page_icon="📊",
    layout="wide" # Mudei para 'wide' para dar mais espaço aos indicadores
)

# --- Título ---
st.title("📊 Dashboard e Ferramenta de Avaliação de Tweets")

# --- Funções de Banco de Dados ---

@st.cache_resource
def init_connection():
    """
    Inicializa a conexão com o banco de dados PostgreSQL.
    """
    try:
        conn = psycopg2.connect(st.secrets["database"]["url"])
        return conn
    except (psycopg2.OperationalError, KeyError) as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        st.info("Verifique se as credenciais no arquivo .streamlit/secrets.toml estão corretas.")
        return None

def fetch_tweets_to_evaluate(_connection):
    """
    Busca tweets cuja coluna 'avaliacao' é NULA.
    """
    if _connection is None: return []
    with _connection.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id_tweet, texto_tweet FROM tweets_avaliacao WHERE avaliacao IS NULL;")
        return cur.fetchall()

def update_tweet_evaluation(_connection, tweet_id, evaluation: bool):
    """
    Atualiza a avaliação e a data de atualização de um tweet.
    """
    if _connection is None: return
    sql_update_query = """
        UPDATE tweets_avaliacao 
        SET avaliacao = %s, data_atualizacao = NOW() 
        WHERE id_tweet = %s;
    """
    with _connection.cursor() as cur:
        cur.execute(sql_update_query, (evaluation, tweet_id))
        _connection.commit()

# NOVA FUNÇÃO PARA BUSCAR AS ESTATÍSTICAS
def fetch_evaluation_stats(_connection):
    """
    Busca estatísticas agregadas da tabela de avaliação.
    """
    if _connection is None:
        return {'total_geral': 0, 'total_avaliados': 0, 'total_true': 0, 'total_false': 0}
    
    # Query única e eficiente para pegar todos os contadores
    sql_stats_query = """
        SELECT
            COUNT(*) AS total_geral,
            COUNT(avaliacao) AS total_avaliados,
            SUM(CASE WHEN avaliacao = TRUE THEN 1 ELSE 0 END) AS total_true,
            SUM(CASE WHEN avaliacao = FALSE THEN 1 ELSE 0 END) AS total_false
        FROM
            tweets_avaliacao;
    """
    with _connection.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(sql_stats_query)
        return cur.fetchone()

# --- Lógica Principal da Aplicação ---

conn = init_connection()

if conn:
    # --- Seção de Indicadores (Dashboard) ---
    stats = fetch_evaluation_stats(conn)
    total_geral = stats['total_geral']
    total_avaliados = stats['total_avaliados']
    total_true = stats['total_true']
    total_false = stats['total_false']

    # Cálculos de porcentagem com segurança (evitando divisão por zero)
    percent_avaliados = (total_avaliados / total_geral * 100) if total_geral > 0 else 0
    percent_true = (total_true / total_avaliados * 100) if total_avaliados > 0 else 0
    percent_false = (total_false / total_avaliados * 100) if total_avaliados > 0 else 0

    st.markdown("### Resumo das Avaliações")
    
    # Criando 5 colunas para os 5 indicadores
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="1. Total de Tweets", value=f"{total_geral:,}".replace(",", "."))
    with col2:
        st.metric(label="2. Total Avaliados", value=f"{total_avaliados:,}".replace(",", "."))
    with col3:
        st.metric(label="3. % Avaliados", value=f"{percent_avaliados:.1f}%")
    with col4:
        st.metric(label="4. % Positivos", value=f"{percent_true:.1f}%", help="Percentual de tweets avaliados como 'Positivo'")
    with col5:
        st.metric(label="5. % Negativos", value=f"{percent_false:.1f}%", help="Percentual de tweets avaliados como 'Negativo'")
    
    st.markdown("---") # Linha divisória

    # --- Seção de Ferramenta de Avaliação ---
    st.header("Ferramenta de Avaliação")
    
    if 'tweets' not in st.session_state:
        st.session_state.tweets = fetch_tweets_to_evaluate(conn)
        st.session_state.current_index = 0

    if not st.session_state.tweets:
        st.info("🎉 Todos os tweets já foram avaliados! Nenhum trabalho pendente.")
    
    elif st.session_state.current_index >= len(st.session_state.tweets):
        st.success("✨ Parabéns! Você avaliou todos os tweets desta rodada.")
        if st.button("Recarregar para buscar novos tweets"):
            del st.session_state.tweets # Força o recarregamento na próxima execução
            st.rerun()
        st.balloons()
    
    else:
        current_tweet = st.session_state.tweets[st.session_state.current_index]
        tweet_id = current_tweet['id_tweet']
        tweet_text = current_tweet['texto_tweet']

        total_a_avaliar = len(st.session_state.tweets)
        progress_text = f"Avaliando Tweet {st.session_state.current_index + 1} de {total_a_avaliar}"
        st.progress((st.session_state.current_index + 1) / total_a_avaliar, text=progress_text)
        
        st.markdown(f"> {tweet_text}", unsafe_allow_html=True)
        st.markdown("---")

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Positivo 👍", use_container_width=True, type="primary"):
                update_tweet_evaluation(conn, tweet_id, True)
                st.session_state.current_index += 1
                st.rerun()

        with btn_col2:
            if st.button("Negativo 👎", use_container_width=True):
                update_tweet_evaluation(conn, tweet_id, False)
                st.session_state.current_index += 1
                st.rerun()