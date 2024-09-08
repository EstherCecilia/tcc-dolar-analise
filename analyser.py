import pandas as pd

class Analyser:
    def __init__(self, path_to_csv, avarage, lstm, arima):
        self.arima = arima
        self.lstm = lstm
        self.avarage = avarage
        self.df = pd.read_csv(path_to_csv, sep=';', header=0, encoding='ISO-8859-1', on_bad_lines='skip')
        self.__prepareDataframe()
    
    def __prepareDataframe(self):
        # Colunas númericas
        colunas_para_converter = ['Abertura', 'Máximo', 'Mínimo', 'Fechamento', 'Volume', 'Quantidade']
        
        for coluna in colunas_para_converter:
            pd_column = self.df[coluna]
            # Garantir que a coluna é do tipo string
            pd_column = pd_column.astype(str)
            # Remover caracteres não numéricos (mantendo apenas números e pontos/vírgulas)
            pd_column = pd_column.str.replace(r'[^\d.,]', '', regex=True)
            # Substituir pontos por vírgulas se necessário (dependendo do formato dos dados)
            pd_column = pd_column.str.replace(r'\.(?=\d{3,})', '', regex=True)  # Remove pontos de milhar
            pd_column = pd_column.str.replace(',', '.', regex=True)  # Substituir vírgulas por pontos (para separadores decimais)
            # Converter para numérico
            self.df[coluna] = pd.to_numeric(pd_column, errors='coerce')
        
        self.df['Data_Hora'] = pd.to_datetime(self.df['Data'] + ' ' + self.df['Hora'], format='%d/%m/%Y %H:%M:%S', dayfirst=True)

    def analyse(self, periodos):
        self.avarage.analyse(self.df, periodos)
        self.lstm.analyse(self.df, periodos)
        self.arima.analyse(self.df, periodos)
        
    def verifyAccuracy(self):
        avarage = self.avarage.getAccuracy()
        lstm = self.lstm.getAccuracy()
        arima = self.arima.getAccuracy()
        
        print('\n----- RESULTADOS -----')
        print(f"[MÉDIA] Percentagem de acertos: {avarage:.2f}%")
        print(f"[LSTM] Percentagem de acertos: {lstm:.2f}%")
        print(f"[ARIMA] Percentagem de acertos: {arima:.2f}%")
        
        

