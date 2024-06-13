import yfinance as yf
import pandas as _pd
import numpy as np
import enum 
import matplotlib.pyplot as plt

class Decisions(enum.Enum):
    sell = -1
    hold = 0
    buy = 1
    

class Portfolio:
    def __init__(self, capital, shares): 

        self.capital = capital
        self.shares = shares
        self.portfolio_value = self.capital + self.shares*price


    def Decide(self, f1, f2, f3, f4):   
        prob_profit = 0.1
        expected_return = 1.1
        modifier = 0.5

        position = self.OptimalPosition(expected_return, prob_profit, modifier)
        shares = abs(int(position/price))
        
        if position > 0:
            self.Order(Decisions.buy, shares)
        else:
            self.Order(Decisions.sell, shares)

    def Order(self, decision, n = -1):
        counter = 0

        # buy n shares
        if decision == Decisions.buy:
            counter = 0  
            while self.capital >= price:
                self.capital -= price
                self.shares += 1
                counter += 1
                if counter == n:
                    break
            
        # sell n shares
        elif decision == Decisions.sell:
            counter = 0  
            while self.shares > 0:
                self.capital += price
                self.shares -= 1
                counter += 1
                if counter == n:
                    break

        # plot a dot for buy or sell points
        if counter > 0:
            if decision.value > 0:
                plt.plot([i], [price], marker='o', markersize=4, color="limegreen")
            elif decision.value < 0:
                plt.plot([i], [price], marker='o', markersize=4, color="red")
    
    def OptimalPosition(self, expected_return, prob_win, modifier):
        prob_lose = 1 - prob_win
        fraction = ((expected_return * prob_win) - prob_lose) / expected_return
        optimal_position = (self.capital * fraction) * modifier

        return optimal_position

    def PortfolioValue(self):
        self.portfolio_value = self.capital + (self.shares*price)
        return self.portfolio_value


    


class MovingAverage:
    def __init__(self):
        self.averages = []
        self.percent_difference = 0
        self.slope = 0
        self.slope_sum = 0
        self.avg_slope = 0
        self.slopes = []
        self.concavity = 0 
        self.concavity_sum = 0
        self.avg_concavity = 0
        self.concavities = []
        self.above = False
        self.flipped = False
        self.edge =  0


    def CalculateAverage(self, value_list, window):
        # account for the beginning of the dataset
        if i < (window - 1):
            self.edge = window - (i + 1)
        else: self.edge = 0
        
        # calculate the average value over the interval
        if i == 0:
            value_sum = price
        else:
            value_sum = 0
            for n in range(window - self.edge):
                value_sum += value_list[i - n]
            
        return value_sum/(window - self.edge)
    


    def Update(self, window):
        # percent deviation from the mean
        difference = price - self.averages[i]
        self.percent_difference = difference/self.averages[i]

        # calculate slope
        if i > 1:
            self.slope = self.averages[i] - self.averages[i - 1]

        # calculate average slope and concavity
        self.slopes.append(self.slope)
        self.slope_sum += abs(self.slope)
        if i < window:
            self.avg_slope = self.slope_sum/(i+1)
            self.concavity = self.slopes[i] - self.slopes[0]
        else:
            self.slope_sum -= abs(self.slopes[0])
            self.slopes.pop(0)
            self.avg_slope = self.slope_sum/window
            self.concavity = self.slopes[window - 1] - self.slopes[0]

        # calculate average concavity
        self.concavities.append(self.concavity)
        self.concavity_sum += self.concavity
        if i < window:
            self.avg_concavity = self.concavity_sum/(i+1)

        else:
            self.concavity_sum -= self.concavities[0]
            self.concavities.pop(0)
            self.avg_concavity = self.concavity_sum/window


        # check if we flip over average line
        if price > self.averages[i]:
            if self.above == False: 
                self.above = True
                self.flipped = True
            else: self.flipped = False
        else:
            if self.above:
                self.above = False
                self.flipped = True
            else: self.flipped = False



while True:

    # input a ticker to track
    ticker = input("Enter ticker: ")
    if ticker == 'exit':
        break

    # get ticker information and price history
    ticker_info = yf.Ticker(ticker)
    price_history = ticker_info.history(start="2015-01-01",  end="2020-12-20")

    # assign lists for the open/close prices, the moving-average values, 
    # and the daily average prices.
    opens = price_history['Open']
    closes = price_history['Close']
    prices = []

    # calculates the inital price of the stock, and 
    # the number of days we are looking back in history
    price = closes[0]
    days = opens.size

    # initialize the portfolio and moving average objects
    starting_capital = 0
    starting_shares = 100
    entry_price = starting_shares * price
    portfolio = Portfolio(starting_capital, starting_shares)

    # objects to track moving averages
    f1 = MovingAverage()
    f2 = MovingAverage()
    f3 = MovingAverage()
    f4 = MovingAverage()

    max_slope = 0

    # iterate over the history of the stock
    for i in range(days):
        
        # create a list of the closing prices
        price = closes[i]
        prices.append(price)
        
        f1_window = 10
        f2_window = 50
        f3_window = 100
        f4_window = 200
        
        # calculate the moving averages
        f1.averages.append(f1.CalculateAverage(prices, f1_window))
        f2.averages.append(f2.CalculateAverage(prices, f2_window))
        f3.averages.append(f3.CalculateAverage(prices, f3_window))
        f4.averages.append(f4.CalculateAverage(prices, f4_window))
        
        # update the functions
        f1.Update(f1_window)
        f2.Update(f2_window)
        f3.Update(f3_window)
        f4.Update(f4_window)

        # decide if we buy, sell, or hold
        portfolio.Decide(f1, f2, f3, f4)
    

    control_value = starting_capital + (prices[days - 1] * starting_shares)
    algo_value = portfolio.PortfolioValue()

    print(" ")
    print("Capital: {}".format(portfolio.capital))
    print("Shares: {}".format(portfolio.shares))
    print("Buy and Hold portfolio value: {}".format(control_value))
    print("Returns: {}".format(control_value - entry_price))
    print("Algorithm portfolio value:  {}".format(algo_value))
    print("Returns: {}".format(algo_value - entry_price))
    print(" ")

    # plot the price history and moving average history
    plot1 = plt.figure(1)
    x = list(range(0, days))
    plt.plot(x, prices)
    plt.title(ticker)
    plt.xlabel("Days")
    plt.ylabel("Price")
    
    plt.plot(x, f1.averages)
    plt.plot(x, f2.averages)
    plt.plot(x, f3.averages)
    plt.plot(x, f4.averages)

    plt.show()
