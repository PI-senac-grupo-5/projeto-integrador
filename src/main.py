import os

import pandas
import streamlit

from models.bug_report import BugReport


def sanitize_csv(csv_path):
    print("Sanitizando dataset")
    bug_dataset_path = os.path.join(BASE_DIR, "..", "etc", "bug_dataset_50k.csv")
    print("Caminho do csv bruto: ", bug_dataset_path)

    # colocar a pipeline aqui dentro

    # 1. Carregar dataset com separador correto ","
    df = pandas.read_csv(bug_dataset_path, sep=",")
    print("Inicial:", df.shape)

    # 2. Remover linhas com valores nulos
    df = df.dropna()
    print("Após remover nulos:", df.shape)

    # 3. Remover coluna identificadora (bug_id) ANTES de checar duplicatas
    print("Bug IDs únicos antes da remoção:", df['bug_id'].nunique(), df.shape[0])
    df = df.drop(columns=['bug_id',
                          'bug_category',
                          'description',
                          'root_cause',
                          'suggested_fix',
                          'explanation'])
    print("Colunas após remover bug_id:", df.columns)

    # 4. Normalizar texto
    # include=object - str não reconhecido
    for col in df.select_dtypes(include='object').columns:
        if col != 'created_at':
            df[col] = df[col].str.lower().str.strip()

    padroes_remover = {
        "title": [
            {"string": "detected in system", "posicao": "fim"}
        ]
    }

    def limpar_coluna(serie, regras):
        for regra in regras:
            texto = regra["string"].strip()
            if regra["posicao"] == "inicio":
                # remove no início, ignorando espaços extras
                serie = serie.str.replace(rf"^{texto}\s*", "", regex=True)
            elif regra["posicao"] == "fim":
                # remove no fim, ignorando ponto final e espaços
                serie = serie.str.replace(rf"\s*{texto}\.*$", "", regex=True)
        return serie.str.strip()

    # aplicar em todas as colunas
    for col, regras in padroes_remover.items():
        if col in df.columns:
            df[col] = limpar_coluna(df[col], regras)
    # Remover duplicados (após remover bug_id e normalizar)
    # Nesta etapa seria possível remover linhas duplicadas após normalização.
    # No entanto, mantive todas as linhas porque cada registro representa um bug contado,
    # mesmo que o texto seja igual.

    # 5. Converter coluna de data com formato explícito
    # format='%Y-%m-%d'
    df['created_at'] = pandas.to_datetime(
        df['created_at'], format='%Y-%m-%d', errors='coerce')

    # 5.1 Remover a hora, mantendo apenas a data
    df['created_at'] = df['created_at'].dt.date

    # 6. Converter coluna numérica
    df['error_code'] = pandas.to_numeric(df['error_code'], errors='coerce')

    # 7. Converter colunas categóricas (após normalização)
    df['severity'] = df['severity'].astype('category')
    df['environment'] = df['environment'].astype('category')

    # 9. Verificação final
    print(df.head())
    print(df.info())
    print("Valores únicos em severity:", df['severity'].unique())
    print("Valores únicos em environment:", df['environment'].unique())
    print("Nulos restantes:\n", df.isnull().sum())
    print("Distribuição error_code:\n", df['error_code'].describe())

    # 10. Salvar
    # Salvar em CSV (mais universal, abre em Excel)
    df.to_csv("../etc/bug_dataset_clean.csv", index=False)

    # salvar o arquivo no path "/etc/bug_dataset_clean.csv"
    print("Arquivos salvos com sucesso!")
    print("Caminho do csv sanitizado: ", csv_path)
    print("Limpeza concluída")


def read_csv(cleaned_csv_path):
    return pandas.read_csv(cleaned_csv_path, sep=",")


# =========================
# DASHBOARD STREAMLIT
# =========================

def mostrar_distribuicao_severidade(data):
    streamlit.subheader("📊 Distribuição de Severidade")

    severity_count = data["severity"].value_counts().sort_values(ascending=False)

    streamlit.bar_chart(severity_count)
    streamlit.caption("Quantidade de bugs por nível de severidade")


def mostrar_taxa_criticos(data):
    streamlit.subheader("🔥 Taxa de Bugs Críticos")

    total = len(data)
    criticos = len(data[data["severity"] == "critical"])
    taxa = (criticos / total) * 100 if total > 0 else 0

    streamlit.progress(taxa / 100)

    col1, col2 = streamlit.columns(2)

    with col1:
        streamlit.metric("Críticos", criticos)

    with col2:
        streamlit.metric("Taxa crítica", f"{taxa:.2f}%")

    if taxa > 20:
        streamlit.error("⚠️ Muitos bugs críticos!")
    else:
        streamlit.success("✔️ Nível crítico sob controle")


def dashboard(reports):
    data = pandas.DataFrame([r.__dict__ for r in reports])

    streamlit.set_page_config(layout="wide")
    streamlit.title(" Dashboard de Bugs")

    # ===== KPIs =====
    total = len(reports)
    criticos = len(data[data["severity"] == "critical"])
    taxa = (criticos / total) * 100 if total > 0 else 0

    col1, col2, col3 = streamlit.columns(3)

    col1.metric("Total de Reports", total)
    col2.metric("Críticos", criticos)
    col3.metric("Taxa Crítica", f"{taxa:.2f}%")

    streamlit.divider()

    # ===== Sidebar =====
    opcao = streamlit.sidebar.multiselect(
        "📊 Visualizações",
        [
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos"
        ],
        default=[
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos"
        ]
    )

    colA, colB = streamlit.columns(2)

    if "Distribuição de Severidade" in opcao:
        with colA:
            mostrar_distribuicao_severidade(data)

    if "Taxa de Bugs Críticos" in opcao:
        with colB:
            mostrar_taxa_criticos(data)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    cleaned_csv_path = os.path.join(BASE_DIR, "..", "etc", "bug_dataset_clean.csv")
    try:
        cleaned_csv = read_csv(cleaned_csv_path)

    except FileNotFoundError:
        print("Falha ao encontrar dataset limpo!")
        # caso falhe em encontrar o arquivo "bug_dataset_clean.csv" no diretório "/etc", chama a pipeline de limpeza e cria o arquivo

        sanitize_csv(cleaned_csv_path)

        if not os.path.exists(cleaned_csv_path):
            # se não criar o dataset, falha e encerra a aplicação
            print("<[ERRO CRITICO]> Dataset ainda não existe após sanitização")
            return

        cleaned_csv = read_csv(cleaned_csv_path)

    # csv que vamos trabalhar "cleaned_csv"
    reports = BugReport.parse_csv(cleaned_csv)

    # lista de objetos bug_report "reports"

    dashboard(reports)


if __name__ == '__main__':
    main()
