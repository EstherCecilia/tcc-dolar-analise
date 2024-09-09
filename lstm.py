import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def preparar_dados_para_lstm(df, n_steps=60):
    """Prepara os dados para a entrada no modelo LSTM."""
    scaler = MinMaxScaler(feature_range=(0, 1))
    df['Fechamento_Scaled'] = scaler.fit_transform(df['Fechamento'].values.reshape(-1,1))

    X, y = [], []
    for i in range(n_steps, len(df)):
        X.append(df['Fechamento_Scaled'][i-n_steps:i])
        y.append(df['Fechamento_Scaled'][i])
        
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    return X, y, scaler

def criar_modelo_lstm(input_shape):
    """Cria e compila o modelo LSTM."""
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    return model

def ajustar_modelo_lstm(df, n_steps=60, epochs=5, batch_size=32):
    """Ajusta o modelo LSTM aos dados de fechamento e faz previsões."""
    X, y, scaler = preparar_dados_para_lstm(df, n_steps)
    
    model = criar_modelo_lstm((X.shape[1], 1))
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
    
    previsoes_scaled = model.predict(X)
    previsoes = scaler.inverse_transform(previsoes_scaled)
    
    df['Previsao_LSTM'] = np.nan
    df.loc[n_steps:, 'Previsao_LSTM'] = previsoes.flatten()
    
    return df

def gerar_decisao_lstm(df):
    """Gera decisões de compra, venda ou manutenção com base nas previsões LSTM."""
    df['Decisao_LSTM'] = df.apply(lambda row: 
                                  'Compra' if row['Previsao_LSTM'] < row['Fechamento'] else
                                  'Venda' if row['Previsao_LSTM'] > row['Fechamento'] else
                                  'Manter', axis=1)
    return df

def verificar_acertos_lstm(df):
    """Verifica a precisão das decisões de LSTM em relação ao retorno futuro."""
    df['Acerto_LSTM'] = df.apply(lambda row: 
                                 'Sim' if (row['Retorno'] > 0 and row['Decisao_LSTM'] == 'Compra') or
                                         (row['Retorno'] < 0 and row['Decisao_LSTM'] == 'Venda') or
                                         (row['Retorno'] == 0 and row['Decisao_LSTM'] == 'Manter') 
                                 else 'Não', axis=1)
    return df

def adicionar_decisoes_lstm(df, n_steps=60, epochs=5, batch_size=32):
    """Função principal para ajustar o modelo LSTM, gerar decisões e verificar acertos."""
    df = ajustar_modelo_lstm(df, n_steps, epochs, batch_size)
    df = gerar_decisao_lstm(df)
    df = verificar_acertos_lstm(df)
    return df
