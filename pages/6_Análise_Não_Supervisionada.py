# pages/6_🤖_Análise_Não_Supervisionada.py
import streamlit as st
from utils import check_password
import pandas as pd
import io
from wordcloud import WordCloud
import matplotlib.pyplot as plt

if not check_password():
    st.stop()

st.set_page_config(page_title="Análise Não Supervisionada", page_icon="🤖", layout="wide")
st.title("🤖 Análise de Algoritmos Não Supervisionados")
st.markdown("---")

# --- Função para Gerar Nuvem de Palavras ---
def create_wordcloud(text_data, title):
    """Gera e exibe uma nuvem de palavras no Streamlit."""
    try:
        # Gera a nuvem de palavras. Substitui vírgulas por espaços.
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            collocations=False # Impede que a biblioteca agrupe palavras
        ).generate(text_data.replace(",", " "))

        # Exibe a imagem gerada usando matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off') # Esconde os eixos
        st.pyplot(fig) # Exibe no Streamlit
    except Exception as e:
        st.error(f"Erro ao gerar nuvem de palavras para '{title}': {e}")
        st.warning("Verifique se as bibliotecas 'wordcloud' e 'matplotlib' estão instaladas.")


# --- Resumo Final ---
st.header("Resumo Final da Análise")
st.write("A análise não supervisionada aplicou técnicas de clusterização (K-Means) e modelagem de tópicos (LDA) para identificar grupos e temas emergentes no conjunto de dados.")

col1, col2 = st.columns(2)
col1.metric("Tópicos LDA Detectados", 5)
col2.metric("Clusters K-Means Detectados", 5)

st.info("""
- **Tópicos (LDA):** Revelam as ideias centrais ou temas recorrentes nos tweets.
- **Clusters (K-Means):** Agrupam tweets com vocabulário semelhante.
- **Tabela de Correspondência:** Mostra quais temas (tópicos) predominam em cada grupo (cluster).
""")

# --- Abas para LDA e K-Means ---
tab1, tab2 = st.tabs(["Análise de Tópicos (LDA)", "Análise de Clusters (K-Means)"])

# Dados dos Tópicos e Clusters
lda_topics = {
    "Tópico 1: (Foco em Suicídio/Ato)": "dia, pra, suicidio, deus, carta, suicida, vai, suicídio, vou, matar",
    "Tópico 2: (Foco em Desejo de Fuga/Morte)": "nao, matem, tudo, queria, mim, melhor, morto, dormir, sempre, pra",
    "Tópico 3: (Foco em Solidão/Desejo de Morrer)": "agora, gente, mds, viver, pra, nao, vou, sozinho, morrer, quero",
    "Tópico 4: (Foco em Depressão/Fim da Vida)": "vou, quer, vai, pra, tudo, acabar, acordar, nunca, vida, depressão",
    "Tópico 5: (Foco em Cansaço/Valor da Vida)": "anos, ainda, pra, pena, depressao, vale, vida, morto, cansado, viver"
}

kmeans_clusters = {
    "Cluster 0:": "quero, morrer, deus, viver, mds, nao, vou, gente, agora, dia",
    "Cluster 1:": "vida, viver, cansado, acabar, vale, pra, quero, pena, vai, nao",
    "Cluster 2:": "pra, morto, morrer, suicídio, vai, depressão, quero, melhor, tudo, vou",
    "Cluster 3:": "matar, vou, vai, frente, pra, ter, quero, nao, morrer, agora",
    "Cluster 4:": "pra, dormir, sempre, queria, quero, acordar, nunca, dia, sono, vou"
}

with tab1:
    st.subheader("Nuvem de Palavras por Tópico (LDA)")
    st.write("Cada tópico representa um conjunto de palavras frequentemente associadas.")
    
    for title, words in lda_topics.items():
        with st.expander(f"**{title}**"):
            st.code(words)
            # Adiciona a nuvem de palavras dentro do expander
            create_wordcloud(words, title)

with tab2:
    st.subheader("Nuvem de Palavras por Cluster (K-Means)")
    st.write("Cada cluster agrupa tweets que usam palavras similares.")
    
    for title, words in kmeans_clusters.items():
        with st.expander(f"**{title}**"):
            st.code(words)
            # Adiciona a nuvem de palavras dentro do expander
            create_wordcloud(words, title)
    

# --- Tabela de Correspondência ---
st.markdown("---")
st.header("Tabela de Correspondência (Tópicos LDA vs. Clusters K-Means)")
st.write("""
Esta tabela mostra a % de tweets de cada cluster (linhas) que pertencem a cada tópico (colunas).
Por exemplo, 97.7% dos tweets no **Cluster 0** (foco em "quero morrer") pertencem ao **Tópico 2** (desejo de fuga/morte).
""")

# Dados da tabela extraídos do PDF
table_data_csv = """
Topico_dominante,0,1,2,3,4
0,1.0,0.7,97.7,0.7,0.0
1,1.5,12.6,3.9,28.3,53.7
2,21.7,25.8,10.9,24.5,17.2
3,86.0,2.2,6.7,3.2,1.9
4,0.5,92.3,1.5,5.2,0.5
"""

# Limpa os dados e carrega em um DataFrame
try:
    # Remove linhas em branco
    csv_cleaned = "\n".join(line for line in table_data_csv.splitlines() if line.strip())
    df = pd.read_csv(io.StringIO(csv_cleaned))
    
    # Define 'Topico_dominante' como o índice (linhas)
    df = df.set_index("Topico_dominante")
    df.index.name = "Tópico Dominante"
    df.columns.name = "Cluster"
    
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Erro ao processar a tabela de dados: {e}")

