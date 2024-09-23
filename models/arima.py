from statsmodels.tsa.arima.model import ARIMA

def adjust_arima_model(df, order=(5,1,0)):
    # Ajusta um modelo ARIMA ao preço de fechamento e adiciona previsões ao DataFrame.
    model = ARIMA(df['Fechamento'], order=order)
    model_fit = model.fit()
    df['Previsao_ARIMA'] = model_fit.predict(start=0, end=len(df)-1, typ='levels')
    return df

def generate_decision_arima(df):
    # Gera decisões de compra, venda ou manutenção com base nas previsões ARIMA.
    df['Decisao_ARIMA'] = df.apply(lambda row: 
                                   'Compra' if row['Previsao_ARIMA'] < row['Fechamento'] else
                                   'Venda' if row['Previsao_ARIMA'] > row['Fechamento'] else
                                   'Manter', axis=1)
    return df

def check_hits_arima(df):
    # Verifica a precisão das decisões de ARIMA em relação ao retorno futuro.
    df['Acerto_ARIMA'] = df.apply(lambda row: 
                                  'Sim' if (row['Retorno'] > 0 and row['Decisao_ARIMA'] == 'Compra') or
                                          (row['Retorno'] < 0 and row['Decisao_ARIMA'] == 'Venda') or
                                          (row['Retorno'] == 0 and row['Decisao_ARIMA'] == 'Manter') 
                                  else 'Não', axis=1)
    return df



def execute(df, period):    
    df = adjust_arima_model(df, order=(period,1,0))
    df = generate_decision_arima(df)
    df = check_hits_arima(df)

    return df
