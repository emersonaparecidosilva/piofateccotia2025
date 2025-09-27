import streamlit as st
import psycopg2
from psycopg2.extras import DictCursor # Facilita o acesso às colunas pelo nome

# --- Configuração da Página ---
st.set_page_config(
    page_title="Ferramenta de Avaliação de Tweets",
    page_icon="📊",
    layout="centered"
)

# --- Título e Descrição ---
st.title("📊 Ferramenta de Avaliação de Tweets")
st.write(
    "Clique em 'Positivo' ou 'Negativo' para classificar o tweet exibido. "
    "Sua avaliação será salva no banco de dados."
)

# --- Funções de Banco de Dados ---

@st.cache_resource
def init_connection():
    """
    Inicializa a conexão com o banco de dados PostgreSQL.
    Usa o cache de recursos do Streamlit para manter a conexão viva.
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
    Retorna uma lista de registros (dicionários).
    """
    if _connection is None:
        return []
    with _connection.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id_tweet, texto_tweet FROM tweets_avaliacao WHERE avaliacao IS NULL;")
        return cur.fetchall()

def update_tweet_evaluation(_connection, tweet_id, evaluation: bool):
    """
    Atualiza a avaliação (como um booleano) e a data de atualização de um tweet.
    """
    if _connection is None:
        return
    
    # Query SQL corrigida para usar %s para o booleano e NOW() para o timestamp
    sql_update_query = """
        UPDATE tweets_avaliacao 
        SET 
            avaliacao = %s, 
            data_atualizacao = NOW() 
        WHERE 
            id_tweet = %s;
    """
    with _connection.cursor() as cur:
        cur.execute(sql_update_query, (evaluation, tweet_id))
        _connection.commit()

# --- Lógica Principal da Aplicação ---

# Inicializa a conexão com o banco de dados
conn = init_connection()

# Apenas prossiga se a conexão for bem-sucedida
if conn:
    # Carrega os tweets na primeira execução ou se a lista estiver vazia
    if 'tweets' not in st.session_state:
        st.session_state.tweets = fetch_tweets_to_evaluate(conn)
        st.session_state.current_index = 0

    # Verifica se a lista de tweets está vazia (nenhum tweet para avaliar)
    if not st.session_state.tweets:
        st.info("🎉 Todos os tweets já foram avaliados! Nenhum trabalho pendente.")
    
    # Verifica se já passamos por todos os tweets da lista atual
    elif st.session_state.current_index >= len(st.session_state.tweets):
        st.success("✨ Parabéns! Você avaliou todos os tweets desta rodada.")
        st.balloons()
    
    # Se ainda há tweets para avaliar, exibe a interface principal
    else:
        # Pega o tweet atual da lista
        current_tweet = st.session_state.tweets[st.session_state.current_index]
        
        # Extrai as informações do tweet (usando DictCursor, podemos acessar como um dicionário)
        tweet_id = current_tweet['id_tweet']
        tweet_text = current_tweet['texto_tweet']

        # Exibe o progresso
        total_tweets = len(st.session_state.tweets)
        progress_text = f"Avaliando Tweet {st.session_state.current_index + 1} de {total_tweets}"
        st.progress((st.session_state.current_index + 1) / total_tweets, text=progress_text)
        
        # Exibe o texto do tweet em uma caixa de citação
        st.markdown(f"> {tweet_text}", unsafe_allow_html=True)
        st.markdown("---") # Linha divisória

        # Cria colunas para os botões
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Positivo 👍", use_container_width=True, type="primary"):
                update_tweet_evaluation(conn, tweet_id, True)  # Passa o booleano True
                st.session_state.current_index += 1
                st.rerun()

        with col2:
            if st.button("Negativo 👎", use_container_width=True):
                update_tweet_evaluation(conn, tweet_id, False) # Passa o booleano False
                st.session_state.current_index += 1
                st.rerun()