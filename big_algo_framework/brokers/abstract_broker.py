from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def get_market_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'marketOrder' method."
        )

    @abstractmethod
    def get_stop_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'stopLimitOrder' method."
        )

    @abstractmethod
    def get_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'limitOrder' method."
        )

    @abstractmethod
    def get_stop_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'stopOrder' method."
        )

    @abstractmethod
    def send_bracket_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'bracketOrder' method."
        )

