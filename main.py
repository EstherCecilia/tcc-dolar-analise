import pandas as pd
import math
import arima
import average
import preprossing
import lstm

def run(period, filepath, path, percent = 0.2):
    # Lê os dados do arquivo CSV
    df = preprossing.get_data(filepath)

    # Normaliza os dados
    df = preprossing.normalize_data(df)


    # Obtém os primeiros 20%
    num_linhas = math.ceil(len(df) * percent)
    primeiros_x_porcento = df.head(num_linhas)
    data = primeiros_x_porcento

    # Fechamento futuro do período seguinte seguinte 
    data['Fechamento Futuro'] = data['Fechamento'].shift(-1) 

    # Ganho ou perda com base no período seguinte
    data['Retorno'] = data['Fechamento Futuro'] - data['Fechamento']


    # (SMA, EMA, VWAP)
    data = average.execute(data, period)

   # ARIMA
    data = arima.execute(data, period)

   # LSTM
    data = lstm.execute(data, period)


    print(f"Percentagem de acertos de {path} no periodo {period}")
    preprossing.valid_percentage(data, 'SMA')
    preprossing.valid_percentage(data, 'EMA')
    preprossing.valid_percentage(data, 'VWAP')
    preprossing.valid_percentage(data, 'ARIMA')
    preprossing.valid_percentage(data, 'LSTM')

    filepathResult = f'report/indicadores_{period}_' + path  + '.csv'
    data.to_csv(filepathResult, index=False, sep=';', encoding='utf-8')

run(30, 'dados/ABEV3_B_0_1min.csv', 'ABEV3_B_0_1min')

# porcentagem ideal: 54%