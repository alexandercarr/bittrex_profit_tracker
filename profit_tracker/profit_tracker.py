from bittrex import bittrex
import config
import json
from decimal import *
from time import sleep

#an instance of the bittrex api object is created in main()
api = None
#this dictionary will contain all information needed for the display
profit_data = {}
non_zero_balances = []
order_histories = {}
current_prices = {}

def main():
    global api
    api = bittrex(config.API_KEY, config.API_SECRET)
    while True:
        sleep(2)

        get_nonzero_balances()
        get_order_histories()
        get_current_prices()
    #methods to be called periodically: get_order_histories every few minutes, get_nonzero_balances every few minutes, get_ticker every few seconds

def sandbox_test():
    print("!#!#!#!#!#!#! PROFIT TRACKER MODULE TESTING #!#!#!#!#!")
    global api
    api = bittrex(config.API_KEY, config.API_SECRET)
    get_nonzero_balances()
    get_order_histories()
    get_current_prices()
    print()
    print("PROFIT DATA")
    print()
    print(profit_data)
    print()
    print("NON ZERO BALANCES")
    print(non_zero_balances)
    print()
    print("ORDER HISTORIES")
    print(order_histories)
    print()
    print("CURRENT PRICES")
    print(current_prices)
    print("!#!#!#!#!#!#! END PROFIT TRACKER MODULE TESTING #!#!#!#!#!")

def update():
    time.sleep(5)
    get_order_histories()



#gets a list of dictionaries of all non-zero balances in the user's bitcoin wallet, excluding USDT
def get_nonzero_balances():
    global non_zero_balances
    balances = api.getbalances()
    for balance in balances:
        if balance['Balance'] != 0.0 and balance['Currency'] != "USDT":
            balance['Balance'] = Decimal(balance['Balance'])
            non_zero_balances.append(balance)
    return non_zero_balances

#gets the order histories of all currencies returned from get_nonzero_balances()
def get_order_histories():
    global order_histories
    for entry in non_zero_balances:
        if entry['Currency'] != "BTC":
            currency = entry['Currency']
            order_histories[currency] = api.getorderhistory('BTC-' + currency, 100)

#helper function
def get_current_prices():
    global current_prices
    for entry in non_zero_balances:
        if entry['Currency'] == "BTC":
            market = "USDT-BTC"
        else:
            market = "BTC-" + entry['Currency']
        ticker_info = api.getticker(market)
        current_prices[entry['Currency']] = ticker_info
    #for key, val in current_prices.items():
    #    print(key)
    #    print(val)
    calculate_profits()

def calculate_profits():
    #calculate_average_purchase_price('ETH', 'BTC-ETH')
    for entry in non_zero_balances:
        if entry['Currency'] != "BTC":
            profit_data[entry['Currency']] = {}
            purchase_price = []
            profit_data[entry['Currency']]['AVG_PURCHASE_PRICE_BTC'] = calculate_average_purchase_price(entry['Currency'], "BTC-"+entry['Currency'], entry['Balance'])
            profit_data[entry['Currency']]['PROFIT_LOSS_USD'] = get_profit_losses(entry['Currency'], "BTC-"+entry['Currency'], Decimal(entry['Balance']))
            profit_data[entry['Currency']]['CURRENT_PRICE_BTC'] = get_current_price("BTC-"+entry['Currency'])
            #for order in order_histories[entry['Currency']]:
                #print(order)

def calculate_average_purchase_price(currency_name, market_name, balance):
    getcontext().prec = 28

    sell_order_types = ['LIMIT_SELL']
    buy_order_types = ['LIMIT_BUY']
    quantity_price = {}
    balance_as_of_this_order = Decimal(0)
    for order in order_histories[currency_name]:
        if balance_as_of_this_order < balance:
            if order['OrderType'] in buy_order_types:
                balance_as_of_this_order += Decimal(order['Quantity'])
            elif order['OrderType'] in sell_order_types:
                balance_as_of_this_order -= Decimal(order['Quantity'])
        quantity_price[order['TimeStamp']] = []
        quantity_price[order['TimeStamp']].append(Decimal(order['Quantity']))
        quantity_price[order['TimeStamp']].append(Decimal((order['PricePerUnit'])))
    weighted_avg_purchase_price = Decimal(0)

    for key, entry in quantity_price.items():
        weight = Decimal(entry[0]) / Decimal(balance)
        weighted_avg_purchase_price += (weight * Decimal(entry[1]))
    return weighted_avg_purchase_price

def get_current_bitcoin_price():
    return Decimal(api.getticker("USDT-BTC")['Last'])

def bitcoin_to_usd_current(btc_amount):
    return btc_amount * get_current_bitcoin_price()
    #bitcoin_price =

def get_current_price(market_name):
    data = api.getticker(market_name)
    current_price = Decimal(data['Last'])
    return current_price

def get_profit_losses(currency_name, market_name, balance):
    bitcoin_price = get_current_bitcoin_price()
    avg_purchase_price = profit_data[currency_name]['AVG_PURCHASE_PRICE_BTC']
    current_price = get_current_price(market_name)
    profit_per_coin_btc = Decimal(avg_purchase_price) - current_price
    total_btc_profit = profit_per_coin_btc * balance
    profit_total = bitcoin_to_usd_current(total_btc_profit)
    return profit_total