from abc import ABC, abstractmethod

class Data(ABC):
    @abstractmethod
    def get_options_data(self, *kwargs):
        raise NotImplementedError(
            "Each data must implement the 'get_options_data' method."
        )
