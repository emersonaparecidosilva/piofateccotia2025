import streamlit as st
import google.generativeai as genai
import sys

# --- CONFIGURAÇÃO DA PÁGINA E API ---

# Configuração básica da página do Streamlit
st.set_page_config(
    page_title="Integração com IA",
    page_icon="🩺",
    layout="wide"
)

# Tenta carregar a chave de API dos segredos do Streamlit
try:
    # Este bloco de código foi melhorado para ler sua chave 
    # independentemente de como ela está no secrets.toml
    api_key = None
    if st.secrets.get("GEMINI_API_KEY"):
        if isinstance(st.secrets.get("GEMINI_API_KEY"), dict):
            api_key = st.secrets["GEMINI_API_KEY"].get("GEMINI_API_KEY")
        elif isinstance(st.secrets.get("GEMINI_API_KEY"), str):
            api_key = st.secrets["GEMINI_API_KEY"]
    
    if not api_key and st.secrets.get("credentials"):
        if isinstance(st.secrets.get("credentials"), dict):
            api_key = st.secrets["credentials"].get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Chave de API não encontrada.")

    genai.configure(api_key=api_key)
except (KeyError, ValueError, FileNotFoundError):
    st.error("ERRO: A 'GEMINI_API_KEY' não foi encontrada.")
    st.error("Por favor, verifique seu painel 'Settings -> Secrets' no Streamlit Cloud.")
    st.stop()


# --- DEFINIÇÃO DO AGENTE (SYSTEM PROMPT) ---

# Este é o "cérebro" do seu agente.
SYSTEM_INSTRUCTION = """
# CONTEXTO E PERSONA DA IA
Você é um assistente de IA especializado em análise de linguagem e sentimento, treinado para atuar como ferramenta de suporte para um psiquiatra sênior.
Seu supervisor (o usuário) é um psiquiatra com mais de 30 anos de experiência em prevenção de suicídio.

# SUA TAREFA
Sua função é realizar uma TRIAGEM INICIAL de textos. Você deve analisar o texto e identificar indicadores de risco de suicídio ou depressão severa.
Você NUNCA deve fornecer um diagnóstico definitivo. Sua função é classificar o NÍVEL DE RISCO para que seu supervisor possa priorizar a análise humana.

# DIRETRIZES DE ANÁLISE
1.  **Indicadores de Risco:** Analise o texto em busca de ideação suicida explícita, desesperança, desamparo, sentimento de ser um fardo, menções a planos, despedidas.

2.  **Formato da Resposta:** Responda ESTRITAMENTE no seguinte formato (use Markdown):

    **Nível de Risco:** [CLASSIFICAÇÃO]

    **Justificativa:** [Análise concisa de 2-3 linhas explicando *por que* você atribuiu esse nível, citando os indicadores encontrados no texto.]

3.  **Níveis de Classificação:**
    * **NÍVEL CRÍTICO:** Presença de ideação explícita com plano ou intenção imediata.
    * **NÍVEL ALTO:** Presença de ideação suicida clara, forte desesperança ou sentimento de ser um fardo.
    * **NÍVEL MÉDIO:** Presença de temas de depressão severa, desamparo ou desesperança, mas sem ideação suicida explícita.
    * **NÍVEL BAIXO:** Tristeza, frustração, mas sem indicadores claros dos níveis acima.
    * **NÍVEL INSUFICIENTE:** Texto muito curto ou ambíguo.

"""

# --- CONFIGURAÇÃO DO MODELO GEMINI ---

generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}


safety_settings = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE" 
}
# ----------------------------------------------------------------------

# Inicialização do modelo
try:
    model = genai.GenerativeModel(
        # ---- CORREÇÃO PRINCIPAL AQUI ----
        model_name="models/gemini-2.5-flash-lite",
        generation_config=generation_config,
        system_instruction=SYSTEM_INSTRUCTION,
        safety_settings=safety_settings
    )
except Exception as e:
    st.error(f"Erro ao inicializar o modelo Gemini: {e}")
    st.stop()


# --- FUNÇÃO DE ANÁLISE ---

def analisar_texto_com_gemini(texto_usuario):
    """
    Envia o texto para a API do Gemini com o prompt de sistema e retorna a análise.
    """
    if not texto_usuario:
        return "Erro: Nenhum texto fornecido."

    try:
        # Esta é a chamada de API
        response = model.generate_content(texto_usuario)
        return response.text

    except Exception as e:
        # Captura erros, incluindo bloqueios de segurança
        st.error(f"ERRO CRÍTICO NA CHAMADA DA API: {e}")
        if "prompt was blocked" in str(e):
            return "Erro: O texto de entrada foi bloqueado pela política de segurança da API, apesar das configurações. O conteúdo pode ser extremo."
        if "response was blocked" in str(e):
             return "Erro: A resposta da IA foi bloqueada. Isso pode acontecer se a IA tentar citar diretamente conteúdo muito gráfico."
        return f"Erro inesperado ao processar a solicitação: {str(e)}"

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---

st.title("🩺 Integração com IA Gemini")

# Área de texto para o input
texto_para_analisar = st.text_area(
    " ",
    height=150,
    placeholder="Insira o texto aqui..."
)

# Botão para disparar a análise
if st.button("Analisar Texto/Tweet"):
    if texto_para_analisar:
        # Mostra um "spinner" enquanto a IA processa
        with st.spinner("Analisando... A IA está avaliando o texto."):
            resultado_analise = analisar_texto_com_gemini(texto_para_analisar)
        
        # Exibe o resultado
        st.subheader("Resultado")
        st.markdown(resultado_analise) # O resultado já vem formatado em Markdown
    else:
        st.warning("Por favor, insira um texto para analisar.")
