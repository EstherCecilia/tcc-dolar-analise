def within_the_threshold(return_value, max, min):
    return_value = abs(return_value) # Módulo
    return return_value >= min and return_value <= max

def decision_by_combination(row, models):
    decisions = [row[f'Decisao_{model}'] for model in models]
    # Verifica se todas as decisões são iguais
    if len(set(decisions)) == 1:
        return decisions[0]  # Retorna a decisão única
    return 'Manter'

def generate_decicion_by_combination_models(df, model):
    models = model.split('_')
    df[f'Decisao_{model}'] = df.apply(lambda row: decision_by_combination(row, models), axis=1)
    return df
    
# Função para determinar a decisão com base em um indicador específico
def decision_by_per(row, model):
    close = row['Fechamento']
    indicator = row[model]

    # Não opera se estiver fora do limiar dos 25% maiores entre o periodo
    if not within_the_threshold(close, row['valor_aceitavel_fechamento_max'], row['valor_aceitavel_fechamento_min']):
        return 'Manter'

    if close < indicator:
        return 'Compra'
    elif close > indicator:
        return 'Venda'
    else:
        return 'Manter' 

# Função principal para gerar decisões de compra, venda ou manter
def generate_decision(df, models):

    for model in models:
        df[f'Decisao_{model}'] = df.apply(lambda row: decision_by_per(row, model), axis=1)

    return df

# Função para verificar se a decisão foi acertada
def check_hit(row, model):
    future_return = row['Retorno']
    decision = row[f'Decisao_{model}']
    
    if not within_the_threshold(future_return, row['valor_aceitavel_retorno_min'], row['valor_aceitavel_retorno_max']) and decision == 'Manter':
        return 'Sim'

    if (future_return > 0 and decision == 'Compra') or \
       (future_return <= 0 and decision == 'Venda') or \
       (decision == 'Manter'):
        return 'Sim'
    else:
        return 'Não'

# Função principal para verificar acertos com base em vários períodos
def check_hits(df, models):
    for model in models:
        df[f'Acerto_{model}'] = df.apply(lambda row: check_hit(row, model), axis=1)

    return df
