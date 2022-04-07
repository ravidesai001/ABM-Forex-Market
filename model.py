from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from CDA import CDA, Order
from data import DataReader
import random

class BankAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.EUR = 10000000000 # 10 billion
        self.USD = 10000000000
        self.bid = self.model.data.iat[0, 0] # exchange rate is always as EURUSD
        self.offer = self.model.data.iat[0, 1]
        self.rate_offset = random.normalvariate(0.0001, 0.00002)

    def cda_trade(self):
        self.model.CDA.MatchOrders()
        for match in self.model.CDA.Matches:
            if match.Bid.CreatorID == self.unique_id:
                self.model.num_trades += 1
                if match.Bid.currency == 0: # euros
                    price = self.model.CDA.ComputeClearingPrice()
                    self.EUR += match.Offer.Quantity # buying euros from counterparty
                    self.USD -= int(match.Offer.Quantity * price) # exchanging dollars for counterparty's euros
                    self.model.usd_volume += abs(int(match.Offer.Quantity * price))
                    self.model.eur_volume += abs(match.Offer.Quantity)
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
                    for agent in self.model.schedule.agents:
                        if agent.unique_id == match.Offer.CreatorID:
                            agent.EUR += int(match.Offer.Quantity * (1 / price))
                            agent.USD -= match.Offer.Quantity
                self.model.CDA.Matches.remove(match)
        
    def cda_random_trade(self):
        rnd = random.random()
        trade_portion = self.model.max_steps
        euros = random.random() * self.EUR/trade_portion
        dollars = random.random() * self.USD/trade_portion
        if rnd < 0.5:
            sellEuroOrder = Order(self.unique_id, True, int(euros), self.offer, 0)
            self.model.CDA.AddOrder(sellEuroOrder)
            sellDollarOrder = Order(self.unique_id, True, int(dollars), self.offer, 0)
            self.model.CDA.AddOrder(sellDollarOrder)
        else:
            buyEuroOrder = Order(self.unique_id, False, int(euros), self.bid, 0)
            self.model.CDA.AddOrder(buyEuroOrder)
            buyDollarOrder = Order(self.unique_id, False, int(dollars), self.bid, 0)
            self.model.CDA.AddOrder(buyDollarOrder)
 
    def cda_reactive_trade(self):
        spread_in_pips = abs(self.bid - self.offer) / 0.0001
        probability = self.model.get_trade_probability(spread_in_pips)
        if random.random() < probability:
            self.cda_random_trade()
    
    def step(self):
        self.bid = self.model.data.iat[self.model.current_step, 0] + self.rate_offset
        self.offer = self.model.data.iat[self.model.current_step, 1] + self.rate_offset
        self.cda_reactive_trade()
        self.cda_trade()
        

class Trader(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, bank):
        super().__init__(unique_id, model)
        self.bank = bank
        self.EUR = 100000000 # 100 million 
        self.USD = 100000000

    def sell_side_trade(self):
        rnd = random.random()
        trade_portion = self.model.max_steps
        other = self.model.traders[round(rnd * (len(self.model.traders) - 1))]
        euros = random.random() * self.EUR/trade_portion
        dollars = random.random() * self.USD/trade_portion
        if rnd < 0.5: # sell eur
            dollars_back = euros * self.bank.offer
            other.EUR += euros
            self.EUR -= euros
            self.USD += dollars_back
            other.USD -= dollars_back
            self.model.usd_volume += abs(dollars_back)
            self.model.eur_volume += abs(euros)
            self.model.num_trades += 1
        else: # sell usd
            euros_back = dollars * (1 / self.bank.offer)
            other.USD += dollars
            self.USD -= dollars
            self.EUR += euros_back
            other.EUR -= euros_back
            self.model.usd_volume += abs(dollars)
            self.model.eur_volume += abs(euros_back)
            self.model.num_trades += 1

    def buy_side_trade(self):
        rnd = random.random()
        trade_portion = self.model.max_steps
        other = self.model.traders[round(rnd * (len(self.model.traders) - 1))]
        euros = random.random() * self.EUR/trade_portion
        dollars = random.random() * self.USD/trade_portion
        if rnd < 0.5: # buy eur
            dollars_sent = euros * self.bank.bid
            other.EUR -= euros
            self.EUR += euros
            self.USD -= dollars_sent
            other.USD += dollars_sent
            self.model.usd_volume += abs(dollars_sent)
            self.model.eur_volume += abs(euros)
            self.model.num_trades += 1
        else: # buy usd
            euros_sent = dollars * (1 / self.bank.bid)
            other.USD -= dollars
            self.USD += dollars
            self.EUR -= euros_sent
            other.EUR += euros_sent
            self.model.usd_volume += abs(dollars)
            self.model.eur_volume += abs(euros_sent)
            self.model.num_trades += 1
    
    def random_trade(self):
        if random.random() < 0.5:
            self.buy_side_trade()
        else:
            self.sell_side_trade()

    def reactive_trade(self):
        spread_in_pips = abs(self.bank.bid - self.bank.offer) / 0.0001
        probability = self.model.get_trade_probability(spread_in_pips)
        if random.random() < probability:
            self.random_trade()

    def step(self):
        if self.EUR <= 0 and self.USD <= 0:
            self.model.schedule.remove(self)
        self.reactive_trade()


class FXModel(Model):
    """FX model with CDA mechanism"""
    def __init__(self, NumBanks, NumTraders, Linear_Model, running_data_path):
        self.num_banks = NumBanks
        self.num_traders = NumTraders
        self.schedule = RandomActivation(self)
        self.running = True
        self.CDA = CDA()
        self.data = DataReader(running_data_path).get_hour_data()
        self.max_steps = len(self.data.index) # number of data rows = max number of model steps
        self.num_trades = 0
        self.current_step = 0
        self.trades = [0]
        self.eur_volume = 0
        self.usd_volume = 0
        self.usd_volumes = [0]
        self.eur_volumes = [0]
        self.params = Linear_Model
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
        self.eur_volumes.append(self.eur_volume)
        self.usd_volumes.append(self.usd_volume)
        self.current_step += 1
        self.schedule.step()

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
