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

# Otimização: Cache evita reprocessar o CSV a cada clique na tela
@streamlit.cache_data

def read_csv(cleaned_csv_path):
    return pandas.read_csv(cleaned_csv_path, sep=",")


def main():
    # Configuração da página deve ser o primeiro comando Streamlit executado
    streamlit.set_page_config(layout="wide")

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

    # >>> AQUI é um bom lugar para inserir o gráfico <<<
    desc_counts = cleaned_csv["description"].value_counts().head(10)

    streamlit.subheader("Top 10 Descriptions")

    #streamlit.bar_chart(desc_counts)

    import altair as alt

    df_plot = desc_counts.reset_index()
    df_plot.columns = ["description", "count"]

# Gráfico de barras

    chart = alt.Chart(df_plot).mark_bar().encode(
        x=alt.X("description", sort="-y", axis=alt.Axis(labelAngle=-45)), # 🔴 gira o texto do eixo X e ordena pelo valor do eixo Y (crescente)
        y=alt.Y("count", scale=alt.Scale(domain=[0, df_plot["count"].max()], zero=False)),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="viridis"))
    )

    streamlit.altair_chart(chart, use_container_width=True)

    # csv que vamos trabalhar "cleaned_csv"
    print(cleaned_csv)
    reports: List[BugReport] = []
    for index, row in cleaned_csv.iterrows():
        try:
            reports.append(BugReport(**row))
        except ValueError:

            continue

    # lista de objetos bug_report "reports"
    
    # Cria uma caixa/barra em volta da métrica
    with streamlit.container(border=True):
        streamlit.metric(label="Total de reports", value=len(reports))

if __name__ == '__main__':
    main()
