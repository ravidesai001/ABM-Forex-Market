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
        self.Bids: List[Order] = []
        self.Offers: List[Order] = []
        self.Matches: List[Match] = []

    def AddOrder(self, order: Order):
        if order.Side:
            self.Offers.append(order)
        else:
            self.Bids.append(order)

    # match opposing currencies 
    def MatchOrders(self):
        self.Bids = sorted(self.Bids, key=lambda x: x.Price)[::-1]
        self.Offers = sorted(self.Offers, key=lambda x: x.Price)

        while (len(self.Bids) > 0 and len(self.Offers) > 0):
            if self.Bids[0].Price < self.Offers[0].Price:
                break
            else:
                currBid = self.Bids.pop()
                currOffer = self.Offers.pop()
                if currBid.Quantity != currOffer.Quantity:
                    if currBid.Quantity > currOffer.Quantity:
                        newBid = Order(currBid.CreatorID, currBid.Side, currBid.Quantity - currOffer.Quantity, currBid.Price, currBid.currency)
                        self.Bids.insert(0, newBid)
                        currBid.Quantity = currOffer.Quantity
                    else:
                        newOffer = Order(currOffer.CreatorID, currOffer.Side, currOffer.Quantity - currBid.Quantity, currOffer.Price, currOffer.currency)
                        self.Offers.insert(0, newOffer)
                        currOffer.Quantity = currBid.Quantity
                if currBid.currency == currOffer.currency:
                    if currBid.CreatorID != currOffer.CreatorID:
                        self.Matches.append(Match(currBid, currOffer))
    
    def ClearOrderBook(self):
        self.Bids.clear()
        self.Offers.clear()
        self.Matches.clear()
    
    def ComputeEfficiency(self) -> Double:
        if (len(self.Bids) > 0 or len(self.Offers) > 0) and len(self.Matches) > 0:
            total_bid_quantity = sum([bid.Quantity for bid in self.Bids])
            total_offer_quantity = sum([offer.Quantity for offer in self.Offers])
            total_match_quantity = sum([match.Bid.Quantity for match in self.Matches])
            return total_match_quantity / (total_bid_quantity + total_offer_quantity)
        else:
            return 0

    def ComputeClearingPrice(self) -> Double:
        if len(self.Matches) == 0:   
            return 0   
        
        clearingPrice = 0   
        cumulativeQuantity = 0
        for match in self.Matches:
            cumulativeQuantity += match.Bid.Quantity
            clearingPrice += match.Bid.Quantity * (match.Bid.Price + match.Offer.Price) / 2
        
        return clearingPrice / cumulativeQuantity

