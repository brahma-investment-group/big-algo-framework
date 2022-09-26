from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def get_market_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_market_order' method."
        )

    @abstractmethod
    def get_stop_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_stop_limit_order' method."
        )

    @abstractmethod
    def get_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_limit_order' method."
        )

    @abstractmethod
    def get_stop_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_stop_order' method."
        )

    @abstractmethod
    def get_trailing_stop_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_trailing_stop_order' method."
        )

    @abstractmethod
    def get_trailing_stop_limit_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_trailing_stop_limit_order' method."
        )

    @abstractmethod
    def get_oto_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'send_oto_order' method."
        )

    @abstractmethod
    def get_oco_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'send_oco_order' method."
        )

    @abstractmethod
    def send_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'send_order' method."
        )

    @abstractmethod
    def get_order_by_symbol(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_order' method."
        )

    @abstractmethod
    def get_all_orders(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_all_orders' method."
        )

    @abstractmethod
    def get_position_by_symbol(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_position' method."
        )

    @abstractmethod
    def get_all_positions(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_all_positions' method."
        )

    @abstractmethod
    def cancel_order(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'cancel_order' method."
        )

    @abstractmethod
    def cancel_all_orders(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'cancel_all_orders' method."
        )

    @abstractmethod
    def close_position(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'close_position' method."
        )

    @abstractmethod
    def close_all_positions(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'close_all_positions' method."
        )

    @abstractmethod
    def get_long_call_vertical_spread_contract(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_long_call_vertical_spread_contract' method."
        )

    @abstractmethod
    def get_short_call_vertical_spread_contract(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_short_call_vertical_spread_contract' method."
        )

    @abstractmethod
    def get_long_put_vertical_spread_contract(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_long_put_vertical_spread_contract' method."
        )

    @abstractmethod
    def get_short_put_vertical_spread_contract(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_short_put_vertical_spread_contract' method."
        )

    @abstractmethod
    def get_account(self, *kwargs):
        raise NotImplementedError(
            "Each broker must implement the 'get_account' method."
        )


