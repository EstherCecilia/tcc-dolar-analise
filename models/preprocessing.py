import pandas as pd

def get_data(filepath):
    # Lê os dados de um arquivo CSV com codificação alternativa.
    return pd.read_csv(filepath, sep=';', header=0, encoding='ISO-8859-1', on_bad_lines='skip')

def normalize_data(df):
    # Normaliza as colunas numéricas e converte as colunas 'Data' e 'Hora' em datetime.
    colunas_para_converter = ['Abertura', 'Máximo', 'Mínimo', 'Fechamento', 'Volume', 'Quantidade']

    def limpar_e_converter_coluna(coluna):
        coluna = coluna.astype(str)
        coluna = coluna.str.replace(r'[^\d.,]', '', regex=True)
        coluna = coluna.str.replace(r'\.(?=\d{3,})', '', regex=True)  # Remove pontos de milhar
        coluna = coluna.str.replace(',', '.', regex=True)  # Substituir vírgulas por pontos (para separadores decimais)
        return pd.to_numeric(coluna, errors='coerce')

    for coluna in colunas_para_converter:
        df[coluna] = limpar_e_converter_coluna(df[coluna])

    df = df.sort_values('Data', ascending=True)

    return df

def generate_close_return(df):
    # Fechamento futuro do período seguinte seguinte 
    df['Fechamento Futuro'] = df['Fechamento'].shift(-1) 

    # Ganho ou perda com base no período seguinte
    df['Retorno'] = df['Fechamento Futuro'] - df['Fechamento']

    return df

def valid_percentage(resultado_df, model):
  filtered_df = resultado_df[resultado_df[f'Acerto_{model}'] == 'Sim']
  percentage = (len(filtered_df) / len(resultado_df)) * 100
  return percentage

def calculates_gain(resultado_df, model):
    filtered_df = resultado_df[resultado_df[f'Acerto_{model}'] == 'Sim']

    # Função condicional para tratar as decisões
    def compute_gain(row):
        if row[f'Decisao_{model}'] == 'Venda' and row['Retorno'] < 0: # Quando for Venda e o Retorno negativo  -> Somar Módulo
            return abs(row['Retorno'])
        elif row[f'Decisao_{model}'] == 'Manter': # Ignorar quando for "Manter"
            return 0  
        else:
            return row['Retorno']  # Somar o restante normalmente

    # Aplicar a função para calcular os ganhos
    filtered_df['Retorno_Ajustado'] = filtered_df.apply(compute_gain, axis=1)
    gain = filtered_df['Retorno_Ajustado'].sum()

    return gain