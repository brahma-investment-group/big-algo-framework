ROADMAP
----------------
1. To include brokers:
- Metratrader5 (Connects to any Forex Broker that support MT5) https://www.mql5.com/en/docs/integration/python_metatrader5
- CCXT - (Connects to any Crypto Broker that CCXT supports)
https://github.com/ccxt/ccxt
- TDA-API (Connects to TD Ameritrade)
https://github.com/alexgolec/tda-api
2. To include documentation


ABOUT
----------------
big-algo-framework is a trading algorithm framework that connects to several brokers and creates, places and manages orders/positions automatically.

big-algo-framework comes in 2 parts:

- Framework
- Examples

Framework
----------------
The framework consists of several broker APIs (or Python wrappers for the broker API). Currently the following brokers are supported:
01. Interactive Brokers - https://interactivebrokers.github.io/tws-api/introduction.html

The framework also comes with common functionality like 'Position Sizing", "Databases" and these are located in the 'big' folder.

Additionally the framework comes with examples that can be used as a starter template for any strategy. Speaking of examples....

Examples
----------------
Developers can create their own strategies/trading bot using the the framework. The examples folder consists of many common functionalities that can be used for any strategy. Additionally, common functionalities have been provided for each broker that is supported by the framework.

Data:
----------------
The framework is built in a way that they are completely unaware of the data source. This means, the developer can fetch and pass data from anywhere (tradingview via webhooks, database or even stream live data). Except for options data from TD Ameritrade, the framework doesn't have any data related functions. That means, the framework doesn't request/store any equity/crypto/forex data. Instead, the strategies receive the data in form of a webhook via Tradingview alerts and FASTAPI. Tradingview alerts has the capability to send any data (ex: OHLC, indicator values, ticker, exchange, timeframe etc.). The examples simply takes the webhook, processes it to prepare the order and sends the order to the broker. 

Other features
----------------
- The framework supports Postgresql. All trade related data are stored in database tables which can be configured from the config file. 
- The framework supports posting alerts on Discord and Twitter. 

The program has been written using Object Oriented concepts. This allows a developer to change any behavior of the framework by inheriting the parent classes and overriding the functions.

I utilized help from several places and only feel it fair to give reference to the information i consumed. So here is a list of useful references:

Mr. Baker @MarketMakerLite :
--
https://marketmakerlite.com (coming soon!)

https://docs.marketmakerlite.com

https://github.com/MarketMakerLite

https://discord.gg/DcU3XBSz

Mr. Pssolanki @pssolanki :
--
https://github.com/pssolanki111/polygon

https://discord.gg/Z7FXQ7RD

Alex Golec tda-api wrapper :
--
https://github.com/alexgolec/tda-api.git

https://tda-api.readthedocs.io/en/latest/index.html

https://discord.gg/eQMHg594

KJJorgensen:
--
https://github.com/KJJorgensen

**Disclaimer**:  The software is provided "as is". Users are encouraged to test the software on paper account, before risking real money. The author accept no responsibility for any damage that might stem from use of big-algo-framework. See the LICENSE file for more details.