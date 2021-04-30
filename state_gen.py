import numpy as np
import random
from utils import *
from state import State
from shapes import Ellipse
from utils import *

'''
This file helps calculate and generate effective states analytically
'''

def calc_pixels_mean(pixels_list):
    if not pixels_list:
        return (0, 0, 0, MAX_COLOR)

    m_R = round(np.average([item[0] for item in pixels_list]))
    m_G = round(np.average([item[1] for item in pixels_list]))
    m_B = round(np.average([item[2] for item in pixels_list]))
    m_alpha = round(np.average([item[3] for item in pixels_list]))

    return (m_R, m_G, m_B, m_alpha)


def calc_pixels_variance(pixels_list):
    if not pixels_list:
        return 0

    v_R = np.var([item[0] for item in pixels_list]) 
    v_G = np.var([item[1] for item in pixels_list])
    v_B = np.var([item[2] for item in pixels_list])
    v_alpha = np.var([item[3] for item in pixels_list])

    return v_R + v_G + v_B + v_alpha


def ellipse_mean_color(center_x ,center_y, max_x_radius, max_y_radius, im_width, im_length, base_pix_arr):
    '''
    Generate a circle around the input point, by gradually increasing radiuses until size or variance exceed values
    '''
    shape_pixels_list = []
    variance = 0
    mean_color = (0, 0, 0, MAX_COLOR)
    ellipse = Ellipse(center_x, center_y, MIN_ELLIPSE_RADIUS, MIN_ELLIPSE_RADIUS, mean_color)
    prev_ellipse = Ellipse(center_x, center_y, 0, 0, mean_color)
    while(True):
        if ellipse.radius_x > max_x_radius or ellipse.radius_x > max_y_radius or variance > INITIAL_SHAPE_MAX_VAR:
            prev_ellipse.color = calc_pixels_mean(shape_pixels_list)
            return prev_ellipse

        for i in range(max(ellipse.center_x - ellipse.radius_x, 0), min(ellipse.center_x + ellipse.radius_x, im_width)):
            for j in range(max(ellipse.center_y - ellipse.radius_y, 0), min(ellipse.center_y + ellipse.radius_y, im_length)):
                if prev_ellipse.is_in_ellipse(i, j): # no need to re-add previously move points
                    continue
                if ellipse.is_in_ellipse(i, j):
                    shape_pixels_list.append(base_pix_arr[j][i])

        variance = calc_pixels_variance(shape_pixels_list)
        prev_ellipse = ellipse
        ellipse.radius_x += 2
        ellipse.radius_y += 2


def ellipse_mean_color_radius(center_x ,center_y, radius_x, radius_y, im_width, im_length, base_pix_arr):
    '''
    Generate an ellipse from input params by calculating the avarage color on original image pixels
    '''
    shape_pixels_list = []
    mean_color = (0, 0, 0, MAX_COLOR)
    ellipse = Ellipse(center_x, center_y, radius_x, radius_y, mean_color)

    for i in range(max(ellipse.center_x - ellipse.radius_x, 0), min(ellipse.center_x + ellipse.radius_x, im_width)):
        for j in range(max(ellipse.center_y - ellipse.radius_y, 0), min(ellipse.center_y + ellipse.radius_y, im_length)):
            if ellipse.is_in_ellipse(i, j):
                shape_pixels_list.append(base_pix_arr[j][i])

    ellipse.color = calc_pixels_mean(shape_pixels_list)

    return ellipse


def random_state(im_width, im_length):
    '''
    Generate a totally random state
    '''
    shapes_list = []
    for i in range(NUMBER_OF_SHAPES):
        ellipse = Ellipse(random.randint(0, im_width),
                            random.randint(0, im_length),
                            random.randint(MIN_ELLIPSE_RADIUS, round(im_width / 2)),
                            random.randint(MIN_ELLIPSE_RADIUS, round(im_length / 2)),
                            (
                            random.randint(0, MAX_COLOR),
                            random.randint(0, MAX_COLOR),
                            random.randint(0, MAX_COLOR),
                            random.randint(0, MAX_COLOR),
                            ))
        shapes_list.append(ellipse)

    return State(shapes_list)


def generate_initial_state(im_width, im_length, base_pix_arr):
    '''
    Generate a state with shapes that pave the entire image fairly evenly, with the avarage color of the pixels in the original image
    '''
    shapes_list = []
    w_range = int(np.floor(np.sqrt(NUMBER_OF_SHAPES * im_width / im_length)))
    h_range = int(np.floor(NUMBER_OF_SHAPES / w_range))
    w_step = int(np.floor(im_width / (w_range + 1)))
    h_step = int(np.floor(im_length / (h_range + 1)))
    for i in range(w_range):
        for j in range(h_range):
            # This function will determain the radiuses by itself
            ellipse = ellipse_mean_color(w_step * (i + 1), h_step * (j + 1), w_step, h_step, im_width, im_length, base_pix_arr)
            shapes_list.append(ellipse)

    # Finish all shaped with empty shapes
    for i in range(NUMBER_OF_SHAPES - len(shapes_list)):
        ellipse = Ellipse(0, 0, 0, MAX_COLOR, (0, 0, 0, MAX_COLOR))
        shapes_list.append(ellipse)

    return State(shapes_list)


def generate_initial_random_state(im_width, im_length, base_pix_arr):
    '''
    Generate a state with random shapes in random locations, where again, color is determined by the original image pixels avarage
    '''
    shapes_list = []
    for i in range(NUMBER_OF_SHAPES):
        ellipse = ellipse_mean_color_radius(random.randint(0, im_width - 1), random.randint(0, im_length - 1), random.randint(MIN_ELLIPSE_RADIUS, min(100, round(im_width / 2))), random.randint(MIN_ELLIPSE_RADIUS, min(100, round(im_length / 2))), im_width, im_length, base_pix_arr)
        shapes_list.append(ellipse)

    return State(shapes_list)