import requests
import psycopg2
from psycopg2 import sql, errors
import time

# --- 1. CONFIGURAÇÕES ---
# Lista dos seus tokens da API do X (Twitter).
bearer_tokens = [
    "AAAAAAAAAAAAAAAAAAAAAC6u4AEAAAAAH1%2BPdBpSqN8Nr6Y8LOuiyBr5xbY%3DCXl64zwO0395Fa1AgJbFEGR01v1kspzuA65ExrW6LCj72M5Zsr",
"AAAAAAAAAAAAAAAAAAAAAPou4QEAAAAAcVshLfM0eOBWafpaDbCrslDI2Os%3DVrvr4NR7HJS9xQ4KOEh7bhF0x6w0sW52uVN6IFgXSaPJ2JdWjJ",
"AAAAAAAAAAAAAAAAAAAAAHs74QEAAAAA4PmY5QLSqqsEb6KPwiI602Osh1w%3DDWNrH6Y9bOo7eR1jYEXS34cidoyWz2dYfc7fzGZEV52ZyqKlvn",
"AAAAAAAAAAAAAAAAAAAAAMZb4QEAAAAAZvqd2ExvgJ37EZkNkMR0n24kjqM%3DEaHag5wlu1BjJx91ukghHBlsJE111jaZwB0XO1VEXifdxvV5pn",
"AAAAAAAAAAAAAAAAAAAAAMhb4QEAAAAA5asYp1HJ%2F4uwG3z4k5szllO3K1s%3Ds3S3OT9iuHxrwW3YFRGDG4TppK4FsvEQ3ReP9ePr5wL48VfkHq",
"AAAAAAAAAAAAAAAAAAAAALpb4QEAAAAA3XrPAEkO8wB8ziRzGPQKuKBhw2M%3DowOj5mZCk51HUzt0EDnPyH6OdFQRTgRe2T4bLri1hazdcJwb8j",
"AAAAAAAAAAAAAAAAAAAAAL474QEAAAAAnNDFD4eGedhSJmHTqNQxfZQklwM%3DsVcypw2eFAlwGcTMvm4QHBJUo7f5Citt87SzUIpeJQLNG4lstO",
"AAAAAAAAAAAAAAAAAAAAALaP4QEAAAAAWnHoOpn83Gsq22pTLHXUGxf7INA%3Dp9hZXHXyqVPI1W8rTFq3cbgW0NBVAZ5isnfBB5AqxKL1bg4O16",
"AAAAAAAAAAAAAAAAAAAAAC2a4QEAAAAApwfT229DR9wtG1bPps%2FCn8PKTjs%3DvJhXmQvAx1CQz5wUm42npCzL9FThGdYeYvCH6QNIYuQki7zBD1",
"AAAAAAAAAAAAAAAAAAAAAOuP4QEAAAAAobIiXo8w6t%2FZFiUwFTwQsFIoWQc%3D2pzmunEuqwRkF8xUEpocAfSUUlfkgHa7a1w11lS21HlWW1jRBT",
"AAAAAAAAAAAAAAAAAAAAAO%2BP4QEAAAAARU8MgS9uezzox4EmawXfMWXjOUE%3Dtwi4Tj6YPYRpjh2RKTrz0dmIvmS9NCz8F4fEv6TsRQrUA5a6mK",
"AAAAAAAAAAAAAAAAAAAAAPWP4QEAAAAA%2F23g59IMeNqeNCDhPXagale1oUY%3DpV2ICdY2EgcAimqMdFUsjGTkhmOpQ6whJyrK21Ll70c41P342C",
"AAAAAAAAAAAAAAAAAAAAAPqP4QEAAAAAQTVhWRd%2F98ulLFT566lCV%2BG6oQc%3D0cgMqS5pQ9myEC8vUXuLy58iivIzrTsaE3xRUl3DxTovV3MfJJ",
"AAAAAAAAAAAAAAAAAAAAAAaQ4QEAAAAAtbZMjnUYErfla1OZRIeRaWPNeI8%3D4jKJ0RHibHBX6uzJ8PEnRyc1sM0pEsDUF0MuP7k7kTkwweXTk9",
"AAAAAAAAAAAAAAAAAAAAABGQ4QEAAAAAa5E9wiHXFjDtcZA7zUHsaezTabc%3DMjc2F8cb3TKezjmAJfY3GWpRVMyjvmEwHi2PRHSNjnVbO2JdWf",
"AAAAAAAAAAAAAAAAAAAAAByQ4QEAAAAAAepvK%2FVU25fzwbT8HvIN5d4LNbs%3DPqURoXIYkJyp5b5J5yj7NbUOot6lh8XqSOttFPoIwgis1sjvck",
"AAAAAAAAAAAAAAAAAAAAAMGP4QEAAAAANJX9bE8ZvS81pXhE%2BT23cT%2Beje4%3D4DIgUISV2vb8ELfTF5yCTvikWxdA4jUdzCFubf4A9oVl60J0Gv",
"AAAAAAAAAAAAAAAAAAAAAMyP4QEAAAAAouMjs1C773XrtDCprD4wSKNEwBE%3DchnC6B3KK32F5tbz5r3oZDlOYjKzPzm05WrmYozUvrOza2VXJF",
"AAAAAAAAAAAAAAAAAAAAANKP4QEAAAAANNhPuVHsOYNEnuBi4nExbXQJnmo%3DaJeSVWy7At6JroVoqk6MzSX28BFdRIXeA5xHPVZl9WmkBJEu5p",
"AAAAAAAAAAAAAAAAAAAAAEma4QEAAAAAKJYQWvsgfGmTlLQFl1CPPZUc1IA%3DUYWBTKw7dhRhkIwnILbt21rMhmmCKfy67WYyC2F6PWKgJurT67",
"AAAAAAAAAAAAAAAAAAAAAIGb4QEAAAAAxMP1UhOg%2Fwa9qEudCyYd1t58z1U%3DctLK8hLG4NrWhZlcBlTolSXVvTACbtCdmcJWZJY71kPWuuFp5W",
"AAAAAAAAAAAAAAAAAAAAANCb4QEAAAAA41kL5jkKMrd6oxWLEbBjhjx9g%2Fg%3D6dYVuMKXMV2GdMWToyvmRmy8yQk17q8o01mNmRLO8aT77xecCk",
"AAAAAAAAAAAAAAAAAAAAABkH4gEAAAAAsGOiosO%2FsYCcRv0XnjQ4LudO6ag%3DCfQlN4QVNpVQ1l9kMa6sDD1t4JPmXcMFMKwbMtSxIycKVh9aZb",
"AAAAAAAAAAAAAAAAAAAAADAH4gEAAAAAPULQ3dMlGOBYBBFynLfPJSPdWdg%3DyPXoS4EueNpM7siVbGmltMHv1lbRr1wYlAUSpI7FcPHv1iPtlD",
"AAAAAAAAAAAAAAAAAAAAAH8H4gEAAAAAWAWQzwAznBi7U2aoLSDEnaGGCuE%3DRjWudAMBuwhAEAtWXlLWuszHB6FPgZTB5SZAJjWDB3J2m45RoQ",
"AAAAAAAAAAAAAAAAAAAAAHQH4gEAAAAAnLfacHVDc%2BktzyqZM83jwg9ZzFc%3DIXsurGVgLryQKZpAqJc9X6KkPhutZkjYDVYki4ufVD2LDQxN0C",
"AAAAAAAAAAAAAAAAAAAAAMiP4QEAAAAAo28Eld3zS%2BvE8fbGC%2BxVe2A6wcw%3D8S8vHqzRzd8KZCJtTAI6yAzGLPGrveKHwX2jY9GwS0gMdbX8ia",
"AAAAAAAAAAAAAAAAAAAAALxb4QEAAAAAbEg6tk6MI4mKLBzM6Nu1BA1bYhs%3DNRsiZ7fQlllIx0b2ZtVxS8SmsWwBOOzsdTyUq649s0khPpQRea",
"AAAAAAAAAAAAAAAAAAAAABqQ4QEAAAAAyASt8aJ95W8ebtHgdd%2FyaL3SOUg%3Df2NqKh94ve79jz9f7tlO5jqcoZLy5U30SKt9VhVmdkiBuvuEFA", #easconta1
]

# Configurações do seu banco de dados PostgreSQL no Render.
config_pg = {
    'user': 'apix_user',
    'password': 'CSYr9e62tbIXH9Rso67YLowaz2cJ7VUp',
    'host': 'dpg-d3mi2mggjchc73d5qqmg-a.oregon-postgres.render.com',
    'port': 5432,
    'database': 'apix_4ini'
}

# --- 2. DADOS DA REQUISIÇÃO ---
query = "suicidio lang:pt -is:retweet"
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