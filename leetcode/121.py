
def calc_sell(prices):
    if not prices:
        return 0
    
    buy = prices[0]
    profit = 0
    
    for price in prices:
        if price < buy:
            buy = price
        elif price - buy > profit:
            profit = price - buy
    
    return profit

prices = [4,2,3,4,10,3]
print(calc_sell(prices))