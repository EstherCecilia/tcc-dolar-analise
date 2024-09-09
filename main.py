import pandas as pd
import math
import arima
import average
import preprossing
import lstm

def run(periodo, filepath, percent = 0.2):
    df = preprossing.get_data(filepath)
    df = preprossing.normalize_data(df)


    # Obtém os primeiros 20%
    num_linhas = math.ceil(len(df) * percent)
    primeiros_x_porcento = df.head(num_linhas)
    data = primeiros_x_porcento

    n_forward = periodo 
    data['Fechamento Futuro'] = data['Fechamento'].shift(-n_forward) # Close periodo minutos ago
    data['Retorno'] = data['Fechamento Futuro'] - data['Fechamento']

    periodos = [periodo]

    # (SMA, EMA, VWAP)
    data = average.add_averages(data, periodos)
    data = average.generate_decision(data, periodos)
    data = average.verificar_acertos(data, periodos)

    # ARIMA
    # data = arima.add_decisions_arima(data)
    # data = arima.verificar_acertos_arima(data)

    # LSTM
    # data = lstm.adicionar_decisoes_lstm(data)


    print(data.head())

    filepathResult = f'indicadores_{periodo}_' + filepath 
    data.to_csv(filepathResult, index=False, sep=';', encoding='utf-8')

run(30, 'ABEV3_B_0_1min.csv')