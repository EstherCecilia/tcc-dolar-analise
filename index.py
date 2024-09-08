from analyser import Analyser
from main.avarage import Average
from main.arima import Arima
from main.lstm import Lstm

QUANTITY_OF_LINES_TO_ANALYSE = 300

analyser = Analyser(
    'ABEV3_B_0_1min.csv',
    Average(QUANTITY_OF_LINES_TO_ANALYSE),
    Arima(QUANTITY_OF_LINES_TO_ANALYSE),
    Lstm(QUANTITY_OF_LINES_TO_ANALYSE)
)
analyser.analyse([5])
analyser.verifyAccuracy()