import streamlit as st
import pandas as pd
from utils import check_password

if not check_password():
    st.stop()

st.set_page_config(page_title="Análise Supervisionada", page_icon="🧠", layout="wide")
st.title("🧠 Análise de Algoritmos de Aprendizado Supervisionado")
st.markdown("---")

# --- SEÇÃO 1: O EXPERIMENTO PRINCIPAL (MUNDO REAL) ---

st.header("Metodologia (Abordagem Principal - Dados Reais)")
st.write(
    """
    A principal análise foi realizada utilizando o conjunto de dados completo de **1.112 tweets avaliados**. 
    Este conjunto de dados reflete a realidade da coleta, sendo **desbalanceado** (aproximadamente 69% Negativos e 31% Positivos).
    
    O processo seguiu os seguintes passos:
    1.  **Pré-processamento do Texto:** Limpeza de dados (acentos, links, stopwords, etc.).
    2.  **Vetorização com TF-IDF:** Transformação do texto em vetores numéricos.
    3.  **Divisão Estratificada (80/20):** Separação dos dados em treino e teste, mantendo a proporção 70/30 de classes em ambos.
    4.  **Treinamento com Correção de Viés:** Os modelos foram treinados usando o parâmetro `class_weight='balanced'`, que "pune" mais o modelo por errar na classe minoritária (Positivo), forçando-o a dar mais atenção a ela.
    """
)

st.header("Resultados (Abordagem Principal - Dados Reais)")

# Criando o DataFrame com os resultados
data = {
    'Modelo': ['Naive Bayes', 'Regressão Logística', 'SVM (LinearSVC)', 'Random Forest', 'LightGBM'],
    'Acurácia Geral': ['74%', '75%', '74%', '78%', '70%'],
    'Recall (Positivo)': [0.29, 0.56, 0.54, 0.44, 0.57],
    'Precisão (Positivo)': [0.74, 0.61, 0.60, 0.76, 0.53],
    'F1-Score (Positivo)': [0.41, 0.58, 0.57, 0.56, 0.55]
}
df_results = pd.DataFrame(data)

st.write("A tabela abaixo resume a performance dos modelos testados no cenário do mundo real. O **F1-Score (Positivo)** foi a métrica principal para a escolha do melhor modelo.")

# Função para destacar o maior valor na coluna
def highlight_max(s):
    # Converte a string para float para comparação
    s_numeric = pd.to_numeric(s, errors='coerce')
    is_max = s_numeric == s_numeric.max()
    return ['background-color: #28a745; color: white' if v else '' for v in is_max]

st.dataframe(
    df_results.style.apply(highlight_max, subset=['F1-Score (Positivo)']),
    use_container_width=True,
    hide_index=True
)

st.subheader("🏆 Modelo Vencedor (Mundo Real): Regressão Logística")
st.success(
    """
    O modelo de **Regressão Logística** foi selecionado como o melhor para a tarefa real. 
    Ele apresentou o F1-Score mais alto para a classe minoritária (0.58), indicando o melhor 
    equilíbrio entre a capacidade de encontrar tweets positivos (`Recall`) e a precisão de suas 
    classificações (`Precision`), **utilizando 100% dos dados coletados**.
    """
)

st.markdown("---")

# --- SEÇÃO 2: O EXPERIMENTO DE LABORATÓRIO (BASE BALANCEADA) ---

st.header("🔬 Análise de Laboratório: Teste com Base Balanceada (50/50)")
st.write(
    """
    Para entender melhor o comportamento fundamental de cada algoritmo sem o viés do desbalanceamento, 
    realizamos um segundo experimento. Criamos um novo dataset perfeitamente balanceado 
    contendo **250 tweets positivos e 250 negativos** (total de 500 amostras), 
    processo chamado de **Under-sampling** (subamostragem).

    Treinamos e testamos os mesmos algoritmos nesta base 50/50.
    """
)

st.subheader("Resultados Comparativos (Dataset Balanceado 50/50)")

# Criando o DataFrame com os resultados do novo experimento
data_balanced = {
    'Modelo': ['Random Forest', 'Regressão Logística', 'SVM (LinearSVC)', 'LightGBM', 'Naive Bayes'],
    'Acurácia Geral': ['74.00%', '72.00%', '71.00%', '63.00%', '58.00%'],
    'F1-Score (Média)': [0.74, 0.72, 0.71, 0.63, 0.55],
    'F1-Score (Positivo)': [0.70, 0.69, 0.70, 0.60, 0.67],
    'F1-Score (Negativo)': [0.77, 0.75, 0.72, 0.65, 0.43]
}
df_results_balanced = pd.DataFrame(data_balanced)

st.dataframe(
    df_results_balanced.style.apply(highlight_max, subset=['F1-Score (Média)']),
    use_container_width=True,
    hide_index=True
)

st.subheader("🏆 Conclusão do Experimento (Balanceado vs. Real)")
st.info(
    """
    **O que este experimento nos ensina?**

    1.  **O Vencedor do "Laboratório":** No cenário 50/50, o **Random Forest** foi o campeão. Ele provou ser o algoritmo mais "inteligente", aprendendo melhor os padrões quando os dados estavam perfeitamente balanceados.

    2.  **Por que a Regressão Logística é a Escolha Final:** Embora o Random Forest tenha vencido o teste de laboratório, ele **perdeu 515 tweets negativos** (765 - 250) que foram descartados no processo de under-sampling.

    3.  **Veredito:** A abordagem da **Regressão Logística** no dataset completo (primeiro teste) é a **melhor solução final**, pois ela usou **toda a informação disponível** (1.112 tweets) e, através da técnica `class_weight='balanced'`, conseguiu corrigir o viés do desbalanceamento sem descartar dados valiosos.
    """
)