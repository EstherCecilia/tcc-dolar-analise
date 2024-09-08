from main.abstractPredict import AbstractPredict

class Arima(AbstractPredict):
    def __init__(self, quantity_of_lines_to_analyse) -> None:
        self.results = []
        self.quantity_of_lines_to_analyse = quantity_of_lines_to_analyse
                
    def _analyse_decision(self, df_periodo):
        sma = df_periodo['Fechamento'].mean()
        ema = df_periodo['Fechamento'].ewm(span=len(df_periodo)).mean().iloc[-1]
        vwap = (df_periodo['Fechamento'] * df_periodo['Volume']).sum() / df_periodo['Volume'].sum()
        ultimo_preco = df_periodo['Fechamento'].iloc[-1]

        # Cruzamento de Médias Móveis (Golden Cross e Death Cross) e vwap como suporte e resistência
        if ema > sma and ultimo_preco > vwap:
            decisao = 'Compra'
        elif ema < sma and ultimo_preco < vwap:
            decisao = 'Venda'
        else:
            decisao = 'Manter'

        return decisao
