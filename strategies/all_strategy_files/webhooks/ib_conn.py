import threading
from ibapi.account_summary_tags import AccountSummaryTags
from strategies.all_strategy_files.child_classes.brokers_ib_child import *

def websocket_con(broker):
    broker.run()

def connect_ib(broker, ip_address, port, ib_client):
    # Connects to interactive brokers with the specified port/client and returns the last order ID.
    broker.connect(ip_address, port, ib_client)
    time.sleep(1)
    broker.reqPositions()
    time.sleep(1)
    broker.reqOpenOrders()
    time.sleep(1)
    broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
    time.sleep(1)

    con_thread = threading.Thread(target=websocket_con, args=(broker,), daemon=True)
    con_thread.start()
    time.sleep(1)

    broker.reqIds(1)
    time.sleep(1)

    return broker.orderId