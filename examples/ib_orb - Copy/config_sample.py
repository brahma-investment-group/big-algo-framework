ib_order_id = 0

webhook = {
    "passphrase":"xxxxxxx"
}

contract = {
    "sec_type":"STK",
    "option_action": "BUY",
    "option_range": "OTM",
    "option_strikes": 1,
    "option_expiry_days": 2,
    "currency":"USD",
    "exchange":"SMART"
}

database = {
    "database_name": "market_data",
    "orders_table":"orb_orders",

    "strategy_table":"orb_strategy"
}

# TWS Paper: 7497
# Gateway Paper: 4002

# TWS Live: 7496
# Gateway Live: 4001

ib_account = {
    "account_no":"DUXXXXXXXXXX",
    "ip_address":'127.0.0.1',
    "port":7497,
    "ib_client":2
}

risk_param = {
    "total_risk": 5,
    "total_risk_units": "percent",
    "max_position_percent": 10
}

twitter = {
    "tw_ckey":"XXXXXXXXXXXXXXXXX",
    "tw_csecret":"XXXXXXXXXXXXXXXXXXXXXX",
    "tw_atoken":"XXXXXXXXXXXXXXXXXXXXXX",
    "tw_asecret":"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}

discord = {
    "webhook": "https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXXXXXXX",
}
