def add_averages(df, periodos):
    for periodo in periodos:
        # Calculando a média móvel simples (SMA) e a média móvel exponencial (EMA)
        df[f'SMA_{periodo}'] = df['Fechamento'].rolling(window=periodo).mean()
        df[f'EMA_{periodo}'] = df['Fechamento'].ewm(span=periodo, adjust=False).mean()

        # VWAP é calculado acumulando (preço * volume) e dividindo pelo volume acumulado
        df[f'VWAP_{periodo}'] = (df['Fechamento'] * df['Volume']).rolling(window=periodo).sum() / df['Volume'].rolling(window=periodo).sum()

    return df

# Função para determinar a decisão com base em um indicador específico
def decision_by_per(close, indicator):
    if close > indicator:
        return 'Compra'
    elif close < indicator:
        return 'Venda'
    else:
        return 'Manter'

# Função principal para gerar decisões de compra, venda ou manter
def generate_decision(df, periodos):
    for periodo in periodos:
        # Gerando decisões com base na SMA
        df[f'Decisao_SMA_{periodo}'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row[f'SMA_{periodo}']), axis=1)

        # Gerando decisões com base na EMA
        df[f'Decisao_EMA_{periodo}'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row[f'EMA_{periodo}']), axis=1)

        # Gerando decisões com base na VWAP
        df[f'Decisao_VWAP_{periodo}'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row[f'VWAP_{periodo}']), axis=1)

    return df

# Função para verificar se a decisão foi acertada
def verificar_acerto(decisao, retorno_futuro):
    if (retorno_futuro > 0 and decisao == 'Compra') or \
       (retorno_futuro < 0 and decisao == 'Venda') or \
       (retorno_futuro == 0 and decisao == 'Manter'):
        return 'Sim'
    else:
        return 'Não'
        
# Função principal para verificar acertos com base em vários períodos
def verificar_acertos(df, periodos):
    for periodo in periodos:
        # Verificando acertos para SMA
        df[f'Acerto_SMA_{periodo}'] = df.apply(lambda row: verificar_acerto(row[f'Decisao_SMA_{periodo}'], row['Retorno']), axis=1)

        # Verificando acertos para EMA
        df[f'Acerto_EMA_{periodo}'] = df.apply(lambda row: verificar_acerto(row[f'Decisao_EMA_{periodo}'], row['Retorno']), axis=1)

        # Verificando acertos para VWAP
        df[f'Acerto_VWAP_{periodo}'] = df.apply(lambda row: verificar_acerto(row[f'Decisao_VWAP_{periodo}'], row['Retorno']), axis=1)

    return df