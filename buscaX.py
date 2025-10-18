import requests
import psycopg2
from psycopg2 import sql, errors
import time

bearer_tokens = [
    "Tokens Separados por Vírgula",

]

# Credenciais do Banco de dados
config_pg = {
    'user': 'user',
    'password': 'password',
    'host': 'host',
    'port': 5432,
    'database': 'apix'
}

# --- 2. DADOS DA REQUISIÇÃO ---
query = "depre lang:pt -is:retweet"
url = f"https://api.x.com/2/tweets/search/recent?query={query}&max_results=100"

# --- 3. EXECUÇÃO PRINCIPAL ---
current_token_index = 0
max_attempts = len(bearer_tokens)

for attempt in range(max_attempts):
    if current_token_index >= len(bearer_tokens):
        print("Todos os tokens foram usados. Pausando por 15 minutos para resetar o limite da API...")
        time.sleep(900)
        current_token_index = 0
        
    bearer_token = bearer_tokens[current_token_index]
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    print(f"\n--- Tentativa {attempt + 1}/{max_attempts} usando o token {current_token_index + 1} ---")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Requisição bem-sucedida! Processando e salvando dados...")
        dados = response.json()
        
        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(**config_pg)
            cursor = conn.cursor()

            # Cria a tabela para salvar apenas o texto
            create_table_query = """
            CREATE TABLE IF NOT EXISTS tweets_texto (
                id_tweet VARCHAR(255) PRIMARY KEY,
                texto_tweet TEXT NOT NULL
            )
            """
            insert_query = "INSERT INTO tweets_texto (id_tweet, texto_tweet) VALUES (%s, %s) ON CONFLICT (id_tweet) DO NOTHING;"

            cursor.execute(create_table_query)
            conn.commit() # Commita a criação da tabela

            if "data" in dados:
                for tweet in dados["data"]:
                    tweet_id = tweet["id"]
                    tweet_text = tweet["text"]
                    
                    try:
                        cursor.execute(insert_query, (tweet_id, tweet_text))
                        print(f"Tweet '{tweet_id}' salvo.")
                    except (psycopg2.Error) as err:
                        print(f"Erro ao inserir tweet '{tweet_id}': {err}")

            conn.commit()
            print("\nProcesso de salvamento concluído.")

        except psycopg2.Error as err:
            print(f"Erro de conexão com o PostgreSQL: {err}")
        
        finally:
            if 'conn' in locals() and not conn.closed:
                cursor.close()
                conn.close()
                print("Conexão com o PostgreSQL encerrada.")
        
        break
    
    elif response.status_code in (401, 429):
        print(f"Erro {response.status_code}. Trocando para o próximo token...")
        current_token_index += 1
    
    else:
        print(f"Erro inesperado: {response.status_code}, {response.text}")
        break