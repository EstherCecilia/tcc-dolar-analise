from statsmodels.tsa.arima.model import ARIMA

def ajustar_modelo_arima(df, order=(5,1,0)):
    """Ajusta um modelo ARIMA ao preço de fechamento e adiciona previsões ao DataFrame."""
    model = ARIMA(df['Fechamento'], order=order)
    model_fit = model.fit()
    df['Previsao_ARIMA'] = model_fit.predict(start=0, end=len(df)-1, typ='levels')
    return df

def gerar_decisao_arima(df):
    """Gera decisões de compra, venda ou manutenção com base nas previsões ARIMA."""
    df['Decisao_ARIMA'] = df.apply(lambda row: 
                                   'Compra' if row['Previsao_ARIMA'] < row['Fechamento'] else
                                   'Venda' if row['Previsao_ARIMA'] > row['Fechamento'] else
                                   'Manter', axis=1)
    return df

def verificar_acertos_arima(df):
    """Verifica a precisão das decisões de ARIMA em relação ao retorno futuro."""
    df['Acerto_ARIMA'] = df.apply(lambda row: 
                                  'Sim' if (row['Retorno'] > 0 and row['Decisao_ARIMA'] == 'Compra') or
                                          (row['Retorno'] < 0 and row['Decisao_ARIMA'] == 'Venda') or
                                          (row['Retorno'] == 0 and row['Decisao_ARIMA'] == 'Manter') 
                                  else 'Não', axis=1)
    return df

def add_decisions_arima(df, order=(5,1,0)):
    """Função principal para ajustar o modelo ARIMA, gerar decisões e verificar acertos."""
    df = ajustar_modelo_arima(df, order)
    df = gerar_decisao_arima(df)
    df = verificar_acertos_arima(df)
    return df
