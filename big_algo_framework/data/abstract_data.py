from abc import ABC, abstractmethod

class Data(ABC):
    @abstractmethod
    def get_hist_equity_data(self, *kwargs):
        raise NotImplementedError(
            "Each data source must implement the 'get_hist_equity_data' method."
        )

    @abstractmethod
    def get_streaming_equity_data(self, *kwargs):
        raise NotImplementedError(
            "Each data source must implement the 'get_streaming_equity_data' method."
        )

    @abstractmethod
    def get_hist_options_data(self, *kwargs):
        raise NotImplementedError(
            "Each data source must implement the 'get_hist_options_data' method."
        )

    @abstractmethod
    def get_streaming_options_data(self, *kwargs):
        raise NotImplementedError(
            "Each data source must implement the 'get_streaming_options_data' method."
        )
