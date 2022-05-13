
class IbCheckOrderPositions():
    def __init__(self, order_dict):
        self.order_dict = order_dict

    def check_ib_positions(self):
        is_position = False
        positions = self.order_dict["broker"].get_position_by_ticker(self.order_dict)

        if not positions.empty:
            is_position = True

        return is_position

    def check_ib_orders(self):
        is_order = False
        orders = self.order_dict["broker"].get_order_by_ticker(self.order_dict)

        if not orders.empty:
            print(orders)
            orders = orders.reset_index()

            for ind in orders.index:
                direction = orders.iloc[ind]["direction"]
                order_id = orders.iloc[ind]["parent_order_id"]

                if direction != self.order_dict["direction"]:
                    self.order_dict["broker"].cancel_order(self.order_dict, order_id)
                    is_order = False

                else:
                    is_order = True

        return is_order
