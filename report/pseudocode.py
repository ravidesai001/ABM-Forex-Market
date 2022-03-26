# bank cda trading algorithm
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