from abc import ABC, abstractmethod

class Data(ABC):
    @abstractmethod
    def get_historic_stock_data(self, *kwargs):
        raise NotImplementedError(
            "Each data must implement the 'get_historic_stock_data' method."
        )

    @abstractmethod
    def get_historic_option_data(self, *kwargs):
        raise NotImplementedError(
            "Each data must implement the 'get_historic_option_data' method."
        )
