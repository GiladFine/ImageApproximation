from PIL import Image
from aggdraw import Draw
import numpy as np
from utils import *
from shapes import Ellipse

class State(object):
    ''' 
    This class represents a state (i.e. a vector of inputs) of the Image Approximation problem

    shapes_list - [Shape(...), ...] * NUMBER_OF_SHAPES
    evaluation   - Float representing the avarage pixel distance (see pixels_array_distance)
    fitness      - 1 - evaluation / MAX_EVALUATION
    '''
    def __init__(self, shapes_list):
        self.shapes_list = shapes_list
        self.evaluation = -1
        self.fitness = -1


    def get_image(self, im_width, im_length):
        im = Image.new("RGBA", (im_width, im_length), (0, 0, 0, MAX_COLOR)) # Black image
        draw = Draw(im)
        for shape in self.shapes_list:
            shape.draw(draw)
        draw.flush()
        return im


    def get_pixels_array(self, im_width, im_length):
        return np.asarray(self.get_image(im_width, im_length))


    def pixels_array_distance(self, arr1, arr2):
        '''
        The main evaluation method, used to determain how much the two pixels_arrays are similar
        '''
        dist_sum = 0.0
        for i in range(arr1.shape[0]):
            for j in range(arr1.shape[1]):
                # normalize alpha channel
                alpha1, alpha2 = arr1[i][j][3] / float(MAX_COLOR), arr2[i][j][3] / float(MAX_COLOR)

                # Calculate premultiplied alpha RGB values
                r1, r2 = round(arr1[i][j][0] * alpha1), round(arr2[i][j][0] * alpha2)
                g1, g2 = round(arr1[i][j][1] * alpha1), round(arr2[i][j][1] * alpha2)
                b1, b2 = round(arr1[i][j][2] * alpha1), round(arr2[i][j][2] * alpha2)

                # euqlidian distance
                dist_sum += np.sqrt(pow((r1 - r2), 2) + pow((g1 - g2), 2) + pow((b1 - b2), 2))

        return dist_sum / (arr1.shape[0] * arr1.shape[1]) # Avg per pixel


    def evaluate(self, base_pix_arr, im_width, im_length):
        # Get the pixels array, resized to fit the input pixels array
        pix_arr = np.asarray(self.get_image(im_width, im_length).resize((base_pix_arr.shape[1], base_pix_arr.shape[0])))
        # Evaluate by pixel distance
        self.evaluation = self.pixels_array_distance(pix_arr, base_pix_arr)
        self.fitness = 1 - (self.evaluation / MAX_PIXEL_DISTANCE)
        return self.evaluation, self.fitness