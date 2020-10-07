from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.common import TickerId, OrderId
from ibapi.tag_value import TagValue
import requests
import sqlite3
import threading
import os
import ibapi
import time

# desktop/stock_market_bot-master

global clientId
clientId = 1

# Покупак -- при отрицательном количестве, иначе продажа
# --- Market Sell 100% Order ---
baseOrder = Order()
baseOrder.orderType = 'MKT'
baseOrder.quantity = 0
baseOrder.faGroup = 'IPO'
baseOrder.faMethod = "PctChange"
baseOrder.faPercentage = "-100"
baseOrder.tif = 'DAY'


# --- Classes and Func. ---
class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self) 
    
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        with open('positions.txt', 'a') as root:
            root.write(' '.join([account, contract.symbol, str(position), str(avgCost)]))
            root.write('\n')
    
    def accountSummary(self, reqId, account, tag, value, currency):
        with open('navs.txt', 'a') as root:
            root.write(' '.join([account, tag, value, currency]))
            root.write('\n')
    
    #def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
     #   with open('curr_orders.txt', 'a') as root:
      #      root.write(orderId, order.account, orderState.status)

    def managedAccounts(self, accountsList: str):
        super().managedAccounts(accountsList)
        with open('flask/accs.txt', 'a') as root:
            root.write(accountsList)

    @staticmethod
    def FillAdaptiveParams(baseOrder: Order, priority: str):
        baseOrder.algoStrategy = "Adaptive"
        baseOrder.algoParams = []
        baseOrder.algoParams.append(TagValue("adaptivePriority", priority))

    def nextOrderId(self):
        with open('num.txt', 'r') as root:
            number = root.readlines()[0]
            number = int(number)

        with open('num.txt', 'w') as root:
            root.write(str(number + 1))

        return number


def get_positions():
    app = IBapi()
    app.connect('127.0.0.1', 7497, clientId)
    print("CONNECTED")
    time.sleep(5)
    thread = threading.Thread(target=app.run)
    app.reqPositions()
    thread.start()
    time.sleep(10)
    try:  
        thread._stop()
    except Exception as stop_marker:
        print(f'Stop error: {type(stop_marker).__name__}')
        return

def get_navs():
    app = IBapi()
    app.connect('127.0.0.1', 7497, clientId)
    print("CONNECTED")
    time.sleep(1)
    app.reqAccountSummary(0, "IPO", "NetLiquidation")
    thread = threading.Thread(target=app.run)
    thread.start()
    time.sleep(1)
    try:  
        thread._stop()
    except Exception as stop_marker:
        print(f'Stop error: {type(stop_marker).__name__}')
        return


def get_accs():
    app = IBapi()
    app.connect('127.0.0.1', 7497, clientId)
    print("CONNECTED")
    time.sleep(5)
    app.reqManagedAccts()
    thread = threading.Thread(target=app.run)
    thread.start()
    time.sleep(10)
    try:  
        thread._stop()
    except Exception as stop_marker:
        print(f'Stop error: {type(stop_marker).__name__}')
        return
 
def get_orders():
    app = IBapi()
    app.connect('127.0.0.1', 7497, clientId)
    print("CONNECTED")
    time.sleep(5)
    app.reqAllOpenOrders()
    thread = threading.Thread(target=app.run)
    thread.start()
    time.sleep(10)
    try:  
        thread._stop()
    except Exception as stop_marker:
        print(f'Stop error: {type(stop_marker).__name__}')
        return

def get_tickers():
    conn = sqlite3.connect("tickers.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Tickers')
    return cursor.fetchall()

def get_nav_risks():
    conn = sqlite3.connect("tickers.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Navs')
    return cursor.fetchall()

def check_tickers(tickers):
    symbols = set()
    for ticker in tickers:
        symbols.add(ticker[2])
    
    with open('navs.txt', 'r') as data:
        position_symbols = set([(line.split())[1] for line in data.readlines()])
    
    not_enough = symbols.difference(position_symbols)
    print(not_enough)

def close_order(acc):
    # закрыть счёт конкретного аккаунта
    global baseOrder
    app = IBapi()
    app.connect('127.0.0.1', 7497, clientId)
    time.sleep(5)

    with open('positions.txt', 'r') as root:
        positions = [line.split() for line in root.readlines()]

    print(positions)

    used = list()
    for position in positions:
        if position[1] not in used:
            contract = Contract()
            contract.secType = 'STK'
            contract.symbol = position[1]
            contract.currency = 'USD'
            contract.exchange = 'SMART'
            used.append(position[1])

            if float(position[2]) >= 0.0:
                baseOrder.action = 'SELL'
            else:
                baseOrder.action = 'BUY'

            ordId = app.nextOrderId()
            app.FillAdaptiveParams(baseOrder, 'Normal')
            app.placeOrder(ordId, contract, baseOrder)

    thread = threading.Thread(target=app.run)
    thread.start()
    time.sleep(3)

    try:  
        thread._stop()
    except Exception as stop_marker:
        print(f'Stop error: {type(stop_marker).__name__}')
        return

def check_risks(risks):
    accounts = list()
    with open('navs.txt', 'r') as root:
        for line in root.readlines():
            accounts.append(line.split())

    conn = sqlite3.connect("tickers.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Navs')
    navs = cursor.fetchall()
    
    orders_to_cancel = set()
    for record in navs:
        for account in accounts:
            print(record[0], account[0])
            if record[0] == account[0]:
                const = record
                break
                
        risk = float(account[2]) - float(const[1])
        if float(risk) > float(const[1]):
            close_order(account[0])

def clear_positions():
    if 'positions.txt' in os.listdir():
        os.remove('positions.txt')

def clear_navs():
    if 'navs.txt' in os.listdir():
        os.remove('navs.txt')

def clear_accs():
    if 'accs.txt' in os.listdir(os.getcwd() + '/flask'):
        os.remove(os.getcwd() + '/flask/accs.txt')

def clear_orders():
    if 'curr_orders.txt' in os.listdir():
        os.remove('curr_orders.txt')


# --- Main Logic ---
get_accs()
while True:
    print('Accounts got...')
    clientId += 1
    get_positions()
    print('Positions got...')
    clientId += 1
    get_navs()
    clientId += 1
    print('Navs got... ')
    risks = get_nav_risks()
    clientId += 1
    print('Risks got...')
    cancel = check_risks(risks)
    clientId += 1
    print('Succeeded check...')

    if cancel:
        for acc in cancel:
            close_order(acc)
            clientId += 1
            print(f"Account {acc} closed")
    else:
        print('No account with high risk.')

    clear_navs()
    clear_positions()

    print('~~ inter-cycle time ~~')
    time.sleep(2)
clear_accs()

# --- End ---
os.abort()
    