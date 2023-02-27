import random
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 1920  # Canvas width
CANVAS_HEIGHT = 1080  # Canvas height
CANVAS_CENTER_X = CANVAS_WIDTH / 2.5  # X-axis in center of canvas
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2.5  # Y-axis in center of canvas
IMAGE_ENLARGE = 11  # Enlarge / Zoom in 
HEART_COLOR = "#ff3366"  # Heart color(16 bit code)

# Hello, world!

def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """
    “Heart Function Generator”
    :param shrink_ratio: Enlarge / Zoom In
    :param t: Parameter
    :return: coordinate
    """
    # Basics Parameter
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # Enlarge
    x *= shrink_ratio
    y *= shrink_ratio

    # Move to Center of Canvas
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """
    Random Internal Diffusion
    :param x: Original X
    :param y: Original Y
    :param beta: Intensity
    :return: Latest coordinates
    """
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy


def shrink(x, y, ratio):
    """
    Vibrate
    :param x: Original X
    :param y: Original Y
    :param ratio: Propotion
    :return: New coordinate
    """
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """
    Customise curve function, Adjust heart beat period
    :param p: Parameter
    :return: Sine
    """
    # Try to replace another dynamic functions to archieve more effect（Bessel function?)
    return 4 * (4 * sin(6 * p)) / (4 * pi)


class Heart:

    def __init__(self, generate_frame=20):
        self._points = set()  # Original heart coordinates set
        self._edge_diffusion_points = set()  # Edge spread effect coordinates set
        self._center_diffusion_points = set()  # Center diffusion effect coordinate set
        self.all_points = {}  # Dynamic starting point coordinates
        self.build(2000)

        self.random_halo = 1000

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # Heart
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  # Create a gap in heart caused by places that are not random covered
            x, y = heart_function(t)
            self._points.add((x, y))

        # Heart inter-expand
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # Heart inter-expand again
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        # Adjust zoom in and out ratio
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)  # Magic Intensity

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)  # Scaling of rounded period

        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # Halo
        heart_halo_point = set()  # Halo coordinates set
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # Create a gap in heart caused by places that are not random covered
            x, y = heart_function(t, shrink_ratio=11.6)  # Magic parameter
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # New point
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))

        # Contour
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # Content
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()  # One Tk
    root.title("Heart Beat")  # Window Name
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()  # Heart 
    draw(root, canvas, heart)  # Start to Draw in Canvas 
    root.mainloop()
