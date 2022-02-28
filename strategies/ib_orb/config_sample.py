orb_oid = 0

webhook = {
    "orb_passphrase":"xxxxxxx"
}

contract = {
    "orb_sec_type":"STK",
    "orb_option_action": "BUY",
    "orb_option_range": "OTM",
    "orb_option_strikes": 1,
    "orb_option_expiry_days": 2,
    "orb_currency":"USD",
    "orb_exchange":"SMART"
}

database = {
    "database_name": "market_data",
    "orders_table":"orb_orders",

    "orb_strategy_table":"orb_strategy"
}

# TWS Paper: 7497
# Gateway Paper: 4002

# TWS Live: 7496
# Gateway Live: 4001

ib_account = {
    "orb_account_no":"DUXXXXXXXXXX",
    "orb_ip_address":'127.0.0.1',
    "orb_port":7497,
    "orb_ib_client":2
}

risk_param = {
    "orb_total_risk": 5,
    "orb_total_risk_units": "percent",
    "orb_max_position_percent": 10
}

twitter = {
    "tw_ckey":"XXXXXXXXXXXXXXXXX",
    "tw_csecret":"XXXXXXXXXXXXXXXXXXXXXX",
    "tw_atoken":"XXXXXXXXXXXXXXXXXXXXXX",
    "tw_asecret":"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}

discord = {
    "orb": "https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXXXXXXX",
}
