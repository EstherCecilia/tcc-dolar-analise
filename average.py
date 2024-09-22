import pandas as pd

def add_averages(df, period):
    # Calculando a média móvel simples (SMA) e a média móvel exponencial (EMA)
    df['SMA'] = df['Fechamento'].rolling(window=period).mean()
    df['EMA'] = df['Fechamento'].ewm(span=period, adjust=False).mean()

    # VWAP é calculado acumulando (preço * volume) e dividindo pelo volume acumulado
    df['VWAP'] = (df['Fechamento'] * df['Volume']).rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()

    return df

# Função para determinar a decisão com base em um indicador específico
def decision_by_per(close, indicator):
    if close > indicator:
        return 'Venda'
    elif close < indicator:
        return 'Compra'
    else:
        return 'Manter' # Manter se o ganho não for tão grande | gerar uma média de ganho (limiar)

# Função principal para gerar decisões de compra, venda ou manter
def generate_decision(df, period):
    df['Decisao_SMA'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row['SMA']), axis=1)

    # Gerando decisões com base na EMA
    df['Decisao_EMA'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row['EMA']), axis=1)

    # Gerando decisões com base na VWAP
    df['Decisao_VWAP'] = df.apply(lambda row: decision_by_per(row['Fechamento'], row['VWAP']), axis=1)

    return df

# Função para calcular o valor aceitável máximo
def calcular_valor_aceitavel_max(rolling_window):
    sorted_values = pd.Series(rolling_window).sort_values(ascending=False)
    quartile_size = int(len(sorted_values) * 0.25)
    
    if quartile_size == 0:
        return None
    
    return sorted_values.iloc[0]  # Primeiro valor dos 25% maiores

# Função para calcular o valor aceitável mínimo
def calcular_valor_aceitavel_min(rolling_window):
    sorted_values = pd.Series(rolling_window).sort_values(ascending=False)
    quartile_size = int(len(sorted_values) * 0.25)
    
    if quartile_size == 0:
        return None
    
    return sorted_values.iloc[quartile_size - 1]  # Último valor dos 25% maiores

# Função para verificar se a decisão foi acertada
def check_hit(decision, retorno, max, min):
    def dentro_do_limiar(retorno, max, min):
        retorno = abs(retorno) # Módulo
        return retorno >= min and retorno <= max

    # TODO: Dúvida sobre comportamento abaixo, checar com Charlene se é para desconsiderar a decisão se estiver fora do limiar
    # if (not dentro_do_limiar(retorno, max, min) and decision == 'Manter' ) or \
    if (not dentro_do_limiar(retorno, max, min)) or \
       (retorno > 0 and dentro_do_limiar(retorno, max, min) and decision == 'Compra') or \
       (retorno < 0 and dentro_do_limiar(retorno, max, min) and decision == 'Venda') or \
       (retorno == 0 and decision == 'Manter'):
        return 'Sim'
    else:
        return 'Não'

# Função principal para verificar acertos com base em vários períodos
def check_hits(df):
    # Verificando acertos para SMA
    df['Acerto_SMA'] = df.apply(lambda row: check_hit(row['Decisao_SMA'], row['Retorno'], row['valor_aceitavel_max'], row['valor_aceitavel_min']), axis=1)

    # Verificando acertos para EMA
    df['Acerto_EMA'] = df.apply(lambda row: check_hit(row['Decisao_EMA'], row['Retorno'], row['valor_aceitavel_max'], row['valor_aceitavel_min']), axis=1)

    # Verificando acertos para VWAP
    df['Acerto_VWAP'] = df.apply(lambda row: check_hit(row['Decisao_VWAP'], row['Retorno'], row['valor_aceitavel_max'], row['valor_aceitavel_min']), axis=1)

    return df


def execute(df, period):
    df = add_averages(df, period)
    df['valor_aceitavel_max'] = df['Retorno'].rolling(window=period).apply(calcular_valor_aceitavel_max, raw=False)
    df['valor_aceitavel_min'] = df['Retorno'].rolling(window=period).apply(calcular_valor_aceitavel_min, raw=False)
    df = generate_decision(df, period)
    df = check_hits(df)

    return df