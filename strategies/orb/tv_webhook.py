from fastapi import FastAPI
from pydantic import BaseModel
import traceback
from strategies.orb.tv_main import start_main
from strategies.orb import config

class webhook_message(BaseModel):
    """ Webhook_message format:
    {
    "ticker": "{{ticker}}",
    "time_frame": {{interval}},
    "entry_time": "{{time}}",

    "entry": {{entry}},
    "sl": {{plot("sl")}},
    "tp1": {{plot("tp1")}},
    "tp2": {{plot("tp2")}},
    "risk": {{plot("risk")}},

    "direction": {{plot("direction")}},
    "open_action": {{plot("open_action")}},
    "close_action": {{plot("close_action")}},

    "passphrase": "123",
    }
    """

    ticker: str
    time_frame: float
    entry_time: int
    entry: float
    sl: float
    tp1: float
    tp2: float
    risk: float
    direction: str
    open_action: str
    close_action: str
    passphrase: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/orb/options')
async def orb_options(webhook_message: webhook_message):
    print("Webhook Recieved:", webhook_message.dict())

    if webhook_message.passphrase not in webhook_message.passphrase:
        return {
            "status": "fail",
            "code": "401",
            "message": "Unauthorized, no passphrase"
        }

    if webhook_message.passphrase != config.webhook_passphrase:
        return {
            "status": "fail",
            "code": "401",
            "message": "Invalid passphrase"
        }

    try:
        trading_params = start_main(webhook_message.dict())  # Add this line to push to trade.
        traceback.print_exc()

        return {
            "status": "success",
            "code": "200",
            "message": f"{str(trading_params)}"
        }

    except Exception as exc:
        traceback.print_exc()
        print(f'exception in orb_options: {str(exc)}')

        return {
            "status": "error",
            "code": "500",
            "message": f"{str(Exception)}"
        }

