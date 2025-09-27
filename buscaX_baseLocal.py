#esse codigo funciona para base local


import requests
import mysql.connector
import time

# --- 1. CONFIGURAÇÕES ---
# Lista dos seus tokens da API do X (Twitter).
# Substitua os tokens de exemplo pelos seus.
bearer_tokens = [
    # "AAAAAAAAAAAAAAAAAAAAAC6u4AEAAAAAH1%2BPdBpSqN8Nr6Y8LOuiyBr5xbY%3DCXl64zwO0395Fa1AgJbFEGR01v1kspzuA65ExrW6LCj72M5Zsr", #henrick
    "AAAAAAAAAAAAAAAAAAAAAP4u4QEAAAAAyJ7MBO2MAJmPzl2tpsKZlV1uQ%2Fk%3D42012qD4VCiky0tb7Y7HvAR1tw6sI41yKSqr33LT2wCHpUX0as", #easconta3
    "AAAAAAAAAAAAAAAAAAAAANcu4QEAAAAAfpX6bZokyiFU%2FZyfvS372TemqbI%3DAMiaOEYtqAe7FaSHL3znTMiMKDai7LqVpIPEpusTScHGkze4DJ", #easconta2
    "AAAAAAAAAAAAAAAAAAAAACiu4AEAAAAA5b7WRL8CXTE0LYaamW2JqCVlYOE%3D6LO3plW3z43nAtqccPft71nz56Ex3ns37htsq1qvDauNgF4J8m", #easconta1
]

# Configurações do seu banco de dados MySQL.
# Preencha com suas credenciais.
config_mysql = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'database': 'apix'
}

# --- 2. DADOS DA REQUISIÇÃO ---
query = "depressão lang:pt -is:retweet"
url = f"https://api.x.com/2/tweets/search/recent?query={query}&max_results=100"

# --- 3. EXECUÇÃO PRINCIPAL ---
current_token_index = 0
max_attempts = len(bearer_tokens)

for attempt in range(max_attempts):
    # Se todos os tokens foram usados sem sucesso, pausa e reinicia o ciclo
    if current_token_index >= len(bearer_tokens):
        print("Todos os tokens foram usados. Pausando por 15 minutos para resetar o limite da API...")
        time.sleep(900)  # Pausa por 15 minutos (900 segundos)
        current_token_index = 0  # Reinicia a lista de tokens
        
    bearer_token = bearer_tokens[current_token_index]
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    print(f"\n--- Tentativa {attempt + 1}/{max_attempts} usando o token {current_token_index + 1} ---")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Requisição bem-sucedida! Processando e salvando dados...")
        dados = response.json()
        
        try:
            conn = mysql.connector.connect(**config_mysql)
            cursor = conn.cursor()

            # Cria a tabela se ela não existir
            create_table_query = """
            CREATE TABLE IF NOT EXISTS tweets (
                id_tweet VARCHAR(255) PRIMARY KEY,
                texto_tweet TEXT NOT NULL
            )
            """
            cursor.execute(create_table_query)

            insert_query = "INSERT INTO tweets (id_tweet, texto_tweet) VALUES (%s, %s)"

            if "data" in dados:
                for tweet in dados["data"]:
                    tweet_id = tweet["id"]
                    tweet_text = tweet["text"]
                    
                    try:
                        cursor.execute(insert_query, (tweet_id, tweet_text))
                        print(f"Tweet '{tweet_id}' salvo.")
                    except mysql.connector.Error as err:
                        if err.errno == 1062:
                            print(f"Tweet '{tweet_id}' já existe, ignorando a inserção.")
                        else:
                            print(f"Erro ao inserir tweet '{tweet_id}': {err}")

            conn.commit()
            print("\nProcesso de salvamento concluído.")

        except mysql.connector.Error as err:
            print(f"Erro de conexão com o MySQL: {err}")
        
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                print("Conexão com o MySQL encerrada.")
        
        break  # Sai do loop porque a requisição foi bem-sucedida
    
    # Tratamento para erros de autenticação (401) e limite de requisições (429)
    elif response.status_code in (401, 429):
        print(f"Erro {response.status_code}. Trocando para o próximo token...")
        current_token_index += 1
        # O 'continue' implícito do loop tentará a próxima iteração com o novo token
    
    else:
        print(f"Erro inesperado: {response.status_code}, {response.text}")
        break  # Sai do loop em caso de outros erros não tratados