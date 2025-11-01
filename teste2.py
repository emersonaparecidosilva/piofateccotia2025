# test_api.py
import google.generativeai as genai
import os

# --- IMPORTANTE ---
# Cole sua API Key AQUI, diretamente no código, apenas para este teste.
# NÃO SALVE ESTE ARQUIVO COM A CHAVE EM LUGAR PÚBLICO.
# ------------------
SUA_API_KEY_AQUI = "AIzaSyCkYh6G9Dq_fa70WqEzlhgiuMYeEdGsNgk"

print({SUA_API_KEY_AQUI})

if "AIzaSyCkYh6G9Dq_fa70WqEzlhgiuMYeEdGsNgk" in SUA_API_KEY_AQUI:
    print("ERRO: Por favor, edite o arquivo test_api.py e insira sua API Key na variável 'SUA_API_KEY_AQUI'.")
    exit()

print("Iniciando teste de conexão...")

try:
    # Configura a API Key
    genai.configure(api_key=SUA_API_KEY_AQUI)

    print(f"API Key configurada (termina com: ...{SUA_API_KEY_AQUI[-4:]})")

    # Configura o modelo (sem o prompt de sistema, só para testar a conexão)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    print("Modelo carregado. Tentando gerar conteúdo...")

    # Faz uma chamada de teste simples
    response = model.generate_content("Isso é um teste. Responda 'OK'.")

    print("\n--- SUCESSO! ---")
    print("Conexão estabelecida e resposta recebida:")
    print(response.text)

except Exception as e:
    print("\n--- ERRO NA CONEXÃO ---")
    print("A chamada para a API do Gemini falhou.")
    print("Esta é a mensagem de erro exata que precisamos:\n")
    print(f"{type(e).__name__}: {e}")

print("\nTeste concluído.")