def add_averages(df, period):
    # Calculando a média móvel simples (SMA) e a média móvel exponencial (EMA)
    df['SMA'] = df['Fechamento'].rolling(window=period).mean()
    df['EMA'] = df['Fechamento'].ewm(span=period, adjust=False).mean()

    # VWAP é calculado acumulando (preço * volume) e dividindo pelo volume acumulado
    df['VWAP'] = (df['Fechamento'] * df['Volume']).rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()

    return df

# Função para determinar a decisão com base em um indicador específico
def decision_by_per(close, indicator):
    if close < indicator:
        return 'Compra'
    elif close > indicator:
        return 'Venda'
    else:
        return 'Manter' # Manter se o ganho não for tão grande | gerar uma média de ganho (limiar)

# Função principal para gerar decisões de compra, venda ou manter
def generate_decision(df, period):
    df[f'Decisao_SMA'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row['SMA']), axis=1)

    # Gerando decisões com base na EMA
    df['Decisao_EMA'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row['EMA']), axis=1)

    # Gerando decisões com base na VWAP
    df['Decisao_VWAP'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row['VWAP']), axis=1)

    return df

# Função para verificar se a decisão foi acertada
def check_hit(decision, future_return):
    if (future_return > 0 and decision == 'Compra') or \
       (future_return < 0 and decision == 'Venda') or \
       (future_return == 0 and decision == 'Manter'):
        return 'Sim'
    else:
        return 'Não'

# Função principal para verificar acertos com base em vários períodos
def check_hits(df):
    # Verificando acertos para SMA
    df['Acerto_SMA'] = df.apply(lambda row: check_hit(row['Decisao_SMA'], row['Retorno']), axis=1)

    # Verificando acertos para EMA
    df['Acerto_EMA'] = df.apply(lambda row: check_hit(row['Decisao_EMA'], row['Retorno']), axis=1)

    # Verificando acertos para VWAP
    df['Acerto_VWAP'] = df.apply(lambda row: check_hit(row['Decisao_VWAP'], row['Retorno']), axis=1)

    return df


def execute(df, period):
    df = add_averages(df, period)
    df = generate_decision(df, period)
    df = check_hits(df)

    return df