import pandas as pd
import warnings
import math
import models.arima as arima
import models.average as average
import models.preprocessing as preprocessing
import models.lstm as lstm
import models.decisions as decisions

# Suprimir todos os warnings
warnings.filterwarnings('ignore')

function_by_model = {
    'SMA': average.execute,
    'EMA': average.execute,
    'VWAP': average.execute,
    'ARIMA': arima.execute,
    'LSTM': lstm.execute
}


function_combined_model = ['SMA_EMA', 'SMA_EMA_VWAP', 'VWAP_LSTM', 'VWAP_ARIMA', 'LSTM_ARIMA', 'SMA_EMA_VWAP_LSTM_ARIMA']

def run(period, path, percent = 1):
    # Lê os dados do arquivo CSV
    filepath = f'dados/{path}.csv'
    df = preprocessing.get_data(filepath)

    # Normaliza os dados
    df = preprocessing.normalize_data(df)


    # Obtém os primeiros de acordo com a porcentagem
    num_linhas = math.ceil(len(df) * percent)
    primeiros_x_porcento = df.head(num_linhas)
    data = primeiros_x_porcento

    # Adiciona o fechamento futuro e o retorno
    data = preprocessing.generate_close_return(data, period)  


    # (SMA, EMA, VWAP)
    for model in function_by_model:
        data = function_by_model[model](data, period)

    for model in function_combined_model:
        data = decisions.generate_decicion_by_combination_models(data, model)
        data = decisions.check_hits(data, [model])

    # Caminho para salvar o arquivo
    file_path = f"results/{path}_{period}_accuracy_and_gain.txt"


    # Abre o arquivo no modo de escrita ('w' sobrescreve o arquivo, 'a' adiciona ao final)
    with open(file_path, 'w') as f:
        # Adicionar acurácia por ganho ou perda por porcentagem
        models = list(function_by_model.keys()) + function_combined_model
        for model in models:
            percentage = preprocessing.generate_percentage_by_model(data, model)
            output_percentage = f"Percentagem de acertos de {model}: {percentage:.2f}%"
            print(output_percentage)
            f.write(output_percentage + '\n')  # Escreve a saída no arquivo
        
        # Adicionar acurácia por ganho ou perda por valor
        for model in function_by_model.keys():
            gain = preprocessing.calculates_gain_by_model(data, model)
            output_gain = f"Ganho de {model}: {gain:.2f}"
            print(output_gain)
            f.write(output_gain + '\n')  # Escreve a saída no arquivo
 

    data_filtered = data.drop(columns=['valor_aceitavel_fechamento_max', 'valor_aceitavel_fechamento_min', 'valor_aceitavel_retorno_max', 'valor_aceitavel_retorno_min'])

    # Salvar os resultados em um arquivo CSV
    file_path_result = f'report/indicadores_{period}_' + path  + '.csv'
    data_filtered.to_csv(file_path_result, index=False, sep=';', encoding='utf-8')


run(2,'WDOFUT_F_0_1min')
run(5,'WDOFUT_F_0_1min')
run(15,'WDOFUT_F_0_1min')
run(30,'WDOFUT_F_0_1min')
run(45,'WDOFUT_F_0_1min')
run(60,'WDOFUT_F_0_1min')
run(24,'WDOFUT_F_0_60min')

# Orientações:
# porcentagem ideal: 54%
# Comprar por lote (valor multiplicado por 100)