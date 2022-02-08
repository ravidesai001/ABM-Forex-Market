from locale import currency
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from CDA import CDA, Order

class BankAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, exchange_rate):
        super().__init__(unique_id, model)
        # try to maintain this initial ratio of euros and dollars as risk mitigation strategy
        self.EUR = 1000000000 # 1 billion
        self.USD = self.EUR * exchange_rate
        self.prevEUR = 0
        self.prevUSD = 0
        # exchange rate is always as EURUSD
        self.exchange_rate = exchange_rate # perhaps init this as 1 then let model reach equilibrium
        self.threshold = 800000000

    def trade(self):
        other = self.random.choice(self.model.schedule.agents)
        sell_currency = self.random.choice(["EUR", "USD"])
        if sell_currency == "EUR":
            euros = self.random.normalvariate(self.EUR/2, self.EUR * 0.05)
            dollars = self.random.normalvariate(other.USD/2, other.USD * 0.05)
            other.EUR += euros
            self.EUR -= euros
            self.USD += dollars
            other.USD -= dollars
        else:
            dollars = self.random.normalvariate(self.USD/2, self.USD * 0.05)
            euros = self.random.normalvariate(other.EUR/2, other.EUR * 0.05)
            other.USD += dollars
            self.USD -= dollars
            self.EUR += euros
            other.EUR -= euros
            self.prevEUR = euros
            self.prevUSD = dollars
    
    # offload risk and unload positions within interbank cda
    def cda_trade(self):
        self.exchange_rate = self.random.gauss(self.exchange_rate, 0.05)
        if self.EUR > self.threshold:
            sellEuroOrder = Order(self.unique_id, True, int(self.EUR - self.threshold), self.exchange_rate, 0)
            self.model.CDA.AddOrder(sellEuroOrder)
        if self.USD > self.threshold * self.exchange_rate:
            sellUsdOrder = Order(self.unique_id, True, int(self.USD - self.threshold * self.exchange_rate), self.exchange_rate, 1)
            self.model.CDA.AddOrder(sellUsdOrder)
        if self.EUR < self.threshold:
            buyEuroOrder = Order(self.unique_id, False, int(self.threshold - self.EUR), self.exchange_rate, 0)
            self.model.CDA.AddOrder(buyEuroOrder)
        if self.USD < self.threshold * self.exchange_rate:
            buyUsdOrder = Order(self.unique_id, False, int(self.threshold * self.exchange_rate - self.USD), self.exchange_rate, 1)
            self.model.CDA.AddOrder(buyUsdOrder)
        # Matched orders
        self.model.CDA.MatchOrders()
        # print(self.model.CDA.Matches)
        for match in self.model.CDA.Matches:
            if match.Bid.CreatorID == self.unique_id:
                if match.Bid.currency == 0: # euros
                    price = self.model.CDA.ComputeClearingPrice()
                    self.EUR += match.Offer.Quantity # buying euros from counterparty
                    self.USD -= int(match.Offer.Quantity * price) # exchanging dollars for counterparty's euros
                    print(str(price) + " euros: "+ str(self.EUR) + " dollars: " + str(self.USD))
                    for agent in self.model.schedule.agents:
                        if agent.unique_id == match.Offer.CreatorID:
                            agent.EUR -= match.Offer.Quantity
                            agent.USD += int(match.Offer.Quantity * price)
                elif match.Bid.currency == 1: # dollars
                    # maybe set clearing price as new exchange rate to see how that works
                    price = self.model.CDA.ComputeClearingPrice()
                    self.EUR -= int(match.Offer.Quantity * (1 / price)) # selling euros to counterparty
                    self.USD += match.Offer.Quantity # getting back dollars from counterparty
                    print(str(price) + " euros: "+ str(self.EUR) + " dollars: " + str(self.USD))
                    for agent in self.model.schedule.agents:
                        if agent.unique_id == match.Offer.CreatorID:
                            agent.EUR += int(match.Offer.Quantity * (1 / price))
                            agent.USD -= match.Offer.Quantity
        
    
    def step(self):
        self.cda_trade()
        # self.trade()

class Trader(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, bank):
        super().__init__(unique_id, model)
        self.bank = bank
        self.EUR = 100
        self.USD = self.EUR * self.bank.exchange_rate
        self.prevEUR = 0
        self.prevUSD = 0

    def trade(self):
        other = self.random.choice(self.model.schedule.agents)
        sell_currency = self.random.choice(["EUR", "USD"])
        if sell_currency == "EUR":
            euros = self.random.normalvariate(self.EUR/2, self.EUR * 0.05)
            dollars = self.random.normalvariate(other.USD/2, other.USD * 0.05)
            other.EUR += euros
            self.EUR -= euros
            self.USD += dollars
            other.USD -= dollars
        else:
            dollars = self.random.normalvariate(self.USD/2, self.USD * 0.05)
            euros = self.random.normalvariate(other.EUR/2, other.EUR * 0.05)
            other.USD += dollars
            self.USD -= dollars
            self.EUR += euros
            other.EUR -= euros
            self.prevEUR = euros
            self.prevUSD = dollars

    def step(self):
        self.trade()
    


class MoneyModel(Model):
    """A model with some number of agents."""
    def __init__(self, NumBanks, NumTraders):
        self.num_banks = NumBanks
        self.num_traders = NumTraders
        self.schedule = RandomActivation(self)
        self.running = True
        self.CDA = CDA("CDA", self)

        # Create agents
        for i in range(self.num_banks):
            exchange_rate = self.random.normalvariate(1.14, 0.05)
            bank = BankAgent("bank" + str(i), self, exchange_rate)
            self.schedule.add(bank)
            # buy and sell agents should belong to the bank
            for i in range(self.num_traders):
                trader = Trader("trader" + str(i) + bank.unique_id, self, bank)
                self.schedule.add(trader)

        self.datacollector = DataCollector(
            model_reporters={"EURUSD": average_rate},
            agent_reporters={"Euros": "EUR", "Dollars": "USD"})

    def step(self):
        # self.CDA.MatchOrders()
        self.datacollector.collect(self)
        self.schedule.step()

def average_rate(model):
    rates = []
    for agent in model.schedule.agents:
        if agent.unique_id.startswith("bank"):
            rates.append(agent.exchange_rate)
    if len(rates) != 0:
        return sum(rates)/len(rates)
    return 0

def currency_ratio(model):
    rates = []
    for agent in model.schedule.agents:
        if agent.unique_id != "CDA" and agent.prevEUR != 0:
            rates.append(agent.prevUSD/float(agent.prevEUR))

    if len(rates) != 0:
        return sum(rates)/len(rates)/100
    return 0
