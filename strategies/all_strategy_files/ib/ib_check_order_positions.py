
class IbCheckOrderPositions():
    def __init__(self, order_dict):
        self.order_dict = order_dict

    def check_ib_positions(self):
        is_position = False
        if self.order_dict["broker"].is_exist_positions(self.order_dict):
            is_position = True

        return is_position

    def check_ib_orders(self):
        is_order = True
        return is_order
