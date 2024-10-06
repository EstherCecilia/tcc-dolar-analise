import models.decisions as decisions

def add_averages(df, period):
    # Calculando a média móvel simples (SMA) e a média móvel exponencial (EMA)
    df['SMA'] = df['Fechamento'].rolling(window=period).mean()
    df['EMA'] = df['Fechamento'].ewm(span=period, adjust=False).mean()

    # VWAP é calculado acumulando (preço * volume) e dividindo pelo volume acumulado
    df['VWAP'] = (df['Fechamento'] * df['Volume']).rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()

    return df

def execute(df, period):
    models = ['SMA', 'EMA', 'VWAP']
    df = add_averages(df, period)
    df = decisions.generate_decision(df, models)
    df = decisions.check_hits(df, models)

    return df