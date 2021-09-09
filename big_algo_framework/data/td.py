from abstract_data import Data
import tda

class TD(Data):
    def __init__(self, ticker, api_key, redirect_uri, credentials_path='./ameritrade-credentials.json'):
        self.api_key = api_key
        self.redirect_uri = redirect_uri
        self.credentials_path = credentials_path
        self.ticker = ticker

        try:
            self.tda_client = tda.auth.client_from_token_file(self.credentials_path, self.api_key)

        except FileNotFoundError:
            from selenium import webdriver

            with webdriver.Chrome() as driver:
                self.tda_client = tda.auth.client_from_login_flow(driver, self.api_key, self.redirect_uri, self.credentials_path)

    def get_hist_equity_data(self, period_type=None, period=None, frequency_type=None, frequency=None,
                             start_dt=None, end_dt=None, extended_hours=False):
        """Fetch historic equity data from TDA client"""
        response = self.tda_client.get_price_history(symbol=self.ticker[0],
                                                     period_type=period_type ,
                                                     period=period,
                                                     frequency_type=frequency_type,
                                                     frequency=frequency,
                                                     start_datetime=start_dt,
                                                     end_datetime=end_dt,
                                                     need_extended_hours_data=extended_hours)

        return response.json()

    def get_streaming_equity_data(self):
        pass

    def get_hist_options_data(self, contract_type=None, strike_count=None, include_quotes=None, strategy=None, interval=None,
                              strike=None, strike_range=None, from_date=None, to_date=None, volatility=None,
                              underlying_price=None, interest_rate=None, days_to_expiration=None, exp_month=None,
                              option_type=None):
        """Fetch historic options data from TDA client"""
        response = self.tda_client.get_option_chain(symbol=self.ticker[0],
                                                    contract_type=contract_type,
                                                    strike_count=strike_count,
                                                    include_quotes=include_quotes,
                                                    strategy=strategy,
                                                    interval=interval,
                                                    strike=strike,
                                                    strike_range=strike_range,
                                                    from_date=from_date,
                                                    to_date=to_date,
                                                    volatility=volatility,
                                                    underlying_price=underlying_price,
                                                    interest_rate=interest_rate,
                                                    days_to_expiration=days_to_expiration,
                                                    exp_month=exp_month,
                                                    option_type=option_type)

        return response.json()

    def get_streaming_options_data(self):
        pass


x = TD(["MSFT"], "ANFJZCL8HLAOEJERGC9CJENJPGUVFU60", "http://localhost:8080/")
print(x.get_hist_equity_data())
