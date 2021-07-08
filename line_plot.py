def assign_points(coords):
    x1 = min(coords[0][0], coords[1][0])
    x2 = max(coords[0][0], coords[1][0])
    y1 = min(coords[0][1], coords[1][1])
    y2 = max(coords[0][1], coords[1][1])
    return x1, x2, y1, y2

class intensity_plot():
    def __init__(self, rect_coords, canvas):
        self.x1, self.x2, self.y1, self.y2 = assign_points(rect_coords)

        self.canvas = canvas
        self.canvas.pack(side="top", fill="both", expand=True)

        self.line = self.canvas.create_line(0, 0, 1, 1, fill="orange", width=3)
        self.coords = self.canvas.coords(self.line)

    def update_vals(self, pixels):
        avg_val = n = 0
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                avg_val += sum(pixels[x][y])
                n += 1
        avg_val = avg_val / n
        #now = datetime.datetime.now()

        self.add_point(avg_val/100)

    def add_point(self, p):
        x = self.coords[-2] + 1
        self.coords.append(x)
        self.coords.append(p)
        #coords = coords[-200:]

    def display(self):
        self.canvas.coords(self.line, *self.coords)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.pack(side="top", fill="both", expand="True")

    def update_canvas(self, canvas):
        self.canvas = canvas
        self.canvas.create_line(*self.coords, fill="green", width=3)
