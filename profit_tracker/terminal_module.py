import os
import requests
import sys
import curses
import profit_tracker
from time import sleep
import numbers
from termcolor import colored

stdscreen = None

space_between_categories = 0
categories = ['COIN', 'BALANCE', 'CURRENT_PRICE_BTC', 'AVG_PURCHASE_PRICE_BTC', 'PROFIT_LOSS_USD']
category_start_posiitions = [0]

#display constants
HEADER_HEIGHT = 2
TABLE_BODY_HEIGHT = 0

#used for debugging. prints the entire profit data dictionary
def sandbox():
    print(profit_tracker.profit_data)

def main():
    global stdscreen
    stdscreen = curses.initscr()
    curses.start_color()
    curses.init_color(0, 0, 0, 0)
    stdscreen.clear()
    title_sequence()
    table_body_win = init_table()
    table_body_string = create_table_body(table_body_win)
    #profit_tracker.main()
    table_body_win.addstr(0, 0, table_body_string)

    #warning colors
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    #success colors
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    #curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_GREEN)
    update_table_values(table_body_win)
    while True:
        sleep(1)
        update_table_values(table_body_win)


def update_table_values(table_body_win):

    if profit_tracker.profit_data == {}:
        #profit_data not yet loaded, break the function
        return
    end_line = "_" * curses.COLS
    table_body_win.clear()

    for key,entry in profit_tracker.profit_data.items():
        current_position = 1
        table_body_win.addstr("|")
        table_body_win.addstr(key)
        current_position += len(key)-1
        while current_position < category_start_posiitions[1]:
            table_body_win.addstr("_")
            current_position += 1
        table_body_win.addstr("|")
        current_position += 1

        if 'BALANCE' in entry:
            balance_string = "{0:.5f}".format(entry['BALANCE'])
            table_body_win.addstr(balance_string)
            current_position += len(balance_string) - 1

        while(current_position) < category_start_posiitions[2] - 1:
            table_body_win.addstr("_")
            current_position += 1
        table_body_win.addstr("|")
        current_position += 1

        if 'CURRENT_PRICE_BTC' in entry:
            current_price_btc_string = "{0:.8f}".format(entry['CURRENT_PRICE_BTC'])
            if entry['CURRENT_PRICE_BTC'] > 0: #TODO find changes in currency to alter color of current price if it has gone up or down
                table_body_win.addstr(current_price_btc_string, curses.color_pair(2))
            current_position += len(current_price_btc_string) - 1
        else:
            table_body_win.addstr("N/A")
            current_position += 2

        while current_position < category_start_posiitions[3] - 1:
            table_body_win.addstr("_")
            current_position += 1
        table_body_win.addstr("|")
        current_position += 1

        avg_purchase_price_string = "{0:.8f}".format(entry['AVG_PURCHASE_PRICE_BTC'])
        table_body_win.addstr(avg_purchase_price_string)
        current_position += len(avg_purchase_price_string) - 1

        while current_position < category_start_posiitions[4] - 1:
            table_body_win.addstr("_")
            current_position += 1
        table_body_win.addstr("|")
        current_position += 1

        if 'PROFIT_LOSS_USD' in entry:
            profit_loss_string = "{0:.8f}".format(entry['PROFIT_LOSS_USD'])
            if entry['PROFIT_LOSS_USD'] > 0:
                table_body_win.addstr(profit_loss_string, curses.color_pair(2))
            else:
                table_body_win.addstr(profit_loss_string, curses.color_pair(1))
            current_position += len(profit_loss_string) - 1
        else:
            table_body_win.addstr("N/A")
            current_position += 2

        while current_position < curses.COLS - 6:
            table_body_win.addstr("_")
            current_position += 1
        table_body_win.addstr("|")
        empty_row = "|"
        empty_row += ' ' * (curses.COLS-2)
        empty_row += "|"
        table_body_win.addstr(empty_row)

    table_body_win.refresh()

#creates the curses window, and creates the window for the table and header
#returns the table_body_win (curses window instance)
def init_table():
    global TABLE_BODY_HEIGHT

    stdscreen.keypad(True)
    init_table_header()
    TABLE_BODY_HEIGHT = curses.LINES - 1
    table_body_win = curses.newwin(TABLE_BODY_HEIGHT, curses.COLS, HEADER_HEIGHT, 0)
    #empty_table_body_string = create_table_body(table_body_win)
    # try:
    #     table_body_win.addstr(0, 0, empty_table_body_string)
    # except:
    #     #do nothing. https://bugs.python.org/issue8243
    #     table_body_win.addstr(0, 0, empty_table_body_string)
    #     pass
    table_body_win.refresh()
    return table_body_win

def init_table_header():
    width = curses.COLS
    title_win = curses.newwin(HEADER_HEIGHT, curses.COLS, 0, 0)
    title_win.addstr(0, 0, create_table_header())
    title_win.refresh()

#returns table_body string
def create_table_body(table_body_win):
    global category_start_posiitions
    screen_height = curses.LINES - 4
    screen_width = curses.COLS - 2
    end_line = "_" * curses.COLS
    line = ""
    for i in range(screen_width):
        if i in category_start_posiitions:
            line += "|"
        elif i == screen_width-1:
            line += "|"
        else:
            line += " "
    table_body = ""
    table_body += end_line
    for i in range(screen_height-HEADER_HEIGHT):
        table_body += line
        table_body += '\n'
    table_body += end_line
    return table_body

def create_table_header():
    global space_between_categories
    global categories
    screen_height = curses.LINES
    screen_width = curses.COLS
    categories_char_count = 0
    table_header_string = ""
    for category in categories:
        categories_char_count += len(category)
    space_between_categories = (screen_width - categories_char_count) // len(categories)

    for category in categories:
        table_header_string += category
        for i in range(space_between_categories):
            table_header_string += " "
    for i,c in enumerate(table_header_string):
        if c != " ":
            if i != 0:
                if table_header_string[i-1] == " ":
                    category_start_posiitions.append(i-1)
    return table_header_string

def title_sequence():
    title_words = ['BITTREX', 'PROFIT', 'TRACKER']
    title_ascii_art = []
    title_window = curses.newwin(curses.LINES-1, curses.COLS-1, 0, 0)
    title_ascii_art_list = [
        '  ___ ___ _____ _____ ___ _____  __ ',
        ' | _ )_ _|_   _|_   _| _ \ __\ \/ / ',
        ' | _ \| |  | |   | | |   / _| >  <  ',
        ' |___/___| |_|  _|_|_|_|_\___/_/\_\ ',
        ' | _ \ _ \/ _ \| __|_ _|_   _|      ',
        ' |  _/   / (_) | _| | |  | |        ',
        ' |_|_|_|_\____/|_| |___| |_|___ ___ ',
        ' |_   _| _ \  /_\ / __| |/ / __| _ \ ',
        '   | | |   / / _ \ (__| | <| _||   /',
        '   |_| |_|_\/_/ \_\___|_|\_\___|_|_\ ',
    ]

    for line in title_ascii_art_list:
        title_window.addstr(line)
        title_window.addstr('\n')



    title_window.refresh()
    sleep(5)
    del title_window
    return

    title_string = """
{}{}
{}
{}{}

{}
    """

    #print(title_string.format(bcolors.OKBLUE, title_ascii_art[0], title_ascii_art[1], title_ascii_art[2], bcolors.ENDC, "github link here"))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
