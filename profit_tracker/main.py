import terminal_module
import profit_tracker
from time import sleep
from threading import Thread

def __init__():
    #profit_tracker.sandbox_test()
    profit_tracker_process = Thread(target = profit_tracker.main)
    profit_tracker_process.start()
    #sandbox = Thread(target = terminal_module.sandbox)
    #sandbox.start()
    terminal_display_process = Thread(target = terminal_module.main)
    terminal_display_process.start()

__init__()
