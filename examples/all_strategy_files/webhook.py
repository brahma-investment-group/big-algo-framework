from fastapi import FastAPI
from pydantic import BaseModel
from examples.ib_orb.read_queue import *
from big_algo_framework.big.social_media import SocialMedia

app = FastAPI()

class webhook_message(BaseModel):
    ticker: str
    exchange: str
    time_frame: float
    entry_time: int
    entry: float
    sl: float
    tp1: float
    tp2: float
    risk: float
    direction: str
    passphrase: str
    is_close: int

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/ib/orb')
async def ib_orb(webhook_message: webhook_message):
    ib_orb_queue.put(webhook_message)

    if webhook_message.is_close == 0:
        discord_data = {
            "webhook": config.discord["orb"],
            "description": "FREE Alerts -  Opening Range Breakout (ORB) Strategy",
        }

        twitter_data = {
            "tw_ckey": config.twitter["tw_ckey"],
            "tw_csecret": config.twitter["tw_csecret"],
            "tw_atoken": config.twitter["tw_atoken"],
            "tw_asecret": config.twitter["tw_asecret"],

            "tweet": "Delayed Trading Alerts - For Education Purposes Only" + "\n" + \
            "$" + webhook_message.ticker + "/" + webhook_message.direction + "/$" + str(webhook_message.entry) + "\n\n" + \
            "For real time join : discord.gg/u3gQGhkPKU" + "\n\n" + \
            "#TheStrat #ORB #OptionsTrading #tradingtips #stockmarkets #stocks #investing #Automation #Algorithms"
        }

        social_media = SocialMedia(webhook_message)
        await social_media.send_discord_alerts(discord_data)
        await social_media.send_twitter_alerts(twitter_data)