import pandas as pd
import numpy as np
import math

from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from tensorflow.keras.callbacks import EarlyStopping

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
df_out = df.sort_values('Data_Hora', ascending=False)
# Calcula o número de linhas correspondentes a 20%
num_linhas = math.ceil(len(df) * 0.2)

# Obtém os primeiros 20%
primeiros_20_porcento = df.head(30)
df_to_analyse = primeiros_20_porcento

print("\n============================= INICIO ==================================")
print("=======================================================================")

def analisar_decisao_media(df_periodo):
    sma = df_periodo['Fechamento'].mean()
    ema = df_periodo['Fechamento'].ewm(span=len(df_periodo)).mean().iloc[-1]
    vwap = (df_periodo['Fechamento'] * df_periodo['Volume']).sum() / df_periodo['Volume'].sum()
    ultimo_preco = df_periodo['Fechamento'].iloc[-1]

    # Cruzamento de Médias Móveis (Golden Cross e Death Cross) e vwap como suporte e resistência
    if ema > sma and ultimo_preco > vwap:
        decisao = 'Compra'
    elif ema < sma and ultimo_preco < vwap:
        decisao = 'Venda'
    else:
        decisao = 'Manter'

    return decisao

def analisar_decisao_arima(df_periodo, order=(0, 1, 1)):
    try:
        # Ajusta o modelo ARIMA
        model = ARIMA(df_periodo['Fechamento'], order=order)
        model_fit = model.fit()

        # Faz a previsão para o próximo período
        previsao = model_fit.forecast(steps=1).iloc[0]

        # Obtenha o último preço
        ultimo_preco = df_periodo['Fechamento'].iloc[-1]

        # Tomada de decisão com base na previsão do ARIMA
        if previsao > ultimo_preco:
            decisao = 'Compra'
        elif previsao < ultimo_preco:
            decisao = 'Venda'
        else:
            decisao = 'Manter'
    except Exception as e:
        print("Erro ao ajustar o modelo ARIMA")
        decisao = 'Erro'

    return decisao

def analisar_decisao_lstm(df_periodo, periodo=4, epochs=5, batch_size=32):
    # Preparar os dados para o LSTM
    dados = df_periodo['Fechamento'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    dados_normalizados = scaler.fit_transform(dados)

    # Verificar se há dados suficientes para o LSTM
    if len(dados_normalizados) <= periodo or len(df_to_analyse) < len(dados_normalizados):
        print(f"Dados insuficientes para o período de {periodo} minutos.")
        return 'Manter'  # Retorna 'Manter' se não houver dados suficientes

    # Criar o gerador de séries temporais
    generator = TimeseriesGenerator(dados_normalizados, dados_normalizados, length=periodo, batch_size=batch_size)

    # Construir o modelo LSTM
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(periodo, 1)))
    model.add(LSTM(units=50))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Usar Early Stopping para evitar o treinamento excessivo
    early_stopping = EarlyStopping(monitor='loss', patience=3)

    # Treinar o modelo
    model.fit(generator, epochs=epochs, batch_size=batch_size, verbose=0, callbacks=[early_stopping])

    # Fazer a previsão
    previsao_normalizada = model.predict(np.reshape(dados_normalizados[-periodo:], (1, periodo, 1)))
    previsao = scaler.inverse_transform(previsao_normalizada)

    # Obter o último preço de fechamento
    ultimo_preco = df_periodo['Fechamento'].iloc[-1]

    # Tomada de decisão com base na previsão do LSTM
    if previsao > ultimo_preco:
        decisao = 'Compra'
    elif previsao < ultimo_preco:
        decisao = 'Venda'
    else:
        decisao = 'Manter'

    return decisao

def verificar_acertos(df, periodos, analisar_decisao):
    resultados = []

    for periodo in periodos:
        print(f"Verificando acertos para período de {periodo} minutos")
        for i in range(0, len(df), periodo):
            df_periodo = df_out.iloc[i:i+periodo]
            decisao = analisar_decisao(df_periodo)
            preco_atual = df_out['Fechamento'].iloc[i+periodo-1]
            proximo_preco = df_out['Fechamento'].iloc[i+periodo]

            if decisao == 'Compra' and proximo_preco > preco_atual:
                acerto = 'Sim'
            elif decisao == 'Venda' and proximo_preco < preco_atual:
                acerto = 'Sim'
            elif decisao == 'Manter' and abs(proximo_preco - preco_atual) < 0.01:
                acerto = 'Sim'
            else:
                acerto = 'Não'

            resultados.append({
                'Data_Hora': df_out['Data_Hora'].iloc[i+periodo-1],
                'Decisão': decisao,
                'Valor_Dolar_Atual': preco_atual,
                'Valor_Dolar_Futuro': proximo_preco,
                'Acertou': acerto
            })

    return pd.DataFrame(resultados)

def valida_porcentagem(resultado_df):
  filtered_df = resultado_df[resultado_df['Acertou'] == 'Sim']
  percentage = (len(filtered_df) / len(resultado_df)) * 100
  print(f"Percentagem de acertos: {percentage:.2f}%")

periodos = [5, 15, 30, 60]
# periodos = [5]
print("Média movel")
resultado_df_media = verificar_acertos(df_to_analyse, periodos, analisar_decisao_media)

print("LSTM")
resultado_df_lstm = verificar_acertos(df_to_analyse, periodos, analisar_decisao_lstm)

print("ARIMA")
resultado_df_arima = verificar_acertos(df_to_analyse, periodos, analisar_decisao_arima)

print("Resultado Media")
valida_porcentagem(resultado_df_media)
print("Resultado LSTM")
valida_porcentagem(resultado_df_lstm)
print("Resultado Arima")
valida_porcentagem(resultado_df_arima)