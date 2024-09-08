import sys
import time

class Logger:
    def __init__(self):
        self.terminal = sys.stdout  # Guarda o stdout original (console)
        self.log = open('./logs/' + str(time.time_ns()) + "_logs", "a")  # Abre o arquivo de log no modo apêndice

    def write(self, message):
        self.terminal.write(message)  # Escreve no console
        self.log.write(message)       # Escreve no arquivo

    def flush(self):
        self.terminal.flush()  # Para forçar a escrita no console
        self.log.flush()       # Para garantir que o conteúdo seja gravado no arquivo


