import pandas as pd
import math


# Tentar ler o CSV com uma codificação alternativa
df = pd.read_csv('ABEV3_B_0_1min.csv', sep=';', header=0, encoding='ISO-8859-1', on_bad_lines='skip')

# Colunas númericas
colunas_para_converter = ['Abertura', 'Máximo', 'Mínimo', 'Fechamento', 'Volume', 'Quantidade']

def limpar_e_converter_coluna(coluna):
    # Garantir que a coluna é do tipo string
    coluna = coluna.astype(str)
    # Remover caracteres não numéricos (mantendo apenas números e pontos/vírgulas)
    coluna = coluna.str.replace(r'[^\d.,]', '', regex=True)
    # Substituir pontos por vírgulas se necessário (dependendo do formato dos dados)
    coluna = coluna.str.replace(r'\.(?=\d{3,})', '', regex=True)  # Remove pontos de milhar
    coluna = coluna.str.replace(',', '.', regex=True)  # Substituir vírgulas por pontos (para separadores decimais)
    # Converter para numérico
    return pd.to_numeric(coluna, errors='coerce')

# Aplicar a função a cada coluna na lista
for coluna in colunas_para_converter:
    df[coluna] = limpar_e_converter_coluna(df[coluna])

# Converter colunas 'Data' e 'Hora' em datetime
df['Data_Hora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S', dayfirst=True)

# Ordenar os dados por Data_Hora (caso não estejam ordenados)
df = df.sort_values('Data_Hora', ascending=True)
# Calcula o número de linhas correspondentes a 20%
num_linhas = math.ceil(len(df) * 0.2)

# Obtém os primeiros 20%
primeiros_20_porcento = df.head(num_linhas)
data = primeiros_20_porcento

def analisar_decisao_media(df_periodo):
    sma = df_periodo['Fechamento'].mean()
    ema = df_periodo['Fechamento'].ewm(span=len(df_periodo)).mean().iloc[-1]

    # Cruzamento de Médias Móveis (Golden Cross e Death Cross)
    if ema > sma:
        decisao = 'Compra'
    elif ema < sma:
        decisao = 'Venda'
    else:
        decisao = 'Manter'

    return decisao


def verificar_acertos(df, periodos, analisar_decisao):
    resultados = []

    for periodo in periodos:
        print(f"Verificando acertos para período de {periodo} minutos")
        for i in range(0, len(df) - periodo, periodo):
            df_periodo = df.iloc[i:i+periodo]
            decisao = analisar_decisao(df_periodo)
            preco_atual = df['Fechamento'].iloc[i+periodo-1]
            proximo_preco = df['Fechamento'].iloc[i+periodo]

            if decisao == 'Compra' and proximo_preco > preco_atual:
                acerto = 'Sim'
            elif decisao == 'Venda' and proximo_preco < preco_atual:
                acerto = 'Sim'
            elif decisao == 'Manter' and abs(proximo_preco - preco_atual) < 0.01:
                acerto = 'Sim'
            else:
                acerto = 'Não'

            resultados.append({
                'Período': periodo, 
                'Tamanho_Período': len(df_periodo),
                'Data_Hora': df['Data_Hora'].iloc[i+periodo-1],
                'Decisão': decisao,
                'Valor_Dolar_Atual': preco_atual,
                'Valor_Dolar_Futuro': proximo_preco,
                'Acertou': acerto
            })

    return pd.DataFrame(resultados)


periodos = [5 ,15, 30, 60]
resultado_df_media = verificar_acertos(data, periodos, analisar_decisao_media)

print(resultado_df_media[resultado_df_media['Acertou'] == 'Sim'])

def valida_porcentagem(resultado_df):
  filtered_df = resultado_df[resultado_df['Acertou'] == 'Sim']
  percentage = (len(filtered_df) / len(resultado_df)) * 100
  print(f"Percentagem de acertos: {percentage:.2f}%")

valida_porcentagem(resultado_df_media)