import streamlit as st
import pandas as pd
from utils import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Análise Supervisionada", page_icon="🧠", layout="wide")
st.title("🧠 Análise de Algoritmos de Aprendizado Supervisionado")
st.markdown("---")

st.header("Metodologia")
st.write(
    """
    Após a avaliação manual de **1.112 tweets**, os dados foram utilizados para treinar e avaliar 
    diferentes algoritmos de classificação. O processo seguiu os seguintes passos:
    1.  **Pré-processamento do Texto:** Limpeza dos dados, remoção de acentos, caracteres especiais, links e *stopwords* (palavras comuns sem valor semântico).
    2.  **Vetorização com TF-IDF:** Transformação do texto limpo em uma representação numérica que os modelos de machine learning pudessem entender.
    3.  **Divisão dos Dados:** Separação dos dados em 80% para treino e 20% para teste, de forma estratificada para manter a proporção de classes.
    4.  **Treinamento e Avaliação:** Treinamento de cinco algoritmos distintos e avaliação de sua performance no conjunto de teste, com foco especial nas métricas para a classe "Positivo" devido ao desbalanceamento dos dados.
    """
)

st.header("Resultados Comparativos")

# Criando o DataFrame com os resultados
data = {
    'Modelo': ['Naive Bayes', 'Regressão Logística', 'SVM (LinearSVC)', 'Random Forest', 'LightGBM'],
    'Acurácia Geral': ['74%', '75%', '74%', '78%', '70%'],
    'Recall (Positivo)': [0.29, 0.56, 0.54, 0.44, 0.57],
    'Precisão (Positivo)': [0.74, 0.61, 0.60, 0.76, 0.53],
    'F1-Score (Positivo)': [0.41, 0.58, 0.57, 0.56, 0.55]
}
df_results = pd.DataFrame(data)

st.write("A tabela abaixo resume a performance dos modelos testados. O **F1-Score (Positivo)** foi a métrica principal para a escolha do melhor modelo, pois representa o melhor equilíbrio entre `recall` e `precisão` para a nossa classe minoritária.")

# Função para destacar o maior valor na coluna
def highlight_max(s):
    is_max = s == s.max()
    return ['background-color: #28a745; color: white' if v else '' for v in is_max]

st.dataframe(
    df_results.style.apply(highlight_max, subset=['F1-Score (Positivo)']),
    use_container_width=True,
    hide_index=True
)

st.subheader("🏆 Modelo Vencedor: Regressão Logística")
st.success(
    """
    O modelo de **Regressão Logística** foi selecionado como o melhor para esta tarefa. 
    Ele apresentou o F1-Score mais alto para a classe minoritária (Positivo), indicando o melhor 
    equilíbrio entre a capacidade de encontrar tweets positivos e a precisão de suas classificações.
    """
)