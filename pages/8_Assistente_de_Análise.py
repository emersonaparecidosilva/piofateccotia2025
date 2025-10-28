import streamlit as st
import pandas as pd
import pickle
from utils import (
    check_password, init_connection, fetch_evaluation_stats,
    preprocess_text_improved, get_stopwords_pt  # Funções de ML importadas do utils
)

# 1. Verifica a senha antes de carregar qualquer coisa
if not check_password():
    st.stop()

# 2. Configurações da página
st.set_page_config(page_title="Assistente de Análise", page_icon="💬", layout="wide")
st.title("💬 Assistente de Análise do Projeto")
st.write("Pergunte sobre o projeto ou use `classificar: [seu texto]` para testar o modelo de IA.")

# --- BASE DE CONHECIMENTO DO NOSSO "BOT" ---

# 3. Carrega a conexão com o banco de dados
conn = init_connection()

# 4. Carrega os dados estáticos (resultados da análise)
data = {
    'Modelo': ['Naive Bayes', 'Regressão Logística', 'SVM (LinearSVC)', 'Random Forest', 'LightGBM'],
    'F1-Score (Positivo)': [0.41, 0.58, 0.57, 0.56, 0.55]
}
df_results = pd.DataFrame(data).set_index('Modelo')

# 5. Carrega o MODELO de ML e o VETORIZADOR (em cache)
@st.cache_resource
def load_model_and_vectorizer():
    """Carrega o modelo salvo e o vetorizador do arquivo .pkl"""
    try:
        with open('supervisionado.pkl', 'rb') as file:
            data = pickle.load(file)
        # Pega as stopwords que o modelo usou no treino
        stop_words = get_stopwords_pt()
        return data['model'], data['vectorizer'], stop_words
    except FileNotFoundError:
        st.error("Arquivo 'supervisionado.pkl' não encontrado! Certifique-se de que ele está na pasta principal do projeto.")
        return None, None, None
    except Exception as e:
        st.error(f"Erro ao carregar o modelo: {e}")
        return None, None, None

model, vectorizer, stop_words = load_model_and_vectorizer()

# --- Função principal que processa a pergunta do usuário ---
def get_bot_response(user_question):
    q = user_question.lower()

    # --- Resposta de Classificação (IA em tempo real) ---
    if q.startswith("classificar:"):
        if model is None or vectorizer is None:
            return "Desculpe, o modelo de classificação não pôde ser carregado. Verifique os logs."
        
        # Extrai o texto a ser classificado
        tweet_text = user_question[len("classificar:"):].strip()
        
        if not tweet_text:
            return "Por favor, escreva um texto após 'classificar:'."
        
        try:
            # 1. Pré-processa o texto
            text_limpo = preprocess_text_improved(tweet_text, stop_words)
            
            # 2. Vetoriza o texto
            text_vetorizado = vectorizer.transform([text_limpo])
            
            # 3. Faz a previsão
            previsao = model.predict(text_vetorizado)
            probabilidade = model.predict_proba(text_vetorizado)
            
            sentimento = "Positivo" if previsao[0] else "Negativo"
            confianca = max(probabilidade[0]) * 100
            
            return f"O modelo previu que o sentimento é **{sentimento}** (com {confianca:.1f}% de confiança)."
        except Exception as e:
            return f"Ocorreu um erro durante a classificação: {e}"

    # --- Respostas Baseadas em Palavras-Chave (Perguntas Frequentes) ---
    
    if "quantos tweets" in q and "coletados" in q:
        stats = fetch_evaluation_stats(conn)
        return f"Foram coletados um total de **{stats.get('total_geral', 'N/A')}** tweets."
    
    if "quantos tweets" in q and "avaliados" in q:
        stats = fetch_evaluation_stats(conn)
        return f"Foram avaliados manualmente **{stats.get('total_avaliados', 'N/A')}** tweets."

    if "qual" in q and "melhor modelo" in q:
        return f"O modelo vencedor foi a **Regressão Logística**. Ele apresentou o melhor equilíbrio (F1-Score de 0.58) para identificar a classe positiva, que era a minoria nos dados."

    if "svm" in q:
        score = df_results.loc['SVM (LinearSVC)']['F1-Score (Positivo)']
        return f"O modelo SVM (LinearSVC) teve um F1-Score de **{score}**, um resultado muito bom e muito similar ao da Regressão Logística."
    
    if "random forest" in q:
        score = df_results.loc['Random Forest']['F1-Score (Positivo)']
        return f"O modelo Random Forest teve um F1-Score de **{score}**. Ele foi o vencedor no teste de 'laboratório' com dados 50/50, mas a Regressão Logística foi melhor no cenário real."

    if "objetivo" in q or "sobre o que" in q:
         return "O objetivo do projeto é classificar o sentimento (positivo ou negativo) em tweets sobre saúde mental, usando aprendizado de máquina supervisionado."
    
    if "ferramentas" in q or "tecnologias" in q:
        return "Usamos **Python** como linguagem principal, **Streamlit** para esta interface, **PostgreSQL** como banco de dados, **Pandas** para análise e **Scikit-learn** para todo o machine learning."

    # Resposta padrão
    return "Desculpe, não entendi. Tente perguntar 'quantos tweets...?', 'qual o melhor modelo?' ou use o comando `classificar: [seu texto aqui]`."

# --- Interface de Chat do Streamlit ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso ajudar a analisar o projeto hoje?"}]

# Exibe as mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura a nova pergunta do usuário
if prompt := st.chat_input("Pergunte ou use 'classificar:'"):
    # Adiciona a pergunta do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera e exibe a resposta do "bot"
    response = get_bot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)