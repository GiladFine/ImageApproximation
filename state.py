from PIL import Image
from aggdraw import Draw, Pen, Brush
import numpy as np
from utils import *
from shapes import Ellipse
from image_reader import ImageLoader

class State(object):
    ''' 
    This class represents a state (i.e. a vector of inputs) of the Image Approximation problem

    ellipse_list - [Ellipse(...), ...] * NUMBER_OF_SHAPES
    evaluation   - Float representing the avarage pixel distance (see pixels_array_distance)
    fitness      - 1 - evaluation / MAX_EVALUATION
    '''
    def __init__(self, ellipse_list):
        self.ellipse_list = ellipse_list
        self.evaluation = -1
        self.fitness = -1

    def get_image(self, im_width, im_length):
        im = Image.new("RGBA", (im_width, im_length), (0, 0, 0, MAX_COLOR))
        draw = Draw(im)
        for ellipse in self.ellipse_list:
            brush = Brush(ellipse.color)
            draw.ellipse((ellipse.center_x - ellipse.radius_x,
                          ellipse.center_y - ellipse.radius_y,
                          ellipse.center_x + ellipse.radius_x,
                          ellipse.center_y + ellipse.radius_y), brush)
        draw.flush()
        return im


    def get_pixels_array(self, im_width, im_length):
        return np.asarray(self.get_image(im_width, im_length))


    def pixels_array_distance(self, arr1, arr2):
        dist_sum = 0.0
        for i in range(arr1.shape[0]):
            for j in range(arr1.shape[1]):
                alpha1, alpha2 = arr1[i][j][3] / float(MAX_COLOR), arr2[i][j][3] / float(MAX_COLOR)
                r1, r2 = round(arr1[i][j][0] * alpha1), round(arr2[i][j][0] * alpha2)
                g1, g2 = round(arr1[i][j][1] * alpha1), round(arr2[i][j][1] * alpha2)
                b1, b2 = round(arr1[i][j][2] * alpha1), round(arr2[i][j][2] * alpha2)

                dist_sum += np.sqrt(pow(max(abs(r1 - r2), abs(r1 - r2 - alpha1 - alpha2)), 2) + 
                                    pow(max(abs(g1 - g2), abs(g1 - g2 - alpha1 - alpha2)), 2) +
                                    pow(max(abs(b1 - b2), abs(b1 - b2 - alpha1 - alpha2)), 2))

        return dist_sum / (arr1.shape[0] * arr1.shape[1])


    def evaluate(self, base_pix_arr, im_width, im_length):
        # start_time = datetime.now()
        # print("start evaluate - {0}".format(datetime.now() - start_time))
        pix_arr = np.asarray(self.get_image(im_width, im_length).resize((base_pix_arr.shape[1], base_pix_arr.shape[0])))
        # print("after array - {0}".format(datetime.now() - start_time))
        self.evaluation = self.pixels_array_distance(pix_arr, base_pix_arr)
        self.fitness = 1 - (self.evaluation / MAX_PIXELS_DISTANCE)
        # print("end evaluate - {0}".format(datetime.now() - start_time))