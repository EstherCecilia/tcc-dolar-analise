import pandas as pd

PERCENT_ACCEPTABLE = 0.25

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

    df = df.iloc[::-1]

    return df

def calculate_acceptable_value_max(rolling_window):
    if len(rolling_window) < 15:
        return rolling_window.iloc[0]
    sorted_values = pd.Series(rolling_window).sort_values(ascending=False)
    quartile_size = int(len(sorted_values) * PERCENT_ACCEPTABLE)
    
    if quartile_size == 0:
        return None
    
    return sorted_values.iloc[0]  # Primeiro valor dos 25% maiores

# Função para calcular o valor aceitável mínimo
def calculate_acceptable_value_min(rolling_window):
    if len(rolling_window) < 15:
        return rolling_window.iloc[-1]
    sorted_values = pd.Series(rolling_window).sort_values(ascending=False)
    quartile_size = int(len(sorted_values) * PERCENT_ACCEPTABLE)
    
    if quartile_size == 0:
        return None
    
    return sorted_values.iloc[quartile_size - 1]  # Último valor dos 25% maiores

def generate_close_return(df, period):
    # Fechamento futuro do período seguinte seguinte 
    df['Fechamento Futuro'] = df['Fechamento'].shift(-1) 

    # Ganho ou perda com base no período seguinte
    df['Retorno'] = df['Fechamento Futuro'] - df['Fechamento']

    df['valor_aceitavel_retorno_max'] = df['Retorno'].rolling(window=period).apply(calculate_acceptable_value_max, raw=False)
    df['valor_aceitavel_retorno_min'] = df['Retorno'].rolling(window=period).apply(calculate_acceptable_value_min, raw=False)

    df['valor_aceitavel_fechamento_max'] = df['Fechamento'].rolling(window=period).apply(calculate_acceptable_value_max, raw=False)
    df['valor_aceitavel_fechamento_min'] = df['Fechamento'].rolling(window=period).apply(calculate_acceptable_value_min, raw=False)
    

    return df

def generate_percentage_by_model(result_df, model):
  result_valid = result_df[result_df[f'Decisao_{model}'] != 'Manter']
  print(f'Valor total apurado no modelo {model}: {len(result_valid)}')
  if len(result_valid) == 0:
        return 0

  filtered_df = result_valid[result_valid[f'Acerto_{model}'] == 'Sim']
  percentage = (len(filtered_df) / len(result_valid)) * 100
  return percentage

def round_to_05(return_value):
    if return_value is None or pd.isna(return_value):
      return 0
      
    return round(return_value * 2) / 2

def calculates_gain_by_model(result_df, model):
    # Função condicional para tratar as decisões
    def compute_gain(row):
        retorno = round_to_05(row['Retorno'])

        if row[f'Decisao_{model}'] == 'Venda' and retorno < 0: # Quando for Venda e o Retorno negativo  -> Somar Módulo
            return abs(retorno) * 10
        elif row[f'Decisao_{model}'] == 'Venda' and retorno > 0:
            return -abs(retorno)  * 10
        elif row[f'Decisao_{model}'] == 'Manter': # Ignorar quando for "Manter"
            return 0
        else:
            return retorno * 10 # Somar o restante normalmente
    # Aplicar a função para calcular os ganhos
    result_df['Retorno_Ajustado'] = result_df.apply(compute_gain, axis=1)
    gain = result_df['Retorno_Ajustado'].sum()

    return gain
