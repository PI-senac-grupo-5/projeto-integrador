import pandas as pd

# 1. Carregar dataset original
df = pd.read_csv("bug_dataset_50k.csv")
print("Inicial:", df.shape)

# 2. Remover duplicados
df = df.drop_duplicates()
print("Após remover duplicados:", df.shape)

# 3. Remover linhas com valores nulos
df = df.dropna()
print("Após remover nulos:", df.shape)

# 4. Remover coluna identificadora (bug_id)
print("Bug IDs únicos antes da remoção:", df['bug_id'].nunique(), df.shape[0])
df = df.drop(columns=['bug_id'])
print("Colunas após remover bug_id:", df.columns)

# 5. Converter coluna de data
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

# 6. Converter coluna numérica (se tiver valores numéricos em texto)
df['error_code'] = pd.to_numeric(df['error_code'], errors='coerce')

# 7. Converter colunas categóricas para category (otimização de memória)
df['severity'] = df['severity'].astype('category')
df['environment'] = df['environment'].astype('category')

# 8. Normalizar texto em colunas categóricas (minúsculo + remover espaços extras)
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.lower().str.strip()

# 9. Checar estatísticas básicas e estrutura final
print(df.head())
print(df.info())
print("Valores únicos em severity:", df['severity'].unique())
print("Valores únicos em environment:", df['environment'].unique())
print("Duplicados restantes:", df.duplicated().sum())
print("Nulos restantes:\n", df.isnull().sum())
print("Distribuição error_code:\n", df['error_code'].describe())

# Salvar em CSV (mais universal, abre em Excel)
df.to_csv("bug_dataset_clean.csv", index=False)

# Salvar em Parquet (mantém tipos e é mais eficiente)
df.to_parquet("bug_dataset_clean.parquet", index=False)
