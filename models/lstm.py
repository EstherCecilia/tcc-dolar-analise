import numpy as np # São usados para manipulação de arrays e dados.
import pandas as pd
from keras.models import Sequential # Usada para construir e treinar redes neurais.
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler  # Ferramenta do Scikit-Learn para normalizar os dados (transformar os valores entre 0 e 1), o que ajuda no desempenho do LSTM.
import models.decisions as decisions

# Função para preparar os dados em janelas de tempo (30 minutos, por exemplo)
def prepare_data(df, period):
    # Normalizando os dados entre 0 e 1
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_scaled = scaler.fit_transform(df[['Fechamento']])
    
    # Criando as janelas de tempo
    X, y = [], []
    for i in range(period, len(df_scaled)):
        X.append(df_scaled[i-period:i, 0])  # Usar o período de minutos
        y.append(df_scaled[i, 0])  # Previsão é o fechamento do próximo período
    
    # Convertendo para numpy arrays
    X, y = np.array(X), np.array(y)
    
    # Reshaping para [samples, time_steps, features], necessário para o LSTM
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler

# Função para treinar o modelo LSTM
def train_model(X_train, y_train, epochs=10, batch_size=32):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(units=1))  # Saída única para prever o preço

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)
    
    return model

def predict_future(df, model, scaler, period):
    # Normalizar os dados de 'Fechamento'
    df_scaled = scaler.transform(df[['Fechamento']].values)

    # Inicializar uma lista para armazenar as previsões
    predictions = []

    # Loop para fazer a previsão a partir do valor no índice 'period'
    for i in range(period, len(df)):
        # Selecionar os últimos 'period' valores para fazer a previsão
        input_data = df_scaled[i-period:i].reshape(1, period, 1)
        
        # Fazer a previsão usando o modelo
        predicted_scaled = model.predict(input_data)
        
        # Inverter a escala da previsão para o valor original
        predicted = scaler.inverse_transform(predicted_scaled)[0][0]
        
        # Armazenar a previsão
        predictions.append(predicted)
    
    # Preencher a coluna 'LSTM' com NaN nos primeiros 'period' registros (sem previsão) e depois as previsões
    df['LSTM'] = np.nan
    df['LSTM'].iloc[period:] = predictions

    return df

def execute(df, period=30, epochs=5, batch_size=2):
    # Preparar os dados para treino
    X_train, y_train, scaler = prepare_data(df, period)

    # Treinar o modelo LSTM
    model = train_model(X_train, y_train, epochs=epochs, batch_size=batch_size)

    # Gerar previsões futuras e preencher a coluna 'LSTM'
    df = predict_future(df, model, scaler, period)

    # Gerar decisões de compra, venda ou manter
    df = decisions.generate_decision(df, ['LSTM'])

    # Verificar acertos
    df = decisions.check_hits(df, ['LSTM'])

    return df