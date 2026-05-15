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

    # Salvar em Parquet (mantém tipos e é mais eficiente)
    #df.to_parquet("bug_dataset_clean.parquet", index=False)

    print("Arquivos salvos com sucesso!")

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
    reports: List[BugReport] = []
    for index, row in cleaned_csv.iterrows():
        try:
            reports.append(BugReport(**row))
        except ValueError:

            continue

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
