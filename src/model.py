from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

class BankAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, exchange_rate):
        super().__init__(unique_id, model)
        self.EUR = 100
        self.USD = self.EUR * exchange_rate
        self.prevEUR = 0
        self.prevUSD = 0
        self.exchange_rate = exchange_rate

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

class BuyAgent(Agent):
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

class SellAgent(Agent):
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
    def __init__(self, NumBanks, NumBuyers, NumSellers):
        self.num_banks = NumBanks
        self.num_buyers = NumBuyers
        self.num_sellers = NumSellers
        self.schedule = RandomActivation(self)
        self.running = True

        # Create agents
        for i in range(self.num_banks):
            exchange_rate = self.random.normalvariate(1.5, 0.1)
            bank = BankAgent("bank" + str(i), self, exchange_rate)
            self.schedule.add(bank)
            # buy and sell agents should belong to the bank
            for i in range(self.num_buyers):
                buyer = BuyAgent(bank.unique_id + "buyer" + str(i), self, bank)
                self.schedule.add(buyer)

            for i in range(self.num_sellers):
                seller = SellAgent(bank.unique_id + "seller" + str(i), self, bank)
                self.schedule.add(seller)

        self.datacollector = DataCollector(
            model_reporters={"EURUSD": currency_ratio},
            agent_reporters={"Euros": "EUR", "Dollars": "USD"})

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def currency_ratio(model):
    rates = []
    for agent in model.schedule.agents:
        if agent.prevEUR != 0:
            rates.append(agent.prevUSD/float(agent.prevEUR))

    if len(rates) != 0:
        return sum(rates)/len(rates)/100
    return 0
