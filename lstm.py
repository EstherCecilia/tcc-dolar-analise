import numpy as np # São usados para manipulação de arrays e dados.
import pandas as pd
from keras.models import Sequential # Usada para construir e treinar redes neurais.
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler  # Ferramenta do Scikit-Learn para normalizar os dados (transformar os valores entre 0 e 1), o que ajuda no desempenho do LSTM.

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

# Função para gerar decisões de compra, venda ou manutenção
def generate_decisions(df, period, model, scaler):
    X_test, _, _ = prepare_data(df, period)
    
    # Fazendo previsões
    previsoes = model.predict(X_test)
    previsoes = scaler.inverse_transform(previsoes)  # Desnormalizar
    
    decisoes = []
    for i in range(len(previsoes)):
        preco_fechamento_atual = df['Fechamento'].iloc[period + i]
        previsao_fechamento_futuro = previsoes[i][0]
        
        # Lógica de decisão
        if previsao_fechamento_futuro > preco_fechamento_atual:
            decisoes.append('Compra')
        elif previsao_fechamento_futuro < preco_fechamento_atual:
            decisoes.append('Venda')
        else:
            decisoes.append('Manter')
    
    return decisoes

def check_accuracies_lstm(df):
    # Verifica a precisão das decisões de LSTM em relação ao retorno futuro.
    df['Acerto_LSTM'] = df.apply(lambda row: 
                                 'Sim' if (row['Retorno'] > 0 and row['Decisao_LSTM'] == 'Compra') or
                                         (row['Retorno'] < 0 and row['Decisao_LSTM'] == 'Venda') or
                                         (row['Retorno'] == 0 and row['Decisao_LSTM'] == 'Manter') 
                                 else 'Não', axis=1)
    return df


def execute(df, period=30, epochs=10, batch_size=32):
    # Preparar os dados para treino
    X_train, y_train, scaler = prepare_data(df, period)

    # Treinar o modelo LSTM
    model = train_model(X_train, y_train, epochs=epochs, batch_size=batch_size)

    # Gerar decisões de compra, venda ou manutenção
    decisoes = generate_decisions(df, period, model, scaler)

    # Adicionar as decisões ao DataFrame original
    df_decisoes = df.iloc[period:].copy()  # Ignorar as primeiras linhas sem previsão
    df_decisoes['Decisao_LSTM'] = decisoes

    # Verificar acertos
    df_decisoes = check_accuracies_lstm(df_decisoes)

    return df_decisoes
