from fastapi import FastAPI
from pydantic import BaseModel
from strategies.all_strategy_files.webhooks.ib_orb import *
from strategies.ib_orb.twitter_bot import send_twitter_alerts
from strategies.ib_orb.discord_bot import send_discord_alerts

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

    # if webhook_message.is_close == 0:
    #     await send_discord_alerts(webhook_message)
    #     await send_twitter_alerts(webhook_message)
