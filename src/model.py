from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from CDA import CDA, Order
from data import DataReader

class BankAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # try to maintain this initial ratio of euros and dollars as risk mitigation strategy
        self.EUR = 5000000000 # 5 billion
        self.USD = 5000000000
        # exchange rate is always as EURUSD
        self.bid = self.model.data.iat[0, 0]
        self.offer = self.model.data.iat[0, 1]
        self.threshold = self.random.normalvariate(5000000000, 500000000) # mu = 5 billion, sigma = 500 million
    
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
                    # print(str(price) + " euros: "+ str(self.EUR) + " dollars: " + str(self.USD))
                    for agent in self.model.schedule.agents:
                        if agent.unique_id == match.Offer.CreatorID:
                            agent.EUR += int(match.Offer.Quantity * (1 / price))
                            agent.USD -= match.Offer.Quantity

    def cda_reactive_trade(self):
        spread_in_pips = abs(self.bid - self.offer) / 0.0001
        pass
        # need to construct a spread to probability of trade execution table along with probability weighting the volume to trade
        # construct continuous probability distribution by dividing each spread data point by the maximum spread
    
    def step(self):
        self.bid, self.offer = self.model.data.iat[self.model.current_step, 0], self.model.data.iat[self.model.current_step, 1]
        # add randomised margin for each bank at this stage
        self.cda_threshold_trade()
        # self.cda_reactive_trade()
        self.threshold = self.random.normalvariate(5000000000, 500000000) # mu = 5 billion, sigma = 500 million
        # print(self.threshold)

class Trader(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, bank):
        super().__init__(unique_id, model)
        self.bank = bank
        self.EUR = 10000000 # 1 million
        self.USD = 10000000
        self.prevEUR = 0
        self.prevUSD = 0

    def trade(self):
        other = self.random.choice(self.model.schedule.agents)
        sell_currency = self.random.choice(["EUR", "USD", "NONE"])
        if sell_currency == "EUR":
            euros = self.random.normalvariate(self.EUR/2, self.EUR * 0.05)
            dollars = self.random.normalvariate(other.USD/2, other.USD * 0.05)
            other.EUR += euros
            self.EUR -= euros
            self.USD += dollars
            other.USD -= dollars
            self.model.num_trades += 1
        elif sell_currency == "USD":
            dollars = self.random.normalvariate(self.USD/2, self.USD * 0.05)
            euros = self.random.normalvariate(other.EUR/2, other.EUR * 0.05)
            other.USD += dollars
            self.USD -= dollars
            self.EUR += euros
            other.EUR -= euros
            self.prevEUR = euros
            self.prevUSD = dollars
            self.model.num_trades += 1

    def step(self):
        self.trade()
    


class FXModel(Model):
    """A model with some number of agents."""
    def __init__(self, NumBanks, NumTraders):
        self.num_banks = NumBanks
        self.num_traders = NumTraders
        self.schedule = RandomActivation(self)
        self.running = True
        self.CDA = CDA("CDA", self)
        self.data = DataReader("./data/december_2021_tick_data.csv").get_hour_data()
        self.max_steps = len(self.data.index) # number of data rows = max number of model steps
        self.num_trades = 0
        self.current_step = 0
        self.trades = [0]

        # Create agents
        for i in range(self.num_banks):
            bank = BankAgent("bank" + str(i), self)
            self.schedule.add(bank)
            # buy and sell agents should belong to the bank
            for i in range(self.num_traders):
                trader = Trader("trader" + str(i) + bank.unique_id, self, bank)
                self.schedule.add(trader)
        self.datacollector = DataCollector(model_reporters={"Bid": average_bid, "Offer": average_offer, "Spread": average_spread, "Trades": num_trades})

    def step(self):
        self.datacollector.collect(self)
        self.trades.append(self.num_trades)
        # print(self.trades)
        self.current_step += 1
        self.schedule.step()
        # print(self.trades)

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

