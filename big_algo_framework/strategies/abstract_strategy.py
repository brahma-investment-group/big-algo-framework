from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self):
        self.check_long = False
        self.check_short = False

        self.trade_long = False
        self.trade_short = False

        self.send_trade = False

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

    def check_high_level_market_conditons(self, *kwargs):
        pass

    def check_long_conditions(self, *kwargs):
        pass

    def check_short_conditions(self, *kwargs):
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

        self.before_check_open_orders()
        self.check_open_orders()
        self.after_check_open_orders()

        self.check_high_level_market_conditons()

        if self.check_long:
            self.check_long_conditions()
            if self.trade_long:
                self.send_trade = True

        if self.check_short:
            self.check_short_conditions()
            if self.trade_short:
                self.send_trade = True

        if self.send_trade:
            self.before_send_orders()
            self.send_orders()
            self.after_send_orders()

        self.end()
