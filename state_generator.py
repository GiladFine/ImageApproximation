import numpy as np
import random
from utils import *
from state import State
from shapes import Ellipse


'''
This file helps calculate and generate effective states analytically
'''
MAX_INITIAL_RADIUS = 70

def calc_pixels_var_and_mean(pixel_list):
    if not pixel_list:
        return 0, (0, 0, 0, 0)

    # Mean
    m_R = round(np.average([item[0] for item in pixel_list]))
    m_G = round(np.average([item[1] for item in pixel_list]))
    m_B = round(np.average([item[2] for item in pixel_list]))
    m_alpha = round(np.average([item[3] for item in pixel_list]))

    # Variance
    v_R = np.var([item[0] for item in pixel_list]) 
    v_G = np.var([item[1] for item in pixel_list])
    v_B = np.var([item[2] for item in pixel_list])
    v_alpha = np.var([item[3] for item in pixel_list])

    return v_R + v_G + v_B + v_alpha, (m_R, m_G, m_B, m_alpha)



def ellipse_mean_color(center_x ,center_y, im_width, im_length, base_pix_arr):
    '''
    Generate a circle around the input point, by gradually increasing radiuses until size or variance exceed values
    '''
    circle_pixels_list = []
    variance = 0
    mean_color = (0, 0, 0, 0)
    ellipse = Ellipse(center_x, center_y, MIN_ELLIPSE_RADIUS, MIN_ELLIPSE_RADIUS, mean_color)
    prev_ellipse = Ellipse(center_x, center_y, 0, 0, mean_color)
    while(True):
        if ellipse.radius_x > 25 or ellipse.radius_y > 25 or variance > INITIAL_SHAPE_MAX_VAR:
            return prev_ellipse

        for i in range(max(ellipse.center_x - ellipse.radius_x, 0), min(ellipse.center_x + ellipse.radius_x, im_width)):
            for j in range(max(ellipse.center_y - ellipse.radius_y, 0), min(ellipse.center_y + ellipse.radius_y, im_length)):
                if prev_ellipse.is_in_ellipse(i, j): # no need to re-add previously move points
                    continue
                if ellipse.is_in_ellipse(i, j):
                    circle_pixels_list.append(base_pix_arr[j][i])

        variance, mean_color = calc_pixels_var_and_mean(circle_pixels_list)

        ellipse.color = mean_color
        prev_ellipse = ellipse
        
        ellipse.radius_x += 2
        ellipse.radius_y += 2


def ellipse_mean_color_radius(center_x ,center_y, radius_x, radius_y, im_width, im_length, base_pix_arr):
    '''
    Generate an ellipse from input params by calculating the avarage color on original image pixels
    '''
    circle_pixels_list = []
    mean_color = (0, 0, 0, 0)
    ellipse = Ellipse(center_x, center_y, radius_x, radius_y, mean_color)

    for i in range(max(ellipse.center_x - ellipse.radius_x, 0), min(ellipse.center_x + ellipse.radius_x, im_width)):
        for j in range(max(ellipse.center_y - ellipse.radius_y, 0), min(ellipse.center_y + ellipse.radius_y, im_length)):
            if ellipse.is_in_ellipse(i, j):
                circle_pixels_list.append(base_pix_arr[j][i])

    _, ellipse.color = calc_pixels_var_and_mean(circle_pixels_list)

    return ellipse


def random_state(im_width, im_length):
    '''
    Generate a totally random state
    '''
    ellipse_list = []
    for i in range(NUMBER_OF_SHAPES):
        ellipse = Ellipse(random.randint(0, im_width),
                            random.randint(0, im_length),
                            random.randint(MIN_ELLIPSE_RADIUS, MAX_INITIAL_RADIUS),
                            random.randint(MIN_ELLIPSE_RADIUS, MAX_INITIAL_RADIUS),
                            (
                            random.randint(0, MAX_COLOR),
                            random.randint(0, MAX_COLOR),
                            random.randint(0, MAX_COLOR),
                            random.randint(0, MAX_COLOR),
                            ))
        ellipse_list.append(ellipse)

    return State(ellipse_list)


def generate_initial_state(im_width, im_length, base_pix_arr):
    '''
    Generate a state with shapes that pave the entire image fairly evenly, with the avarage color of the pixels in the original image
    '''
    ellipse_list = []
    w_range = int(np.floor(np.sqrt(NUMBER_OF_SHAPES * im_width / im_length)))
    h_range = int(np.floor(NUMBER_OF_SHAPES / w_range))
    w_step = int(np.floor(im_width / (w_range + 1)))
    h_step = int(np.floor(im_length / (h_range + 1)))
    for i in range(w_range):
        for j in range(h_range):
            # This function will determain the radiuses by itself
            ellipse = ellipse_mean_color(w_step * (i + 1), h_step * (j + 1), im_width, im_length, base_pix_arr)
            ellipse_list.append(ellipse)

    # Finish all shaped with empty shapes
    for i in range(NUMBER_OF_SHAPES - len(ellipse_list)):
        ellipse = Ellipse(0, 0, 0, 0, (0, 0, 0, 0))
        ellipse_list.append(ellipse)

    return State(ellipse_list)


def generate_initial_random_state(im_width, im_length, base_pix_arr):
    '''
    Generate a state with random shapes in random locations, where again, color is determined by the original image pixels avarage
    '''
    ellipse_list = []
    for i in range(NUMBER_OF_SHAPES):
        ellipse = ellipse_mean_color_radius(random.randint(0, im_width - 1), random.randint(0, im_length - 1), random.randint(MIN_ELLIPSE_RADIUS, 100), random.randint(MIN_ELLIPSE_RADIUS, 100), im_width, im_length, base_pix_arr)
        ellipse_list.append(ellipse)

    return State(ellipse_list)