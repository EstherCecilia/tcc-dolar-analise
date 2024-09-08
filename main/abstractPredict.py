from abc import ABC

class AbstractPredict(ABC):
    def analyse(self, df, periodos):
        print(f"Iniciando análise para {self.__class__.__name__}")

        for periodo in periodos:
            print(f"[{self.__class__.__name__}] Analisando dados para período de {periodo} minutos")

            for i in range(0, self.quantity_of_lines_to_analyse, periodo):
                df_periodo = df.iloc[i:i+periodo]
                decisao = self._analyse_decision(df_periodo)
                preco_atual = df['Fechamento'].iloc[i+periodo-1]
                proximo_preco = df['Fechamento'].iloc[i+periodo]

                if decisao == 'Compra' and proximo_preco > preco_atual:
                    acerto = 'Sim'
                elif decisao == 'Venda' and proximo_preco < preco_atual:
                    acerto = 'Sim'
                elif decisao == 'Manter' and abs(proximo_preco - preco_atual) < 0.01:
                    acerto = 'Sim'
                else:
                    acerto = 'Não'

                self.results.append({
                    'Data_Hora': df['Data_Hora'].iloc[i+periodo-1],
                    'Decisão': decisao,
                    'Valor_Dolar_Atual': preco_atual,
                    'Valor_Dolar_Futuro': proximo_preco,
                    'Acertou': acerto
                })
    
    def getAccuracy(self):
        filtered_df = [item for item in self.results if item.get('Acertou') == 'Sim']
        percentage = (len(filtered_df) / len(self.results)) * 100
        return percentage

    def clear_results(self):
        print("Limpando dados...")
        self.results = []