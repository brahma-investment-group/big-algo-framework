from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self):
        self.is_position = False
        self.is_order = False

    def start(self, *kwargs):
        pass

    def before_check_positions(self, *kwargs):
        pass

    def check_positions(self, *kwargs):
        pass

    def after_check_positions(self, *kwargs):
        pass

    def before_check_open_orders(self, *kwargs):
        pass

    def check_open_orders(self, *kwargs):
        pass

    def after_check_open_orders(self, *kwargs):
        pass

    def before_send_orders(self, *kwargs):
        pass

    def send_orders(self, *kwargs):
        pass

    def after_send_orders(self, *kwargs):
        pass

    def end(self, *kwargs):
        pass

    def execute(self):
        self.start()

        self.before_check_open_orders()
        self.check_positions()
        self.after_check_positions()

        if self.is_position:
            self.before_check_open_orders()
            self.check_open_orders()
            self.after_check_open_orders()

            if self.is_order:
                self.before_send_orders()
                self.send_orders()
                self.after_send_orders()

        self.end()
