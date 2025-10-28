# ============================================
# 🔹 ANÁLISE DE TWEETS COM LDA, K-MEANS E T-SNE
# ============================================

# 🧩 Instale antes (se necessário):
# pip install psycopg2-binary sqlalchemy pandas scikit-learn nltk plotly gensim

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import plotly.express as px

# -------------------------------------------------
# 🔧 1. CONEXÃO AO BANCO DE DADOS (Render PostgreSQL)
# -------------------------------------------------

# 👉 Substitua pelas suas credenciais do Render
DB_HOST = "dpg-d3mi2mggjchc73d5qqmg-a.oregon-postgres.render.com"
DB_NAME = "apix_4ini"
DB_USER = "apix_user"
DB_PASS = "CSYr9e62tbIXH9Rso67YLowaz2cJ7VUp"
DB_PORT = "5432"  # geralmente é essa porta no Render

# Cria conexão com SQLAlchemy
conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

# -------------------------------------------------
# 📥 2. LEITURA DOS DADOS
# -------------------------------------------------

query = "SELECT id_tweet, texto_tweet FROM tweets_texto;"
tweets_df = pd.read_sql(query, engine)
print(f"Total de tweets carregados: {len(tweets_df)}")

# -------------------------------------------------
# 🧹 3. PRÉ-PROCESSAMENTO DE TEXTO
# -------------------------------------------------

nltk.download('stopwords')
stopwords_pt = set(stopwords.words('portuguese'))

def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"http\S+", "", texto)  # remove links
    texto = re.sub(r"@\w+", "", texto)     # remove menções
    texto = re.sub(r"[^a-zA-Zá-úÁ-Ú\s]", "", texto)  # remove símbolos
    palavras = [p for p in texto.split() if p not in stopwords_pt and len(p) > 2]
    return " ".join(palavras)

tweets_df['texto_limpo'] = tweets_df['texto_tweet'].astype(str).apply(limpar_texto)

# -------------------------------------------------
# 🧠 4. LDA - DETECÇÃO DE TÓPICOS
# -------------------------------------------------

vectorizer = CountVectorizer(max_df=0.9, min_df=10)
X_lda = vectorizer.fit_transform(tweets_df['texto_limpo'])

lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(X_lda)

# Mostra palavras principais de cada tópico
palavras = vectorizer.get_feature_names_out()
for i, topic in enumerate(lda.components_):
    top_palavras = [palavras[j] for j in topic.argsort()[-10:]]
    print(f"Tópico {i+1}: {', '.join(top_palavras)}")

# -------------------------------------------------
# 🔸 5. K-MEANS - AGRUPAMENTO DE TWEETS
# -------------------------------------------------

tfidf = TfidfVectorizer(max_features=1000)
X_tfidf = tfidf.fit_transform(tweets_df['texto_limpo'])

num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
tweets_df['cluster'] = kmeans.fit_predict(X_tfidf)

# -------------------------------------------------
# 🌈 6. t-SNE - VISUALIZAÇÃO 2D
# -------------------------------------------------

tsne = TSNE(n_components=2, random_state=42, perplexity=40, max_iter=1000)
tsne_results = tsne.fit_transform(X_tfidf.toarray())

tweets_df['tsne_x'] = tsne_results[:, 0]
tweets_df['tsne_y'] = tsne_results[:, 1]

# -------------------------------------------------
# 📊 7. VISUALIZAÇÃO INTERATIVA
# -------------------------------------------------

fig = px.scatter(
    tweets_df,
    x='tsne_x',
    y='tsne_y',
    color=tweets_df['cluster'].astype(str),
    hover_data=['texto_tweet'],
    title="Visualização dos Clusters de Tweets (K-Means + t-SNE)"
)
fig.show()

# -------------------------------------------------
# 🧾 8. COMPARAÇÃO DOS RESULTADOS
# -------------------------------------------------
print("\nResumo dos clusters encontrados:")
print(tweets_df['cluster'].value_counts())

# Salva resultado final (se quiser)
tweets_df.to_csv("resultados_tweets_clusters.csv", index=False)
print("\nResultados salvos em 'resultados_tweets_clusters.csv'")

# ============================================
# 🔍 9. COMPARAÇÃO ENTRE LDA x K-MEANS
# ============================================
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud

# 🧠 9.1. Palavras principais de cada tópico (LDA)
print("\n==============================")
print("🔹 Principais palavras de cada tópico (LDA)")
print("==============================")

num_top_palavras = 10
palavras = vectorizer.get_feature_names_out()

lda_topicos = {}
for i, topic in enumerate(lda.components_):
    top_palavras = [palavras[j] for j in topic.argsort()[-num_top_palavras:]]
    lda_topicos[f"Tópico {i+1}"] = top_palavras
    print(f"Tópico {i+1}: {', '.join(top_palavras)}")

# 🧾 Gera nuvens de palavras dos tópicos (LDA)
fig, axes = plt.subplots(1, len(lda_topicos), figsize=(18, 8))
for i, (nome_topico, palavras_lista) in enumerate(lda_topicos.items()):
    texto = " ".join(palavras_lista)
    wc = WordCloud(width=800, height=600, background_color="white").generate(texto)
    axes[i].imshow(wc, interpolation="bilinear")
    axes[i].set_title(nome_topico, fontsize=14)
    axes[i].axis("off")
plt.suptitle("🧠 LDA — Principais Palavras por Tópico", fontsize=18)
plt.show()

# 🔸 9.2. Palavras mais frequentes por cluster (K-Means)
print("\n==============================")
print("🔹 Palavras mais frequentes de cada cluster (K-Means)")
print("==============================")

# Cria uma lista de palavras por cluster
for cluster_id in sorted(tweets_df['cluster'].unique()):
    textos_cluster = tweets_df[tweets_df['cluster'] == cluster_id]['texto_limpo']
    todas_palavras = " ".join(textos_cluster).split()
    contador = Counter(todas_palavras)
    palavras_comuns = [p for p, _ in contador.most_common(10)]
    print(f"Cluster {cluster_id}: {', '.join(palavras_comuns)}")

# 🧾 Gera nuvens de palavras dos clusters (K-Means)
num_clusters = len(tweets_df['cluster'].unique())
fig, axes = plt.subplots(1, num_clusters, figsize=(20, 8))
for i, cluster_id in enumerate(sorted(tweets_df['cluster'].unique())):
    textos_cluster = tweets_df[tweets_df['cluster'] == cluster_id]['texto_limpo']
    texto = " ".join(textos_cluster)
    wc = WordCloud(width=800, height=600, background_color="white").generate(texto)
    axes[i].imshow(wc, interpolation="bilinear")
    axes[i].set_title(f"Cluster {cluster_id}", fontsize=14)
    axes[i].axis("off")
plt.suptitle("🎨 K-Means — Palavras Mais Frequentes por Cluster", fontsize=18)
plt.show()

# ============================================
# 📈 10. RESUMO FINAL DA ANÁLISE
# ============================================

print("\n==============================")
print("📊 RESUMO FINAL")
print("==============================")
print(f"Tópicos LDA detectados: {len(lda_topicos)}")
print(f"Clusters K-Means detectados: {num_clusters}")
print("\nOs gráficos mostraram visualmente:")
print("- Os tópicos (LDA) revelam as ideias centrais ou temas recorrentes nos tweets.")
print("- Os clusters (K-Means) agrupam tweets com vocabulário semelhante.")
print("- Comparando ambos, você pode ver quais temas (tópicos) predominam em cada grupo.")
print("\n💡 Dica: use os prints acima para nomear manualmente cada cluster e tópico.")

# ============================================
# 🔗 11. CORRESPONDÊNCIA ENTRE CLUSTERS (K-Means) E TÓPICOS (LDA)
# ============================================

import numpy as np

print("\n==============================")
print("🔗 CORRESPONDÊNCIA CLUSTERS ↔ TÓPICOS (K-Means x LDA)")
print("==============================")

# Gera as distribuições de tópicos para cada tweet
lda_distribuicao = lda.transform(X_lda)

# Adiciona o tópico dominante de cada tweet
tweets_df["topico_dominante"] = np.argmax(lda_distribuicao, axis=1)

# Calcula a tabela de correspondência (cluster x tópico)
tabela_corresp = pd.crosstab(tweets_df["cluster"], tweets_df["topico_dominante"], normalize="index") * 100
tabela_corresp = tabela_corresp.round(1)  # porcentagens com 1 casa decimal

print("\n📋 Tabela de correspondência (% de tweets de cada cluster que pertencem a cada tópico):\n")
print(tabela_corresp)

# Visualização em heatmap
import seaborn as sns
plt.figure(figsize=(8, 6))
sns.heatmap(tabela_corresp, annot=True, cmap="YlGnBu", fmt=".1f")
plt.title("🔗 Correspondência entre Clusters (K-Means) e Tópicos (LDA)")
plt.xlabel("Tópico LDA")
plt.ylabel("Cluster K-Means")
plt.show()

# Interpretação automática
for cluster_id in tabela_corresp.index:
    topico_pred = tabela_corresp.loc[cluster_id].idxmax()
    valor = tabela_corresp.loc[cluster_id, topico_pred]
    print(f"🧩 Cluster {cluster_id} → Tópico dominante: {topico_pred} ({valor:.1f}% dos tweets)")

print("\n💡 Interprete assim:")
print("- Cada linha representa um cluster K-Means (grupos de tweets semelhantes).")
print("- Cada coluna representa um tópico LDA (tema latente identificado).")
print("- O número mais alto em cada linha indica qual tópico domina aquele cluster.")
