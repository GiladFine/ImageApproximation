from PIL import Image
from aggdraw import Draw, Pen, Brush
import numpy as np
from utils import *

class ImageLoader(object):
    '''
    This class helps loading, parsing & resizing the input image
    base_image                    - original image
    resize_image                  - a resizing of the original image (used for saving time on evaluations)
    image_width, image_length     - original image size in pixels
    resized_width, resized_length - resized image size in pixels
    base_pixels_array             - original image as pixels array
    base_pixels_array_alpha       - original image as pixels array with alpha channel
    resized_pixels_array          - resized image as pixels array
    resized_pixels_array_alpha    - resized image as pixels array with alpha channel
    '''
    def __init__(self, path):
        self.base_image = Image.open(path, 'r')
        if self.base_image.mode not in ['RGBA', 'RGB']:
            Exception("Unknown image mode - " + self.base_image.mode)
        
        self.image_width, self.image_length = self.calc_resize(self.base_image.size[0], self.base_image.size[1], BASE_IMAGE_MAX_PIXELS)
        self.base_image = self.base_image.resize((self.image_width, self.image_length))

        self.resized_width, self.resized_length = self.calc_resize(self.image_width, self.image_length, EVALUATION_MAX_PIXELS)
        self.resized_image = self.base_image.resize((self.resized_width, self.resized_length))
       
        self.base_pixels_array = np.asarray(self.base_image)
        self.base_pixels_array_alpha = self.add_alpha_to_pixels(self.base_pixels_array)

        self.resized_pixels_array = np.asarray(self.resized_image)
        self.resized_pixels_array_alpha = self.add_alpha_to_pixels(self.resized_pixels_array)


    def calc_resize(self, im_width, im_length, pixel_amount):
        if im_width * im_length <= pixel_amount: # Image is small enough
            return (im_width, im_length)

        # In order for the image ratio to be preserved, we calc the factor to resize the image by
        factor = np.sqrt(im_width * im_length / pixel_amount)
        return (round(im_width / factor), round(im_length / factor))


    def add_alpha_to_pixels(self, pix_arr):
        '''
        This function is used to convert the RGB pixels to RGBA with Maximal transparency over black background
        '''
        w_size, l_size, pix_size = pix_arr.shape
        pix_size = 4
        ret_arr = np.zeros((w_size, l_size, pix_size), dtype='uint8')
        for i in range(pix_arr.shape[0]):
            for j in range(pix_arr.shape[1]):
                color = pix_arr[i][j]
                if len(color) == 4 and color[-1] != MAX_COLOR: # If RGBA pixel, we can still add trancparency when alpha is maxed
                    continue
                alpha = max(color)
                if alpha == 0:
                    ret_arr[i][j] = (MAX_COLOR, MAX_COLOR, MAX_COLOR, MAX_COLOR)
                else:
                    ret_arr[i][j] = (round(color[0] * MAX_COLOR / alpha), round(color[1] * MAX_COLOR / alpha), round(color[2] * MAX_COLOR / alpha), alpha)

        return ret_arr
