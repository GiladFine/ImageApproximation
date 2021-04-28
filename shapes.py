import random
from utils import *
class Shape(object):
    def __init__(self, color):
        self.color = color

    def mutate_gene(self, val, prob, step, min_val = None, max_val = None):
        if random.uniform(0, 1) > prob:
            return val
        new_val = val + random.choice([-1, 1]) * step
        if min_val and new_val < min_val: return min_val
        if max_val and new_val > max_val: return max_val
        return new_val

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


    def mutate(self, prob, im_width, im_length):
        self.radius_x = self.mutate_gene(self.radius_x, prob, MUTATION_AMOUNT * 50, min_val=0)
        self.radius_y = self.mutate_gene(self.radius_y, prob, MUTATION_AMOUNT * 50, min_val=0)
        self.center_x = self.mutate_gene(self.center_x, prob, MUTATION_AMOUNT * im_width, min_val=0, max_val=im_width - 1)
        self.center_y = self.mutate_gene(self.center_y, prob, MUTATION_AMOUNT * im_length, min_val=0, max_val=im_length - 1)

        n_R = self.mutate_gene(self.color[0], prob, round(MUTATION_AMOUNT * MAX_COLOR), min_val=0, max_val=MAX_COLOR)
        n_G = self.mutate_gene(self.color[1], prob, round(MUTATION_AMOUNT * MAX_COLOR), min_val=0, max_val=MAX_COLOR)
        n_B = self.mutate_gene(self.color[2], prob, round(MUTATION_AMOUNT * MAX_COLOR), min_val=0, max_val=MAX_COLOR)
        n_A = self.mutate_gene(self.color[3], prob, round(MUTATION_AMOUNT * MAX_COLOR), min_val=0, max_val=MAX_COLOR)

        self.color = (n_R, n_G, n_B, n_A) 