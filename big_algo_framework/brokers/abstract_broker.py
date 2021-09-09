from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def get_market_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'marketOrder' method."
        )

    def get_stop_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'stopLimitOrder' method."
        )

    def get_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'limitOrder' method."
        )

    def get_stop_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'stopOrder' method."
        )

    def send_bracket_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'bracketOrder' method."
        )

