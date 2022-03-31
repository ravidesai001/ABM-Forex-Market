# bank cda trading algorithm
from telnetlib import theNULL
from timeit import repeat
from turtle import end_fill


if r < 0.5 then
    euro_sale_order = {quantity = random_euros, price = Bid}
    dollar_sale_order = {quantity = random_dollars, price = Bid}
    model_cda.send_order(euro_sale_order, dollar_sale_order)
else
    euro_buy_order = {quantity = random_euros, price = Offer}
    dollar_buy_order = {quantity = random_dollars, price = Offer}
    model_cda.send_order(euro_buy_order, dollar_buy_order)
end

matched_orders = model_cda.match_orders()
clearing_price = model_cda.compute_clearing_price()

for each match m element of matched_orders do
    exchange currency quantity in m at clearing_price


# trading agent trading algorithm
if r < 0.5 then
    buy random number of euros from another trader at bank.Bid
    buy random number of dollars from another trader at bank.Bid
else
    sell random number of euros to another trader at bank.Offer
    sell random number of dollars to another trader at bank.Offer
end

# CDA order matching algorithm

bids = bids sorted by price descending
offers = offers sorted by price ascending
matches = empty set

repeat
    if bids[0].price < offers[0].price then
        break
    end

    current_bid = bids.pop()
    current_offer = offers.pop()
    if current_bid.quantity > current_offer.quantity then
        new_bid_order = {quantity = current_bid.quantity - current_offer.quantity, price = current_bid_price, currency = current_bid.currency}
        bids.insert_at_front(new_bid_order)
    end

    if current_bid.quantity < current_offer.quantity then
        new_offer_order = {quantity = current_offer.quantity - current_bid.quantity, price = current_offer_price, currency = current_offer.currency}
        offers.insert_at_front(new_offer_order)
    end

    if current_bid.currency == current_offer.currency then
        matches.add((current_bid, current_offer))
    end

until bids is empty and offers is empty

# CDA clearing price computation

if matches is empty then
    return 0

clearing_price = 0
cumulative_quantity = 0
for each match m element of matches do
    cumulative_quantity = cumulative_quantity + m.bid.quantity
    clearing price = clearing_price + m.bid.quantity * (m.bid.price + m.offer.price) / 2

return clearing_price / cumulative_quantity
