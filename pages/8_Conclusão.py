# pages/7_📜_Conclusão.py
import streamlit as st
from utils import check_password

# Autenticação
if not check_password():
    st.stop()

# Configuração da página
st.set_page_config(page_title="Conclusão", page_icon="📜", layout="wide")

# Estilo visual personalizado
st.markdown(
    """
    <style>
    .block-container {
        max-width: 900px;
        margin: auto;
        padding-top: 2rem;
    }
    h1, h2, h3, h4, h5, h6, p {
        text-align: justify;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Conteúdo
st.title("📜 Conclusão do Projeto")
st.markdown("---")

st.write("""
O desenvolvimento deste projeto possibilitou compreender, na prática, como técnicas de ciência de dados e aprendizado de máquina podem ser aplicadas em contextos socialmente relevantes, como a detecção de ideação suicida em postagens de redes sociais. Através da coleta de dados via API do Twitter/X, foi possível estruturar uma base de mais de três mil tweets, dos quais uma amostra representativa foi cuidadosamente analisada e rotulada para o treinamento de modelos de aprendizado supervisionado.
""")

st.write("""
Durante o processo, o grupo enfrentou desafios relacionados à limpeza e balanceamento dos dados, bem como à escolha de algoritmos adequados para lidar com o desbalanceamento entre classes positivas e negativas. Os experimentos comparativos demonstraram que, embora o modelo Random Forest tenha obtido melhor desempenho em uma base artificialmente balanceada, a Regressão Logística apresentou resultados mais consistentes e interpretáveis quando aplicada ao conjunto real, representando, portanto, a melhor solução final. Essa decisão reforça a importância de considerar o contexto e a natureza dos dados, e não apenas métricas isoladas, ao avaliar modelos de IA.
""")

st.write("""
Além da implementação dos algoritmos, o projeto também integrou uma aplicação web desenvolvida em Streamlit, hospedada em ambiente gratuito, que permitiu a visualização e interação com os resultados de forma acessível. A combinação de ferramentas como Python, PostgreSQL, Google Gemini e bibliotecas de processamento de linguagem natural consolidou um pipeline robusto para análise textual e experimentação com dados reais.
""")

st.write("""
Por fim, o trabalho reforça o potencial da Ciência de Dados como instrumento de apoio à saúde mental e à prevenção do suicídio, mostrando que a tecnologia pode ser utilizada de forma ética e responsável para identificar sinais de alerta e promover ações preventivas. Embora o modelo desenvolvido ainda possa ser aprimorado com bases mais amplas e diversificadas, os resultados alcançados representam um passo significativo na aplicação de inteligência artificial voltada ao bem-estar social.
""")
