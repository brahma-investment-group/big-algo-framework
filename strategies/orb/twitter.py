import time
import tweepy
from strategies.orb import config

def send_alert(data):
    msg = \
        "Delayed Trading Alerts - For Education Purposes Only"+ "\n" + \
        "$" + data.ticker + "/" + data.direction + "/$" + str(data.entry) + "\n\n" + \
        "For real time join : discord.gg/u3gQGhkPKU" + "\n\n" + \
        "@moneytimegroup #TheStrat #ORB #OptionsTrading #tradingtips #stockmarkets #stocks #investing #Automation #Algorithms"

    msg = msg.encode("latin-1", "backslashreplace").decode("unicode_escape")
    tw_auth = tweepy.OAuthHandler(config.twitter["tw_ckey"], config.twitter["tw_csecret"])
    tw_auth.set_access_token(config.twitter["tw_atoken"], config.twitter["tw_asecret"])
    tw_api = tweepy.API(tw_auth)
    try:
        tw_api.update_status(
            status=msg
        )
    except Exception as e:
        print("[X] Twitter Error:\n>", e)
