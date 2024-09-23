import pandas as pd

def get_data(filepath):
    """Lê os dados de um arquivo CSV com codificação alternativa."""
    return pd.read_csv(filepath, sep=';', header=0, encoding='ISO-8859-1', on_bad_lines='skip')

def normalize_data(df):
    """Normaliza as colunas numéricas e converte as colunas 'Data' e 'Hora' em datetime."""
    colunas_para_converter = ['Abertura', 'Máximo', 'Mínimo', 'Fechamento', 'Volume', 'Quantidade']

    def limpar_e_converter_coluna(coluna):
        coluna = coluna.astype(str)
        coluna = coluna.str.replace(r'[^\d.,]', '', regex=True)
        coluna = coluna.str.replace(r'\.(?=\d{3,})', '', regex=True)  # Remove pontos de milhar
        coluna = coluna.str.replace(',', '.', regex=True)  # Substituir vírgulas por pontos (para separadores decimais)
        return pd.to_numeric(coluna, errors='coerce')

    for coluna in colunas_para_converter:
        df[coluna] = limpar_e_converter_coluna(df[coluna])

    df['Data_Hora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S', dayfirst=True)
    df = df.sort_values('Data_Hora', ascending=True)

    return df

def valid_percentage(resultado_df, model):
  filtered_df = resultado_df[resultado_df[f'Acerto_{model}'] == 'Sim']
  percentage = (len(filtered_df) / len(resultado_df)) * 100
  print(f"Percentagem de acertos de {model}: {percentage:.2f}%")