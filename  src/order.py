class Product:
    def __init__(self, barcode, name="Generic Product"):
        self.barcode = barcode
        self.name = name

class Order:
    order_counter = 0

    def __init__(self, product, quantity):
        self.id = Order.order_counter
        Order.order_counter += 1
        self.product = product
        self.quantity = quantity  # Totaal aantal benodigde producten
        self.assigned_robots = []  # Lijst van robots die aan deze order zijn toegewezen

    def assign_robot(self, robot):
        self.assigned_robots.append(robot)
