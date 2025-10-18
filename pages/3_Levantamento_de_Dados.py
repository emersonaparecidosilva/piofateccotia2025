import streamlit as st
import os
from utils import check_password, init_connection, fetch_evaluation_stats

if not check_password():
    st.stop()

st.set_page_config(page_title="Levantamento de Dados", page_icon="📊", layout="wide")
st.title("📊 Levantamento e Coleta de Dados")
st.markdown("---")

st.subheader("Processo de Coleta")
st.write(
    """
    Buscamos inicialmente uma base pronta e atual com os temos relacionados ao tema do nosso trabalho, porém não encontramos. 
    Com isso, decidimos coletar nossos dados diretamente na API do X.
    Nosso primeiro desafio foi a limitação de uso da versão gratuita, 1 requisição por mês com retorno de apenas 100 registros.
    Fizemos uma forma tarefa e criamos várias contas de desenvolvedor utilizando emails temporários.
    Com isso, finalmente conseguimos uma quantidade de tokens suficientes e iniciamos a coleta dos dados. Cada chamada na API utilizavamos um termo especifico. 
    """
)

st.subheader("Termos Pesquisados")
todos_os_termos = [
    "suicidio", "suicida", "suicidio", "suicida", "suicidio", "me matar",
    "estar morto", "cansado de viver", "suicidio", "estar morto",
    "nunca acordar", "acabar com a minha vida", "me matar",
    "dormir pra sempre", "quero morrer", "meu bilhete suicida",
    "não vale a pena viver", "cansado de viver", "suicidio",
    "minha carta de suicidio", "nunca acordar", "quero morrer",
    "estar morto", "melhor sem mim", "cansado de viver", "morrer sozinho",
    "pronto para pular", "suicidio", "melhor morto"
]

termos_unicos = list(set(todos_os_termos))

markdown_lista = ""
for termo in termos_unicos:
    markdown_lista += f"- {termo}\n"  # Adiciona "- item"

st.markdown(markdown_lista)

arquivo_codigo = "buscaX.py"

codigo_para_mostrar = ""
try:
    with open(arquivo_codigo, "r", encoding="utf-8") as f:
        codigo_para_mostrar = f.read()
except FileNotFoundError:
    codigo_para_mostrar = f"Erro: Arquivo '{arquivo_codigo}' não encontrado na raiz do projeto."
except Exception as e:
    codigo_para_mostrar = f"Ocorreu um erro ao ler o arquivo: {e}"

st.subheader("Código para Extração dos Dados")
with st.expander("**Clique aqui**", expanded=False):
    st.code(codigo_para_mostrar, language="python")


st.subheader("Estruturação dos Dados")
st.write(
    """
    Iniciamos com base local, em mysql. Porém, chegamos na conclusão que isso inviabilizaria a avaliação dos tweets por todo o
    grupo, pois, ficaria apenas na máquina de um integrante. Optamos então por se cadastrar na plataforma "Render.com" e 
    criamos uma instância gratuita do Postgres, versão 17. Logo, todo o time conseguiu conectar na base e apoiar.
    """
)

st.subheader("Avaliação dos Tweets")
st.write(
    """
    Aproveitamos o conhecimento em streamlit desenvolvido em sala de aula e criamos uma ferramenta para que nossa equipe pudesse avaliar
    de forma sincrona, de onde estiver. Visita a seção "Avaliação dos Tweets" ao lado. 
    """
)

texto_metodologia = """
**Intuito** --> Identificar tweets que indiquem sinais de um quadro depressivo em quem está publicando.
 
**O que fazer:**
 
* Avaliar como **POSITIVO** aqueles tweets que indiquem os sinais de depressão e/ou comportamento suicida em quem escreve.
* Avaliar como **NEGATIVO** aqueles que indicam quaisquer outros comportamentos ou que indicam o comportamento buscado, mas em terceiros (**EX:** Alguém sendo agressivo e desejando que outra pessoa tenha depressão é um comportamento negativo, mas não se enquadra naquilo que buscamos).
 
**O que não fazer:**
 
* Avaliar como positivo tweets que não indicam depressão de quem posta (**EX:** `@DC_da_Depressão` esse episódio de ontem foi lamentável).
* Avaliar como positivo aqueles tweets que citam depressão, mas como forma de "brincadeira"(**Ex:** Meus amigo curtindo uma festa na praia e eu aqui trabalhando, que depressão).
* Avaliar como positivo aqueles tweets que citam depressão e/ou comportamento suicida, mas em terceiros e não em quem está escrevendo(**EX:** Meu amigo sofreu uma perda na família e tenho medo que ele possar atentar contra a própria vida).
"""

with st.expander("**Metodologia de avaliação dos tweets**"):
    st.markdown(texto_metodologia, unsafe_allow_html=True)

st.subheader("Resumo Quantitativo")
conn = init_connection()
if conn:
    stats = fetch_evaluation_stats(conn)
    total_coletado = stats.get('total_geral', 0)
    total_avaliado = stats.get('total_avaliados', 0)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Tokens Utilizados", "29")
    col2.metric("Total de Tweets Coletados", "3.552")
    col3.metric("Tweets Avaliados", f"{total_avaliado:,}".replace(",", "."))
    col4.metric("Positivo", "347")
    col5.metric("Negativo", "765")