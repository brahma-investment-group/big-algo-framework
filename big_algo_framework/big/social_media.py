import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import asyncio
import tweepy

class SocialMedia():
    def __init__(self, data):
        self.data = data

    async def send_discord_alerts(self, discord_data):
        color = "00FF00" if self.data.direction == "Bullish" else "FF0000"

        username = "Brahma Investment Group (BIG)" if "username" not in discord_data else discord_data["username"]
        avatar_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxKypivRu2U0me3b7a2FECr34Z3_Q7S74yAtKqY_481zZL7VIPQwB7ohE-QPtVh6_ESjI&usqp=CAU" if "avatar_url" not in discord_data else discord_data["avatar_url"]
        webhook = discord_data["webhook"]
        description = discord_data["description"]
        author_name = "Brahma Investment Group (BIG)" if "author_name" not in discord_data else discord_data["author_name"]
        author_url = "http://google.com" if "author_url" not in discord_data else discord_data["author_url"]
        author_icon_url = "https://i.imgur.com/R66g1Pe.jpg" if "author_icon_url" not in discord_data else discord_data["author_icon_url"]
        footer_text = "Not Investment Advice! Ideas Are NOT Signals To Buy/Sell & For Educational/Entertainment Only" if "footer_text" not in discord_data else discord_data["footer_text"]
        footer_icon_url = "https://i.imgur.com/fKL31aD.jpg" if "footer_icon_url" not in discord_data else discord_data["footer_icon_url"]

        try:
            prem_webhook = DiscordWebhook(username=username,
                                          avatar_url=avatar_url,
                                          url=webhook)

            embed = DiscordEmbed(title=self.data.ticker,
                                 url="https://www.tradingview.com/chart/",
                                 description=description,
                                 color=color,
                                 author={"name": author_name,
                                         "url": author_url,
                                         "icon_url": author_icon_url},
                                 footer={"text": footer_text,
                                         "icon_url": footer_icon_url}
                                 )

            embed.add_embed_field(name="Time Frame", value=str(self.data.time_frame), inline=True)
            embed.add_embed_field(name="Direction", value=self.data.direction, inline=True)
            embed.add_embed_field(name="Limit Entry", value="$" + str(self.data.entry), inline=True)
            embed.add_embed_field(name="Stop Loss", value="$" + str(self.data.sl), inline=True)
            embed.add_embed_field(name="Take Profit 1", value="$" + str(self.data.tp1), inline=True)
            embed.add_embed_field(name="Take Profit 2", value="$" + str(self.data.tp2), inline=True)

            prem_webhook.add_embed(embed)
            prem_webhook.execute(remove_embeds=True, remove_files=True)

        except Exception as e:
            print("[X] Discord Error:\n>", e)

    async def send_twitter_alerts(self, twitter_data):
        await asyncio.sleep(1800)

        tweet = twitter_data["tweet"].encode("latin-1", "backslashreplace").decode("unicode_escape")
        tw_auth = tweepy.OAuthHandler(twitter_data["tw_ckey"], twitter_data["tw_csecret"])
        tw_auth.set_access_token(twitter_data["tw_atoken"], twitter_data["tw_asecret"])
        tw_api = tweepy.API(tw_auth)
        try:
            tw_api.update_status(
                status = tweet
            )
        except Exception as e:
            print("[X] Twitter Error:\n>", e)
