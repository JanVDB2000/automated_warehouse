import tkinter as tk
import random
from collections import deque

class Warehouse:
    def __init__(self, canvas, rows=100, cols=100, cell_size=10):
        self.canvas = canvas
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # Grid met voorraad
        self.grid = [[10 for _ in range(cols)] for _ in range(rows)]
        self.cell_rectangles = [[None for _ in range(cols)] for _ in range(rows)]

        # Store points (rij, kolom)
        self.store_points = [
            (0, 0),
            (0, cols - 1),
            (rows - 1, 0),
            (rows - 1, cols - 1)
        ]
        # Delivery points (rij, kolom)
        self.delivery_points = [
            (0, cols // 2),
            (rows - 1, cols // 2)
        ]

        self.draw_grid()
        self.robots = []

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="white", outline="gray"
                )
                self.cell_rectangles[r][c] = rect

        # Store points in lichtblauw
        for (r, c) in self.store_points:
            x1 = c * self.cell_size
            y1 = r * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="lightblue", outline="black"
            )

        # Leverpunten in lichtgroen
        for (r, c) in self.delivery_points:
            x1 = c * self.cell_size
            y1 = r * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="lightgreen", outline="black"
            )

    def is_cell_occupied(self, r, c):
        if (r, c) in self.store_points:
            return False
        # Anders checken of er al een robot staat
        for robot in self.robots:
            if (robot.row, robot.col) == (r, c):
                return True
        return False

    def update(self):
        for robot in self.robots:
            robot.move_step()
        self.canvas.after(200, self.update)

    def update_cell(self, r, c):
        inv = self.grid[r][c]
        if inv <= 0:
            color = "red"
        elif inv < 3:
            color = "orange"
        elif inv < 10:
            color = "yellow"
        elif inv == 10:
            color = "white"
        else:
            color = "lightgreen"
        rect_id = self.cell_rectangles[r][c]
        self.canvas.itemconfig(rect_id, fill=color)

    def update_all_cells(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.update_cell(r, c)

    def new_order(self):
        # Zoek een cel met voorraad
        available_cells = [
            (r, c) for r in range(self.rows)
            for c in range(self.cols) if self.grid[r][c] > 0
        ]
        if not available_cells:
            print("Geen voorraad beschikbaar om de order te vervullen!")
            return

        order_cell = random.choice(available_cells)
        waiting_robots = [rbt for rbt in self.robots if rbt.state == "waiting"]
        if waiting_robots:
            chosen_robot = random.choice(waiting_robots)
            chosen_robot.target = order_cell
            chosen_robot.state = "to_order"
            print(f"Robot {chosen_robot.id} gaat order uitvoeren op cel {order_cell}")
        else:
            print("Geen beschikbare robot voor de order!")

    def fulfill_order(self, robot, cell):
        r, c = cell
        if self.grid[r][c] > 0:
            self.grid[r][c] -= 1
            print(f"Order op cel {cell} uitgevoerd door robot {robot.id}. Voorraad: {self.grid[r][c]}")
            self.update_cell(r, c)
        else:
            print("Voorraad op deze cel is al op!")

    def get_random_store_point(self):
        return random.choice(self.store_points)

    def robot_to_replenish(self):
        # Zoek cellen met voorraad < 5
        low_stock_cells = [
            (r, c) for r in range(self.rows)
            for c in range(self.cols) if self.grid[r][c] < 5
        ]
        if not low_stock_cells:
            print("Geen cellen met lage voorraad gevonden.")
            return

        chosen_cell = random.choice(low_stock_cells)
        waiting_robots = [rbt for rbt in self.robots if rbt.state == "waiting"]
        if waiting_robots:
            chosen_robot = random.choice(waiting_robots)
            chosen_robot.replenish_target = chosen_cell
            # Robot gaat eerst naar een leverpunt
            chosen_robot.target = random.choice(self.delivery_points)
            chosen_robot.state = "to_delivery"
            print(f"Robot {chosen_robot.id} gaat naar een leverpunt om cel {chosen_cell} aan te vullen.")
        else:
            print("Geen robot beschikbaar voor aanvulling!")

    def deliver_product(self, robot, cell):
        r, c = cell
        amount = 5  # Hoeveelheid om bij te vullen
        max_stock = 10
        old_val = self.grid[r][c]
        self.grid[r][c] = min(self.grid[r][c] + amount, max_stock)
        print(f"Robot {robot.id} levert product aan cel {cell}. Voorraad: {old_val} -> {self.grid[r][c]}")
        self.update_cell(r, c)

    def find_path(self, start, goal):
        if start == goal:
            return [start]
        queue = deque()
        visited = set()
        queue.append((start, [start]))
        visited.add(start)

        while queue:
            current, path = queue.popleft()
            (r, c) = current

            # Buren: up, down, left, right
            for (nr, nc) in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) not in visited:
                        # Check of de cel vrij is of (optioneel) een store point
                        if not self.is_cell_occupied(nr, nc) or (nr, nc) in self.store_points:
                            new_path = path + [(nr, nc)]
                            if (nr, nc) == goal:
                                return new_path
                            visited.add((nr, nc))
                            queue.append(((nr, nc), new_path))
        return None

