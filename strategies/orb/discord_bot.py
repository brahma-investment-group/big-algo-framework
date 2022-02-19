import time
from discord_webhook import DiscordWebhook, DiscordEmbed
from strategies.orb import config

async def send_discord_alerts(data):
    webhook = config.discord["orb"]
    color = "00FF00" if data.direction == "Bullish" else "FF0000"

    try:
        prem_webhook = DiscordWebhook(username="Brahma Investment Group (BIG)",
                                      avatar_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxKypivRu2U0me3b7a2FECr34Z3_Q7S74yAtKqY_481zZL7VIPQwB7ohE-QPtVh6_ESjI&usqp=CAU",
                                      url=webhook)

        embed = DiscordEmbed(title=data.ticker,
                             url="https://www.tradingview.com/chart/",
                             description="FREE Alerts -  Opening Range Breakout (ORB) Strategy",
                             color=color,
                             author={"name": "Brahma Investment Group (BIG)",
                                     "url": "http://google.com",
                                     "icon_url": "https://i.imgur.com/R66g1Pe.jpg"},
                             footer={"text": "Not Investment Advice! Ideas Are NOT Signals To Buy/Sell & For Educational/Entertainment Only",
                                     "icon_url": "https://i.imgur.com/fKL31aD.jpg"}
                             )

        embed.add_embed_field(name="Time Frame", value=str(data.time_frame), inline=True)
        embed.add_embed_field(name="Direction", value=data.direction, inline=True)
        embed.add_embed_field(name="Limit Entry", value="$" + str(data.entry), inline=True)
        embed.add_embed_field(name="Stop Loss", value="$" + str(data.sl), inline=True)
        embed.add_embed_field(name="Take Profit 1", value="$" + str(data.tp1), inline=True)
        embed.add_embed_field(name="Take Profit 2", value="$" + str(data.tp2), inline=True)

        prem_webhook.add_embed(embed)
        prem_webhook.execute(remove_embeds=True, remove_files=True)

    except Exception as e:
        print("[X] Discord Error:\n>", e)
