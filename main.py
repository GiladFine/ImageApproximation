from image_loader import ImageLoader
from algorithm import Genetics
from os import listdir
from os.path import isfile, join

def main():
    files = [f for f in listdir('input') if isfile(join('input', f))]
    results = []
    for item in files:
        print(item)
        in_path = 'input/' + item
        out_initial = 'results2/init-' + item.split('.')[0] + '.png'
        out_end = 'results2/end-' + item.split('.')[0] + '.png'
        im_reader = ImageLoader(in_path)
        genetics = Genetics(im_reader.image_width, im_reader.image_length, im_reader.base_pixels_array_alpha, im_reader.resized_pixels_array_alpha)
        genetics.get_best_image().save(out_initial)
        genetics.run()
        genetics.get_best_image().save(out_end)
        genetics.full_evaluation()
        results.append("{0} - {1}".format(item, genetics.best_state.fitness))

    print(results)


if __name__ == "__main__":
    main()