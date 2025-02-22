import random

class Robot:
    def __init__(self, canvas, warehouse, robot_id, start_row, start_col):
        self.canvas = canvas
        self.warehouse = warehouse
        self.id = robot_id
        self.row = start_row
        self.col = start_col

        self.target = (start_row, start_col)
        self.state = "waiting"  # waiting, to_order, to_delivery, to_replenish
        self.replenish_target = None

        # Pad dat de robot stap voor stap kan volgen (None = geen pad)
        self.current_path = None

        # Tel hoe vaak de robot achtereenvolgens niet kan bewegen
        self.stuck_steps = 0
        # Drempel om BFS te triggeren (bijv. 5 "mislukte" stappen)
        self.stuck_threshold = 5

        self.robot_radius = warehouse.cell_size // 3
        pixel_x = self.col * warehouse.cell_size + warehouse.cell_size // 2
        pixel_y = self.row * warehouse.cell_size + warehouse.cell_size // 2
        self.robot_item = canvas.create_oval(
            pixel_x - self.robot_radius,
            pixel_y - self.robot_radius,
            pixel_x + self.robot_radius,
            pixel_y + self.robot_radius,
            fill="blue"
        )

    def move_step(self):
        # Als we al een pad hebben, probeer de volgende stap uit dat pad
        if self.current_path and len(self.current_path) > 0:
            next_cell = self.current_path[0]
            # Check of die cel vrij is
            if not self.warehouse.is_cell_occupied(*next_cell) or next_cell in self.warehouse.store_points:
                # Verplaats de robot
                self.row, self.col = next_cell
                self.current_path.pop(0)  # Verwijder deze stap uit de route
                self.update_position_on_canvas()
                self.stuck_steps = 0  # We zijn bewogen, dus niet meer 'stuck'
            else:
                # Cel is bezet; we blijven staan en increment stuck_steps
                self.stuck_steps += 1
                # Als we te vaak vastzitten, probeer opnieuw een route te vinden
                if self.stuck_steps > self.stuck_threshold:
                    self.find_new_path()
        else:
            # We hebben geen (of leeg) current_path; beweeg stap voor stap in Manhattan-stijl
            if (self.row, self.col) != self.target:
                moved = self.try_step_towards_target()
                if not moved:
                    # Robot kon niet bewegen
                    self.stuck_steps += 1
                    if self.stuck_steps > self.stuck_threshold:
                        self.find_new_path()
                else:
                    self.stuck_steps = 0
            else:
                # We zijn bij de target, voer actie uit
                self.do_action_at_target()

    def try_step_towards_target(self):
        """
        Beweeg 1 stap richting self.target (Manhattan),
        retourneer True als het gelukt is, False als we geblokkeerd zijn.
        """
        (tr, tc) = self.target
        drow = tr - self.row
        dcol = tc - self.col

        step_r = 0
        step_c = 0
        if drow != 0:
            step_r = 1 if drow > 0 else -1
        elif dcol != 0:
            step_c = 1 if dcol > 0 else -1

        candidate_r = self.row + step_r
        candidate_c = self.col + step_c

        # Check occupancy
        if not self.warehouse.is_cell_occupied(candidate_r, candidate_c) or \
           (candidate_r, candidate_c) in self.warehouse.store_points:
            self.row = candidate_r
            self.col = candidate_c
            self.update_position_on_canvas()
            return True
        else:
            return False

    def find_new_path(self):
        """Probeer met BFS een nieuw pad te vinden naar self.target."""
        path = self.warehouse.find_path((self.row, self.col), self.target)
        if path is not None and len(path) > 1:
            # De eerste stap is onze huidige positie, die slaan we niet nogmaals op
            self.current_path = path[1:]
            print(f"Robot {self.id} heeft een nieuw pad gevonden van {path[0]} naar {path[-1]}.")
        else:
            # Geen pad gevonden, of pad is triviaal
            self.current_path = None
            print(f"Robot {self.id} kan geen pad vinden naar {self.target}. Blijft voorlopig staan.")
        self.stuck_steps = 0

    def do_action_at_target(self):
        # Actie uitvoeren afhankelijk van de state
        if self.state == "to_order":
            self.warehouse.fulfill_order(self, self.target)
            self.target = self.warehouse.get_random_store_point()
            self.state = "waiting"
        elif self.state == "to_delivery":
            # Aangekomen bij leverpunt -> naar replenish_target
            self.state = "to_replenish"
            self.target = self.replenish_target
        elif self.state == "to_replenish":
            self.warehouse.deliver_product(self, self.target)
            self.target = self.warehouse.get_random_store_point()
            self.state = "waiting"

    def update_position_on_canvas(self):
        pixel_x = self.col * self.warehouse.cell_size + self.warehouse.cell_size // 2
        pixel_y = self.row * self.warehouse.cell_size + self.warehouse.cell_size // 2
        self.canvas.coords(
            self.robot_item,
            pixel_x - self.robot_radius,
            pixel_y - self.robot_radius,
            pixel_x + self.robot_radius,
            pixel_y + self.robot_radius
        )
