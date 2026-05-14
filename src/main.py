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

if __name__ == '__main__':
    main()