import pandas as pd
import warnings
import math
import models.arima as arima
import models.average as average
import models.preprocessing as preprocessing
import models.lstm as lstm

# Suprimir todos os warnings
warnings.filterwarnings('ignore')

function_by_model = {
    'SMA': average.execute,
    'EMA': average.execute,
    'VWAP': average.execute,
    'ARIMA': arima.execute,
    'LSTM': lstm.execute
}


def run(period, path, percent = 0.8):
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

    # Caminho para salvar o arquivo
    file_path = f"results/{path}_{period}_accuracy_and_gain.txt"


    # Abre o arquivo no modo de escrita ('w' sobrescreve o arquivo, 'a' adiciona ao final)
    with open(file_path, 'w') as f:
        # Adicionar acurácia por ganho ou perda por porcentagem
        for model in function_by_model.keys():
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


# run(30, 'ABEV3_B_0_1min')
run(30, 'IBOV_B_0_1min')

# Orientações:
# porcentagem ideal: 54%
# Comprar por lote (valor multiplicado por 100)