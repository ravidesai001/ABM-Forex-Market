from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from CDA import CDA, Order
from data import DataReader
from numpy import loadtxt
import random

class BankAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # try to maintain this initial ratio of euros and dollars as risk mitigation strategy
        self.EUR = 10000000000 # 1 billion
        self.USD = 10000000000
        # exchange rate is always as EURUSD
        self.bid = self.model.data.iat[0, 0]
        self.offer = self.model.data.iat[0, 1]
        self.threshold = random.normalvariate(800000000, 100000000) # mu = 800 million, sigma = 100 million
        self.rate_offset = random.normalvariate(0.0001, 0.00002)
    
    # offload risk and unload positions within interbank cda
    # instead of threshold trading, trade on the bid ask spread explicitly
    def cda_threshold_trade(self):
        if self.EUR > self.threshold:
            sellEuroOrder = Order(self.unique_id, True, int(self.EUR - self.threshold), self.offer, 0)
            self.model.CDA.AddOrder(sellEuroOrder)
        elif self.USD > self.threshold:
            sellUsdOrder = Order(self.unique_id, True, int(self.USD - self.threshold), self.offer, 1)
            self.model.CDA.AddOrder(sellUsdOrder)
        elif self.EUR < self.threshold:
            buyEuroOrder = Order(self.unique_id, False, int(self.threshold - self.EUR), self.bid, 0)
            self.model.CDA.AddOrder(buyEuroOrder)
        elif self.USD < self.threshold:
            buyUsdOrder = Order(self.unique_id, False, int(self.threshold- self.USD), self.bid, 1)
            self.model.CDA.AddOrder(buyUsdOrder)
        # Matched orders
        self.model.CDA.MatchOrders()
        # print(len(self.model.CDA.Matches))
        for match in self.model.CDA.Matches:
            if match.Bid.CreatorID == self.unique_id:
                self.model.num_trades += 1
                if match.Bid.currency == 0: # euros
                    price = self.model.CDA.ComputeClearingPrice()
                    self.EUR += match.Offer.Quantity # buying euros from counterparty
                    self.USD -= int(match.Offer.Quantity * price) # exchanging dollars for counterparty's euros
                    self.model.usd_volume += abs(int(match.Offer.Quantity * price))
                    self.model.eur_volume += abs(match.Offer.Quantity)
                    # print(str(price) + " euros: "+ str(self.EUR) + " dollars: " + str(self.USD))
                    for agent in self.model.schedule.agents:
                        if agent.unique_id == match.Offer.CreatorID:
                            agent.EUR -= match.Offer.Quantity
                            agent.USD += int(match.Offer.Quantity * price)
                elif match.Bid.currency == 1: # dollars
                    # maybe set clearing price as new exchange rate to see how that works
                    price = self.model.CDA.ComputeClearingPrice()
                    self.EUR -= int(match.Offer.Quantity * (1 / price)) # selling euros to counterparty
                    self.USD += match.Offer.Quantity # getting back dollars from counterparty
                    self.model.usd_volume += abs(match.Offer.Quantity)
                    self.model.eur_volume += abs(int(match.Offer.Quantity * (1 / price)))
                    # print(str(price) + " euros: "+ str(self.EUR) + " dollars: " + str(self.USD))
                    for agent in self.model.schedule.agents:
                        if agent.unique_id == match.Offer.CreatorID:
                            agent.EUR += int(match.Offer.Quantity * (1 / price))
                            agent.USD -= match.Offer.Quantity

    def cda_reactive_trade(self):
        spread_in_pips = abs(self.bid - self.offer) / 0.0001
        probability = self.model.get_trade_probability(spread_in_pips)
        if random.random() < probability:
            self.cda_threshold_trade()
        # need to construct a spread to probability of trade execution table along with probability weighting the volume to trade
        # construct continuous probability distribution by dividing each spread data point by the maximum spread
    
    def step(self):
        self.bid, self.offer = self.model.data.iat[self.model.current_step, 0] + self.rate_offset, self.model.data.iat[self.model.current_step, 1] + self.rate_offset
        # add randomised margin for each bank at this stage
        # self.cda_threshold_trade()
        self.cda_reactive_trade()
        self.threshold = random.normalvariate(800000000, 100000000) # mu = 800 million, sigma = 100 million
        # print(self.threshold)

class Trader(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, bank):
        super().__init__(unique_id, model)
        self.bank = bank
        self.EUR = 100000000 # 100 million
        self.USD = 100000000

    def trade(self):
        self.model.num_trades += 1
        rnd = random.random()
        other = self.model.traders[round(rnd * (len(self.model.traders) - 1))]
        if rnd < 0.5: # sell eur
            euros = random.normalvariate(self.EUR/2, self.EUR * 0.05)
            dollars = euros * self.bank.offer
            other.EUR += euros
            self.EUR -= euros
            self.USD += dollars
            other.USD -= dollars
            self.model.usd_volume += abs(dollars)
            self.model.eur_volume += abs(euros)
        else: # sell usd
            dollars = random.normalvariate(self.USD/2, self.USD * 0.05)
            euros = dollars * (1 / self.bank.offer)
            other.USD += dollars
            self.USD -= dollars
            self.EUR += euros
            other.EUR -= euros
            self.model.usd_volume += abs(dollars)
            self.model.eur_volume += abs(euros)

    def step(self):
        spread_in_pips = abs(self.bank.bid - self.bank.offer) / 0.0001
        probability = self.model.get_trade_probability(spread_in_pips)
        if random.random() * 2 < probability:
            self.trade()
    


class FXModel(Model):
    """FX model with agents modelling market activity"""
    def __init__(self, NumBanks, NumTraders):
        self.num_banks = NumBanks
        self.num_traders = NumTraders
        self.schedule = RandomActivation(self)
        self.running = True
        self.CDA = CDA("CDA", self)
        self.data = DataReader("./data/year_2021_tick_data.csv").get_hour_data()
        self.max_steps = len(self.data.index) # number of data rows = max number of model steps
        self.num_trades = 0
        self.current_step = 0
        self.trades = [0]
        self.eur_volume = 0
        self.usd_volume = 0
        self.usd_volumes = [0]
        self.eur_volumes = [0]
        self.params = loadtxt("./data/model_params.txt", delimiter=",", dtype=(float, float))

        # Create agents
        for i in range(self.num_banks):
            bank = BankAgent("bank" + str(i), self)
            self.schedule.add(bank)
            # buy and sell agents should belong to the bank
            for i in range(self.num_traders):
                trader = Trader("trader" + str(i) + bank.unique_id, self, bank)
                self.schedule.add(trader)
        self.datacollector = DataCollector(
            model_reporters={"Bid": average_bid, "Offer": average_offer, "Spread": average_spread, "Trades": num_trades, "USD Volume": usd_volume, "EUR Volume": eur_volume}
        )

        self.traders = [agent for agent in self.schedule.agents if agent.unique_id.startswith("trader")]
    
    def get_trade_probability(self, x):
        # example from trained spread dataset-> y = 1 - 0.03125x
        # gives probability of trading based on current spread in pips x
        # h(x) = {1 - 0.03125x, if 0 <= x <= 32;
        #         1, if x < 0;
        #         0, if x > 32}
        p = float(self.params[0]) * x + float(self.params[1])
        if p > 1:
            return 1
        elif p < 0:
            return 0
        else:
            return p

    def step(self):
        self.datacollector.collect(self)
        self.trades.append(self.num_trades)
        # print(self.eur_volumes)
        self.eur_volumes.append(self.eur_volume)
        self.usd_volumes.append(self.usd_volume)
        # print(self.trades)
        self.current_step += 1
        self.schedule.step()
        # print(self.trades)

def eur_volume(model):
    return model.eur_volumes[-1] - model.eur_volumes[-2] if len(model.eur_volumes) > 1 else model.eur_volumes[-1]
    
def usd_volume(model):
    return model.usd_volumes[-1] - model.usd_volumes[-2] if len(model.usd_volumes) > 1 else model.usd_volumes[-1]

def num_trades(model):
    return model.trades[-1] - model.trades[-2] if len(model.trades) > 1 else model.trades[-1]

def average_bid(model):
    rates = []
    for agent in model.schedule.agents:
        if agent.unique_id.startswith("bank"):
            rates.append(agent.bid)
    if len(rates) != 0:
        return sum(rates)/len(rates)
    return model.data.iat[0,0]

def average_offer(model):
    rates = []
    for agent in model.schedule.agents:
        if agent.unique_id.startswith("bank"):
            rates.append(agent.offer)
    if len(rates) != 0:
        return sum(rates)/len(rates)
    return model.data.iat[0,1]

# spread in pips
def average_spread(model):
    spreads = []
    for agent in model.schedule.agents:
        if agent.unique_id.startswith("bank"):
            spreads.append(abs(agent.offer - agent.bid))
    if len(spreads) != 0:
        return (sum(spreads)/len(spreads))/0.0001
    return abs(model.data.iat[0,1] - model.data.iat[0,0])/0.0001

