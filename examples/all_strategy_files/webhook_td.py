from fastapi import FastAPI
from pydantic import BaseModel
from examples.tda_sqzmom.process_webhook import process_webhook


app = FastAPI()

class webhook_message(BaseModel):
        ticker: str
        close: float
        quantity: float
        dte: float
        callput: str
        instruction: str
        passphrase: str


@app.post('/test')
def option_order(webhook_message: webhook_message):
    print("Webhook Recieved:", webhook_message.dict())
    process_webhook(webhook_message)
