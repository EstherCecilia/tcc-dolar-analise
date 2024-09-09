Previsão do Comportamento do Dólar utilizando Séries Temporais e Análise Preditiva
Introdução
Este repositório contém o código e os recursos utilizados no TCC que investiga a previsão do comportamento do dólar no mercado financeiro. O objetivo do trabalho é avaliar a eficácia de diferentes técnicas de séries temporais e análise preditiva, como médias móveis simples, médias móveis exponenciais, VWAP, ARIMA, e redes neurais LSTM (Long Short-Term Memory), na previsão das tendências de compra e venda do dólar.

Estrutura do Projeto
data/: Contém os arquivos CSV com os dados históricos de preços do dólar.
notebooks/: Jupyter notebooks utilizados para a análise e desenvolvimento dos modelos.
scripts/: Scripts Python para a execução dos modelos e geração de resultados.
models/: Modelos treinados e resultados gerados pela análise.
README.md: Documentação do projeto.
Requisitos
Python 3.8+
Pipenv ou virtualenv (recomendado para gerenciamento de ambiente virtual)
Dependências listadas em Pipfile ou requirements.txt
Configuração do Ambiente Virtual
Usando Pipenv
Instale o Pipenv (caso ainda não tenha instalado):

bash
pip install pipenv
Clone o repositório:

bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
Crie o ambiente virtual e instale as dependências:

bash
pipenv install
Ative o ambiente virtual:

bash
pipenv shell
Usando virtualenv
Instale o virtualenv (caso ainda não tenha instalado):

bash
pip install virtualenv
Clone o repositório:

bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
Crie o ambiente virtual:

bash
virtualenv venv
Ative o ambiente virtual:

No Windows:
bash
venv\Scripts\activate
No macOS/Linux:
bash
source venv/bin/activate
Instale as dependências:

bash
pip install -r requirements.txt
Execução
Após configurar o ambiente virtual, você pode executar os notebooks ou scripts diretamente. Para executar um notebook:

bash
jupyter notebook notebooks/analise.ipynb
Para executar um script Python:

bash
python scripts/nome_do_script.py
