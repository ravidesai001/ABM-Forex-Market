from tokenize import Double
from typing import List
from dataclasses import dataclass

@dataclass
class Order(object):   
    CreatorID: int   
    Side: bool # true = offer, false = bid
    Quantity: int   
    Price: int
    currency: int # 0 = euros, 1 = dollars

@dataclass  
class Match(object):   
    Bid: Order   
    Offer: Order

class CDA:
    def __init__(self):
        self.bids: List[Order] = []
        self.offers: List[Order] = []
        self.matches: List[Match] = []

    def add_order(self, order: Order):
        if order.Side:
            self.offers.append(order)
        else:
            self.bids.append(order)

    # match opposing currencies 
    def match_orders(self):
        self.bids = sorted(self.bids, key=lambda x: x.Price)[::-1]
        self.offers = sorted(self.offers, key=lambda x: x.Price)

        while (len(self.bids) > 0 and len(self.offers) > 0):
            if self.bids[0].Price < self.offers[0].Price:
                break
            curr_bid = self.bids.pop()
            curr_offer = self.offers.pop()
            if curr_bid.Quantity > curr_offer.Quantity:
                new_bid = Order(curr_bid.CreatorID, curr_bid.Side, curr_bid.Quantity - curr_offer.Quantity, curr_bid.Price, curr_bid.currency)
                self.bids.insert(0, new_bid)
                curr_bid.Quantity = curr_offer.Quantity
            if curr_bid.Quantity < curr_offer.Quantity:
                new_offer = Order(curr_offer.CreatorID, curr_offer.Side, curr_offer.Quantity - curr_bid.Quantity, curr_offer.Price, curr_offer.currency)
                self.offers.insert(0, new_offer)
                curr_offer.Quantity = curr_bid.Quantity
            if curr_bid.currency == curr_offer.currency:
                if curr_bid.CreatorID != curr_offer.CreatorID:
                    self.matches.append(Match(curr_bid, curr_offer))

    def compute_clearing_price(self) -> Double:
        if len(self.matches) == 0:   
            return 0   
        
        clearing_price = 0   
        cumulative_quantity = 0
        for match in self.matches:
            cumulative_quantity += match.Bid.Quantity
            clearing_price += match.Bid.Quantity * (match.Bid.Price + match.Offer.Price) / 2
        
        return clearing_price / cumulative_quantity

