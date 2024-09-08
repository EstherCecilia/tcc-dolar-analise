import numpy as np
from main.abstractPredict import AbstractPredict

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore
from tensorflow.keras.callbacks import EarlyStopping # type: ignore

class Lstm(AbstractPredict):
    def __init__(self, quantity_of_lines_to_analyse) -> None:
        self.results = []
        self.quantity_of_lines_to_analyse = quantity_of_lines_to_analyse

    def _analyse_decision(self, df_periodo, periodo=4, epochs=5, batch_size=32):
        # Preparar os dados para o LSTM
        dados = df_periodo['Fechamento'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        dados_normalizados = scaler.fit_transform(dados)

        # Verificar se há dados suficientes para o LSTM
        if len(dados_normalizados) <= periodo or self.quantity_of_lines_to_analyse < len(dados_normalizados):
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

    