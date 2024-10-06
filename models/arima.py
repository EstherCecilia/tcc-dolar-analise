from statsmodels.tsa.arima.model import ARIMA
import models.decisions as decisions

def adjust_arima_model(df, order=(5,1,0)):
    # Ajusta um modelo ARIMA ao preço de fechamento e adiciona previsões ao DataFrame.
    model = ARIMA(df['Fechamento'], order=order)
    model_fit = model.fit()
    df['ARIMA'] = model_fit.predict(start=0, end=len(df)-1, typ='levels')
    return df

def execute(df, period):    
    df = adjust_arima_model(df, order=(period,1,0))
    df = decisions.generate_decision(df, ['ARIMA'])
    df = decisions.check_hits(df, ['ARIMA'])

    return df
