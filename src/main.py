import os
from typing import List

import pandas
import streamlit

from models.bug_report import BugReport

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def sanitize_csv(csv_path):
    print("Sanitizando dataset")
    bug_dataset_path = os.path.join(BASE_DIR, "..", "etc", "bug_dataset_50k.csv")
    print("Caminho do csv bruto: ", bug_dataset_path)

    # colocar a pipeline aqui dentro
    # salvar o arquivo no path "/etc/bug_dataset_clean.csv"

    print("Caminho do csv sanitizado: ", csv_path)
    print("Limpeza concluída")


def read_csv(cleaned_csv_path):
    return pandas.read_csv(cleaned_csv_path, sep=",")


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
    print(cleaned_csv)
# transforma o CSV em lista de BugReport
    reports = BugReport.parse_csv(cleaned_csv)

    # valida se deu certo
    if len(reports) == 0:
        print("Nenhum BugReport válido encontrado")
        return

    # lista de objetos bug_report "reports"

    for report in reports:
        # acessamos os campos do report dessa forma
        if (report.error_code == 404
                and "memory leak" in report.title
                and "laravel" in report.tech_stack):
            print("Encontrado report com status 404: ", report.__dict__)
    streamlit.set_page_config(layout="wide")
    streamlit.metric(label="Total de reports", value=len(reports))

# =========================
# DASHBOARD STREAMLIT
# =========================

def mostrar_total_reports(reports):
    streamlit.metric(label="Total de reports", value=len(reports))


def mostrar_distribuicao_severidade(data):
    streamlit.subheader("Distribuição de Severidade")

    severity_count = data["severity"].value_counts()
    streamlit.bar_chart(severity_count)


def mostrar_taxa_criticos(data):
    streamlit.subheader("Taxa de Bugs Críticos")

    total = len(data)
    criticos = len(data[data["severity"] == "critical"])

    taxa = (criticos / total) * 100 if total > 0 else 0

    col1, col2 = streamlit.columns(2)

    with col1:
        streamlit.metric("Críticos", criticos)

    with col2:
        streamlit.metric("Taxa", f"{taxa:.2f}%")

    streamlit.progress(min(taxa / 100, 1))

    streamlit.write(f"{criticos} de {total} bugs são críticos")


def dashboard(reports):
    data = pandas.DataFrame([r.__dict__ for r in reports])

    streamlit.set_page_config(layout="wide")
    streamlit.title("Dashboard de Bugs")

    opcao = streamlit.sidebar.multiselect(
        "O que você quer ver?",
        [
            "Total de Reports",
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos"
        ],
        default=[
            "Total de Reports",
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos"
        ]
    )

    if "Total de Reports" in opcao:
        mostrar_total_reports(reports)

    if "Distribuição de Severidade" in opcao:
        mostrar_distribuicao_severidade(data)

    if "Taxa de Bugs Críticos" in opcao:
        mostrar_taxa_criticos(data)


def main():
    cleaned_csv_path = os.path.join(BASE_DIR, "..", "etc", "bug_dataset_clean.csv")

    try:
        cleaned_csv = read_csv(cleaned_csv_path)

    except FileNotFoundError:
        print("Falha ao encontrar dataset limpo!")
        sanitize_csv(cleaned_csv_path)

        if not os.path.exists(cleaned_csv_path):
            print("<[ERRO CRITICO]> Dataset ainda não existe após sanitização")
            return

        cleaned_csv = read_csv(cleaned_csv_path)

    reports = BugReport.parse_csv(cleaned_csv)

    if len(reports) == 0:
        print("Nenhum BugReport válido encontrado")
        return

    dashboard(reports)
    
if __name__ == '__main__':
    main()