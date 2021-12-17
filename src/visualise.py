from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

from model import *

chart = ChartModule([{"Label": "EURUSD",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

server = ModularServer(MoneyModel,
                       [chart],
                       "Money Model",
                       {"NumBanks":5, "NumBuyers":100, "NumSellers":100})

server.port = 8521 # The default
server.launch()