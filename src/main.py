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
    data_frame = pandas.read_csv(bug_dataset_path, sep=",")
    print("Inicial:", data_frame.shape)

    # 2. Remover linhas com valores nulos
    data_frame = data_frame.dropna()
    print("Após remover nulos:", data_frame.shape)

    # colunas removidas por redundancia nos dados
    columns_to_remove = ['bug_id',
                         'bug_category',
                         'description',
                         'root_cause',
                         'suggested_fix',
                         'explanation']
    data_frame = data_frame.drop(columns=columns_to_remove)

    # Normaliza o texto
    for col in data_frame.select_dtypes(include='object').columns:
        if col != 'created_at':
            data_frame[col] = data_frame[col].str.lower().str.strip()
        if col == 'title':
            data_frame[col] = data_frame[col].str.replace("detected in system", "")

    data_frame['created_at'] = pandas.to_datetime(
        data_frame['created_at'], format='%Y-%m-%d', errors='coerce')

    data_frame['created_at'] = data_frame['created_at'].dt.date

    data_frame['error_code'] = pandas.to_numeric(data_frame['error_code'], errors='coerce')

    data_frame['severity'] = data_frame['severity'].astype('category')
    data_frame['environment'] = data_frame['environment'].astype('category')

    data_frame.to_csv("../etc/bug_dataset_clean.csv", index=False)

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
    streamlit.subheader("Distribuição de Severidade")

    severity_count = data["severity"].value_counts().sort_values(ascending=False)

    streamlit.bar_chart(severity_count)
    streamlit.caption("Quantidade de bugs por nível de severidade")


def mostrar_taxa_criticos(data):
    streamlit.subheader("Taxa de Bugs Críticos")

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
        streamlit.error("Muitos bugs críticos!")
    else:
        streamlit.success("️Nível crítico sob controle")


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
        "Visualizações",
        [
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos"
        ],
        default=[
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos"
        ]
    )

    col_a, col_b = streamlit.columns(2)

    if "Distribuição de Severidade" in opcao:
        with col_a:
            mostrar_distribuicao_severidade(data)

    if "Taxa de Bugs Críticos" in opcao:
        with col_b:
            mostrar_taxa_criticos(data)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    cleaned_csv_path = os.path.join(BASE_DIR, "..", "etc", "bug_dataset_clean.csv")
    try:
        sanitize_csv(cleaned_csv_path)
        cleaned_csv = read_csv(cleaned_csv_path)

    except FileNotFoundError:
        print("<[ERRO CRITICO]> Dataset ainda não existe após sanitização")
        return

    reports = BugReport.parse_csv(cleaned_csv)

    dashboard(reports)


if __name__ == '__main__':
    main()
