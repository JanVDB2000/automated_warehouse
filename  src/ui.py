import tkinter as tk
import random
from warehouse import Warehouse
from robot import Robot

class WarehouseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Geautomatiseerd Magazijn")
        size = 50
        self.canvas = tk.Canvas(self, width=size * 10, height=size * 10, bg="white")
        self.canvas.pack()

        self.warehouse = Warehouse(self.canvas, rows=size, cols=size, cell_size=10)

        # 25 robots, elk startend op een willekeurig store point
        for i in range(25):
            (r, c) = random.choice(self.warehouse.store_points)
            robot = Robot(self.canvas, self.warehouse, i, r, c)
            self.warehouse.robots.append(robot)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        order_btn = tk.Button(button_frame, text="Nieuwe Order", command=self.warehouse.new_order)
        order_btn.pack(side=tk.LEFT, padx=5)

        replenish_btn = tk.Button(button_frame, text="Aanvullen (Leverpunt)", command=self.warehouse.robot_to_replenish)
        replenish_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self, text="Beweeg over het grid om de voorraad te zien.")
        self.status_label.pack(pady=5)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

        self.warehouse.update()

    def on_canvas_motion(self, event):
        row = event.y // self.warehouse.cell_size
        col = event.x // self.warehouse.cell_size
        if 0 <= row < self.warehouse.rows and 0 <= col < self.warehouse.cols:
            inv = self.warehouse.grid[row][col]
            self.status_label.config(text=f"Cel ({row}, {col}): Voorraad {inv}")
        else:
            self.status_label.config(text="Buiten het grid.")

if __name__ == "__main__":
    app = WarehouseApp()
    app.mainloop()
