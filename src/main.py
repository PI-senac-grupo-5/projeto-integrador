import os

import pandas
import streamlit

from models.bug_report import BugReport
from utils.error_code import ErrorCode


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
    for col in data_frame.select_dtypes(include=['object', 'string']).columns:
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

    data_frame.to_csv(csv_path, index=False)

    # salvar o arquivo no path "/etc/bug_dataset_clean.csv"
    print("Arquivos salvos com sucesso!")
    print("Caminho do csv sanitizado: ", csv_path)
    print("Limpeza concluída")


@streamlit.cache_data
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


def media_codigos_erro_dashboard(data):
    import altair as alt

    streamlit.subheader("Códigos de Erro Mais Frequentes")

    error_count = (
        data["error_code"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    error_count.columns = ["error_code", "count"]

    total_errors = error_count["count"].sum()

    top_error = error_count.iloc[0]

    col1, col2 = streamlit.columns(2)

    with col1:
        streamlit.metric(
            "Top 10 Ocorrências",
            total_errors
        )

    with col2:
        streamlit.metric(
            "Código Mais Frequente",
            f"{top_error['error_code']}"
        )

    chart = alt.Chart(error_count).mark_bar(size=30).encode(
        y=alt.Y(
            "error_code:N",
            sort="-x",
            title="Código de Erro"
        ),
        x=alt.X(
            "count:Q",
            title="Ocorrências"
        ),
        color=alt.Color(
            "count:Q",
            scale=alt.Scale(scheme="viridis")
        ),
        tooltip=["error_code", "count"]
    ).properties(
        height=400
    )

    streamlit.altair_chart(chart, width="stretch")

    if top_error["count"] > 5000:
        streamlit.warning(
            f"O código '{top_error['error_code']}': '{ErrorCode.get_description(top_error['error_code'])}' possui alta recorrência."
        )
    else:
        streamlit.success(
            "Os códigos de erro estão distribuídos."
        )


def tech_stack_dashboard(data):
    import altair as alt

    streamlit.subheader("Bugs por Tech Stack")

    tech_count = data["tech_stack"].value_counts().reset_index()
    tech_count.columns = ["tech_stack", "count"]

    chart = alt.Chart(tech_count).mark_bar(size=25).encode(
        y=alt.Y(
            "tech_stack:N",
            sort="-x"
        ),
        x=alt.X(
            "count:Q"
        ),
        color=alt.Color(
            "count:Q",
            scale=alt.Scale(scheme="viridis")
        ),
        tooltip=["tech_stack", "count"]
    ).properties(
        height=600
    )

    streamlit.altair_chart(chart, width="stretch")


def bugs_por_ambiente_dashboard(data):
    import altair as alt

    streamlit.subheader("Bugs por Ambiente")

    ambiente_count = (
        data["environment"]
        .value_counts()
        .reset_index()
    )

    ambiente_count.columns = ["environment", "count"]

    total_bugs = ambiente_count["count"].sum()

    ambiente_critico = ambiente_count.iloc[0]

    col1, col2 = streamlit.columns(2)

    with col1:
        streamlit.metric(
            "Total Bugs",
            total_bugs
        )

    with col2:
        streamlit.metric(
            "Ambiente Crítico",
            ambiente_critico["environment"]
        )

    chart = alt.Chart(ambiente_count).mark_arc(innerRadius=50).encode(
        theta="count:Q",
        color="environment:N",
        tooltip=["environment", "count"]
    ).properties(
        height=450
    )

    streamlit.altair_chart(chart, width="stretch")

    if ambiente_critico["environment"] == "production":
        streamlit.error(
            "Production possui maior volume de bugs."
        )
    else:
        streamlit.success(
            "Production é o ambiente mais estável."
        )


def overtime_dashboard(data):
    streamlit.subheader("Top 10")

    desc_counts = data["title"].value_counts().head(10)

    import altair as alt

    df_plot = desc_counts.reset_index()
    df_plot.columns = ["title", "count"]

    total_titles = int(df_plot["count"].sum())
    top_title = df_plot.iloc[0]["title"] if not df_plot.empty else "N/A"
    top_count = int(df_plot.iloc[0]["count"]) if not df_plot.empty else 0

    col1, col2 = streamlit.columns(2)

    with col1:
        streamlit.metric("Total Top 10", total_titles)

    with col2:
        streamlit.metric("Mais frequente", top_count)

    min_count = df_plot["count"].min()
    max_count = df_plot["count"].max()

    padding = 20

    chart = alt.Chart(df_plot).mark_bar(size=30).encode(
        y=alt.Y(
            "title:N",
            sort="-x"
        ),
        x=alt.X(
            "count:Q",
            scale=alt.Scale(
                domain=[
                    min_count - padding,
                    max_count + padding
                ],
                zero=False,
                clamp=True
            )
        ),
        color=alt.Color(
            "count:Q",
            scale=alt.Scale(scheme="viridis")
        ),
        tooltip=["title", "count"]
    ).properties(
        height=500
    )

    streamlit.altair_chart(chart, width="stretch")

    if top_count > 10:
        streamlit.warning(
            f"A Issues mais frequente é '{top_title}' com {top_count} ocorrências."
        )
    else:
        streamlit.success("As descrições estão bem distribuídas.")


def bugs_timeline_dashboard(data):
    import altair as alt

    streamlit.subheader("Bugs ao Longo do Tempo")

    timeline = (
        data.groupby("created_at")
        .size()
        .reset_index(name="count")
    )

    chart = alt.Chart(timeline).mark_line(point=True).encode(
        x="created_at:T",
        y="count:Q",
        tooltip=["created_at", "count"]
    ).properties(
        height=400
    )

    streamlit.altair_chart(chart, width="stretch")


def heatmap_dashboard(data):
    import altair as alt

    streamlit.subheader("Heatmap Severidade x Ambiente")

    heatmap = (
        data.groupby(["environment", "severity"])
        .size()
        .reset_index(name="count")
    )

    chart = alt.Chart(heatmap).mark_rect().encode(
        x="environment:N",
        y="severity:N",
        color="count:Q",
        tooltip=["environment", "severity", "count"]
    ).properties(
        height=300
    )

    streamlit.altair_chart(chart, width="stretch")


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
            "Taxa de Bugs Críticos",
            "Bugs mais frequentes",
            "Média de códigos de erro",
            "Bugs por ambiente",
            "Bugs por stack",
            "Timeline",
            "Heatmap"
        ],
        default=[
            "Distribuição de Severidade",
            "Taxa de Bugs Críticos",
            "Bugs mais frequentes"
        ]
    )

    col_a, col_b = streamlit.columns(2)

    if "Distribuição de Severidade" in opcao:
        with col_a:
            mostrar_distribuicao_severidade(data)

    if "Taxa de Bugs Críticos" in opcao:
        with col_b:
            mostrar_taxa_criticos(data)
    if "Bugs mais frequentes" in opcao:
        overtime_dashboard(data)

    if "Média de códigos de erro" in opcao:
        media_codigos_erro_dashboard(data)

    if "Bugs por ambiente" in opcao:
        bugs_por_ambiente_dashboard(data)

    if "Bugs por stack" in opcao:
        tech_stack_dashboard(data)

    if "Timeline" in opcao:
        bugs_timeline_dashboard(data)
    if "Heatmap" in opcao:
        heatmap_dashboard(data)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ETC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "etc"))

CLEAN_CSV_PATH = os.path.join(ETC_DIR, "bug_dataset_clean.csv")
RAW_CSV_PATH = os.path.join(ETC_DIR, "bug_dataset_50k.csv")


def main():
    try:
        if not os.path.isfile(CLEAN_CSV_PATH):
            sanitize_csv(CLEAN_CSV_PATH)

        cleaned_csv = read_csv(CLEAN_CSV_PATH)

    except FileNotFoundError:
        print("<[ERRO CRITICO]> Dataset ainda não existe após sanitização")
        return

    reports = BugReport.parse_csv(cleaned_csv)

    dashboard(reports)


if __name__ == '__main__':
    main()
