from image_loader import ImageLoader
from algorithm import Genetics

def main():
    im_reader = ImageLoader('input/kyle.jpg')
    genetics = Genetics(im_reader.image_width, im_reader.image_length, im_reader.base_pixels_array_alpha, im_reader.resized_pixels_array_alpha)
    genetics.get_best_image().show()
    genetics.run()
    genetics.get_best_image().show()
    genetics.full_evaluation()


if __name__ == "__main__":
    main()