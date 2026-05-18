
import pandas as pd

# 1. Carregar dataset com separador correto ","
df = pd.read_csv("bug_dataset_50k.csv", sep=",")
print("Inicial:", df.shape)

# 2. Remover linhas com valores nulos
df = df.dropna()
print("Após remover nulos:", df.shape)

# 3. Remover coluna identificadora (bug_id) ANTES de checar duplicatas
print("Bug IDs únicos antes da remoção:", df['bug_id'].nunique(), df.shape[0])
df = df.drop(columns=['bug_id'])
print("Colunas após remover bug_id:", df.columns)

# 4. Normalizar texto
# include=object - str não reconhecido
for col in df.select_dtypes(include='object').columns:
    if col != 'created_at':
        df[col] = df[col].str.lower().str.strip()

# 4.1 Remover redundâncias fixas nas colunas
padroes_remover = {
    "title": [
        {"string": "detected in system", "posicao": "fim"}
    ],
    "description": [
        {"string": "this issue relates to a", "posicao": "inicio"},
        {"string": "occurring in the application", "posicao": "fim"}
    ],
    "root_cause": [
        {"string": "misconfiguration or logic issue related to", "posicao": "inicio"}
    ],
    "suggested_fix": [
        {"string": "review and fix the", "posicao": "inicio"},
        {"string": "to best practices", "posicao": "fim"}
    ],
    "explanation": [
        {"string": "this bug requires a", "posicao": "inicio"},
        {"string": "due to its nature.", "posicao": "fim"}
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
df['created_at'] = pd.to_datetime(
    df['created_at'], format='%Y-%m-%d', errors='coerce')

# 5.1 Remover a hora, mantendo apenas a data
df['created_at'] = df['created_at'].dt.date

# 6. Converter coluna numérica
df['error_code'] = pd.to_numeric(df['error_code'], errors='coerce')

# 7. Converter colunas categóricas (após normalização)
df['severity'] = df['severity'].astype('category')
df['environment'] = df['environment'].astype('category')

# 9. Verificação final
print(df.head())
print(df.info())
print("Valores únicos em severity:", df['severity'].unique())
print("Valores únicos em environment:", df['environment'].unique())
print("Duplicados restantes:", df.duplicated().sum())
print("Nulos restantes:\n", df.isnull().sum())
print("Distribuição error_code:\n", df['error_code'].describe())

# 10. Salvar
# Salvar em CSV (mais universal, abre em Excel)
df.to_csv("bug_dataset_clean.csv", index=False)

# Salvar em Parquet (mantém tipos e é mais eficiente)
df.to_parquet("bug_dataset_clean.parquet", index=False)


print("Arquivos salvos com sucesso!")
