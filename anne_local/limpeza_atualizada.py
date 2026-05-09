import pandas as pd

# 1. Carregar dataset com separador correto
df = pd.read_csv("bug_dataset_50k.csv", sep=";")
print("Inicial:", df.shape)

# 2. Remover linhas com valores nulos
df = df.dropna()
print("Após remover nulos:", df.shape)

# 3. Remover coluna identificadora (bug_id) ANTES de checar duplicatas
print("Bug IDs únicos antes da remoção:", df['bug_id'].nunique(), df.shape[0])
df = df.drop(columns=['bug_id'])
print("Colunas após remover bug_id:", df.columns)

# 4. Normalizar texto
for col in df.select_dtypes(include='str').columns:
    if col != 'created_at':
        df[col] = df[col].str.lower().str.strip()

# 5. Remover duplicados (após remover bug_id e normalizar)
df = df.drop_duplicates()
print("Após remover duplicados:", df.shape)

# 6. Converter coluna de data com formato explícito
df['created_at'] = pd.to_datetime(df['created_at'], format='%d/%m/%Y', errors='coerce')

# 7. Converter coluna numérica
df['error_code'] = pd.to_numeric(df['error_code'], errors='coerce')

# 8. Converter colunas categóricas (após normalização)
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