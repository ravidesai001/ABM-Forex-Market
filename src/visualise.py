from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

from model import *

rate_chart = ChartModule([{"Label": "Bid",
                      "Color": "Black"},
                      {"Label": "Offer",
                      "Color": "Red"}],
                    data_collector_name='datacollector')
                

spread_chart = ChartModule([{"Label": "Spread", "Color": "Red"}], 
                    data_collector_name='datacollector')

server = ModularServer(MoneyModel,
                       [rate_chart, spread_chart],
                       "Money Model",
                       {"NumBanks":5, "NumTraders": 100})

server.port = 8521 # The default
server.launch()