class Shape(object):
    def __init__(self, color):
        self.color = color
        

class Ellipse(Shape):
    def __init__(self, x, y, r_x, r_y, color):
        super().__init__(color)
        self.center_x, self.center_y = x, y
        self.radius_x, self.radius_y = r_x, r_y

    def is_in_ellipse(self, x, y):
        dx = abs(x - self.center_x)
        dy = abs(y - self.center_y)

        if dx > self.radius_x:
            return False
        if dy > self.radius_y:
            return False
        if pow(dx, 2) + pow(dy, 2) <= pow(self.radius_x * self.radius_y, 2): 
            return True

        return False

