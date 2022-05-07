
class IbCheckOrderPositions():
    def __init__(self, order_dict):
        self.order_dict = order_dict

    def check_ib_positions(self):
        is_position = False
        positions = self.order_dict["broker"].get_position_by_ticker(self.order_dict)

        if positions.empty:
            is_position = True

        return is_position

    def check_ib_orders(self):
        is_order = False
        orders = self.order_dict["broker"].get_order_by_ticker(self.order_dict)

        if orders.empty:
            is_order = True

        return is_order
