import numpy as np
from PIL import Image
from copy import deepcopy
import random
from datetime import datetime
from multiprocessing import Pool, freeze_support
from utils import *
from image_reader import ImageLoader
from genetics import Genetics
from shapes import Ellipse
from state import State
from state_generator import *


def generate_initial_population(im_width, im_length, base_pix_arr):
    print("before MP - {0}".format(datetime.now() - start_time))

    population = []

    # ellipse_pool = run_multiprocess(ellipse_mean_color_radius, input_list)

    # population = [State(random.sample(ellipse_pool, NUMBER_OF_SHAPES)) for i in range(CROSSOVER_POPULATION - 1)] + [generate_initial_state(im_width, im_length, base_pix_arr)]

    initial_state = generate_initial_state(im_width, im_length, base_pix_arr)
    population = []
    for i in range(9):
        population.append(deepcopy(initial_state))
    for state in population:
        random.shuffle(state.ellipse_list)
        for ellipse in state.ellipse_list:
            n_rad_x = ellipse.radius_x + random.choice([-1, 1]) * MUTATION_AMOUNT * 50
            if n_rad_x > 0: ellipse.radius_x = n_rad_x
            n_rad_y = ellipse.radius_y + random.choice([-1, 1]) * MUTATION_AMOUNT * 50
            if n_rad_y > 0: ellipse.radius_y = n_rad_y
            n_x = ellipse.center_x + random.choice([-1, 1]) * MUTATION_AMOUNT * im_width
            if n_x >= 0 and n_x < im_width: ellipse.center_x = n_x
            n_y = ellipse.center_y + random.choice([-1, 1]) * MUTATION_AMOUNT * im_length
            if n_y >= 0 and n_y < im_width: ellipse.center_y = n_y

            n_R = ellipse.color[0] + random.choice([-1, 1]) * round(MUTATION_AMOUNT * MAX_COLOR)
            n_R = n_R if n_R >= 0 and n_R <= MAX_COLOR else ellipse.color[0] 
            n_G = ellipse.color[1] + random.choice([-1, 1]) * round(MUTATION_AMOUNT * MAX_COLOR)
            n_G = n_G if n_G >= 0 and n_G <= MAX_COLOR else ellipse.color[1] 
            n_B = ellipse.color[2] + random.choice([-1, 1]) * round(MUTATION_AMOUNT * MAX_COLOR)
            n_B = n_B if n_B >= 0 and n_B <= MAX_COLOR else ellipse.color[2] 
            n_a = ellipse.color[3] + random.choice([-1, 1]) * round(MUTATION_AMOUNT * MAX_COLOR)
            n_a = n_a if n_a >= 0 and n_a <= MAX_COLOR else ellipse.color[3]
            ellipse.color = (n_R, n_G, n_B, n_a) 

    population.append(initial_state)

    input_list = [(im_width, im_length, base_pix_arr)] * (GENERATION_POPULATION - len(population))
    
    population.extend(run_multiprocess(generate_initial_random_state, input_list))

    print("after MP - {0}".format(datetime.now() - start_time))

    return population


def crossover_and_mutate(father, mother, im_width, im_length):
    new_ellipse_list = []

    # Crossover
    for i in range(len(father.ellipse_list)):
        ellipse = deepcopy(father.ellipse_list[i] if random.uniform(0, 1) < 0.5 else mother.ellipse_list[i])
        
        # Mutate
        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            ellipse.radius_x = ellipse.radius_x + random.choice([-1, 1]) * MUTATION_AMOUNT * 50
            if ellipse.radius_x < 0: ellipse.radius_x = 0

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            ellipse.radius_y = ellipse.radius_y + random.choice([-1, 1]) * MUTATION_AMOUNT * 50
            if ellipse.radius_y < 0: ellipse.radius_y = 0

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            ellipse.center_x = ellipse.center_x + random.choice([-1, 1]) * MUTATION_AMOUNT * im_width
            if ellipse.center_x < 0: ellipse.center_x = 0
            if ellipse.center_x >= im_width: ellipse.center_x = im_width - 1

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            ellipse.center_y = ellipse.center_y + random.choice([-1, 1]) * MUTATION_AMOUNT * im_length
            if ellipse.center_y < 0: ellipse.center_y = 0
            if ellipse.center_y >= im_length: ellipse.center_y = im_length - 1

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            n_R = ellipse.color[0] + random.choice([-1, 1]) * round(round(MUTATION_AMOUNT * MAX_COLOR))
            if n_R < 0: n_R = 0
            if n_R > MAX_COLOR: n_R = MAX_COLOR
        else:
            n_R = ellipse.color[0]

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            n_G = ellipse.color[1] + random.choice([-1, 1]) * round(round(MUTATION_AMOUNT * MAX_COLOR))
            if n_G < 0: n_G = 0
            if n_G > MAX_COLOR: n_G = MAX_COLOR
        else:
            n_G = ellipse.color[1]

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            n_B = ellipse.color[2] + random.choice([-1, 1]) * round(round(MUTATION_AMOUNT * MAX_COLOR))
            if n_B < 0: n_B = 0
            if n_B > MAX_COLOR: n_B = MAX_COLOR
        else:
            n_B = ellipse.color[2]

        if random.uniform(0, 1) <= MUTATION_PROBABILITY:
            n_A = ellipse.color[3] + random.choice([-1, 1]) * round(round(MUTATION_AMOUNT * MAX_COLOR))
            if n_A < 0: n_A = 0
            if n_A > MAX_COLOR: n_A = MAX_COLOR
        else:
            n_A = ellipse.color[3]

        ellipse.color = (n_R, n_G, n_B, n_A)
        
        new_ellipse_list.append(ellipse)
        random.shuffle(new_ellipse_list)

    return State(new_ellipse_list)


def run_multiprocess(func, arg_list):
    with Pool() as pool:
        output_list = pool.starmap(func, arg_list)
    return output_list

start_time = datetime.now()

def main():
    im_reader = ImageLoader('input/portrait.jpg')
    IMAGE_WIDTH, IMAGE_LENGTH = im_reader.image_width, im_reader.image_length
    base_pix_arr = im_reader.base_pixels_array
    base_pix_arr_alpha = im_reader.base_pixels_array_alpha
    base_pix_arr_resized = im_reader.resized_pixels_array
    base_pix_arr_resized_alpha = im_reader.resized_pixels_array_alpha

    print("start initial population - {0}".format(datetime.now() - start_time))
    initial_population = generate_initial_population(IMAGE_WIDTH, IMAGE_LENGTH, base_pix_arr_alpha)
    print("end initial population - {0}".format(datetime.now() - start_time))
    for state in initial_population:
        state.evaluate(base_pix_arr_resized_alpha, IMAGE_WIDTH, IMAGE_LENGTH)
    print("end initial population evaluation - {0}".format(datetime.now() - start_time))
    initial_population.sort(key = lambda x: x.evaluation)
    print("end initial population sort - {0}".format(datetime.now() - start_time))
    print("Initial Population, Best E = {0}, Fitness = {1}".format(initial_population[0].evaluation, 1 - initial_population[0].evaluation / MAX_PIXELS_DISTANCE))

    best_state = initial_population[0]
    initial_state = best_state

    initial_image = best_state.get_image(IMAGE_WIDTH, IMAGE_LENGTH)
    initial_image.show()
    generation = initial_population
    prev_best = best_state.evaluation
    freeze_counter = 0
    for i in range(MAX_ITERATIONS):
        if (datetime.now() - start_time).total_seconds() >= MAX_SECONDS:
            break

        # if freeze_counter >= 15:
        #     break
        print("Gen {0}, Best E = {1}, Fitness = {2}".format(i, best_state.evaluation, 1 - best_state.evaluation / MAX_PIXELS_DISTANCE))
        print("start generation - {0}".format(datetime.now() - start_time))
        new_generation = []
        for i in range(CROSSOVER_POPULATION):
            for j in range(int(np.ceil(GENERATION_POPULATION / CROSSOVER_POPULATION))):
                rand_index = i
                while rand_index == i:
                    rand_index = random.randint(0, GENERATION_POPULATION - 1)
                new_generation.append(crossover_and_mutate(generation[i], generation[rand_index], IMAGE_WIDTH, IMAGE_LENGTH))
        
        print("end crossover and mutation - {0}".format(datetime.now() - start_time))
        for state in new_generation:
            state.evaluate(base_pix_arr_resized_alpha, IMAGE_WIDTH, IMAGE_LENGTH)
        print("end generation evaluations - {0}".format(datetime.now() - start_time))
        new_generation.extend(generation[:5])
        new_generation.sort(key = lambda x: x.evaluation)
        new_generation = new_generation[:(GENERATION_POPULATION - len(new_generation))] 
        print("end generation sort - {0}".format(datetime.now() - start_time))
        best_state = new_generation[0]
        freeze_counter = freeze_counter + 1 if prev_best == best_state.evaluation else 0
        prev_best = best_state.evaluation

        generation = new_generation
    
    print("start list to image - {0}".format(datetime.now() - start_time))
    end_image = best_state.get_image(IMAGE_WIDTH, IMAGE_LENGTH)
    print("end list to image - {0}".format(datetime.now() - start_time))
    end_image.show()
    print("start final evaluate - {0}".format(datetime.now() - start_time))
    best_state.evaluate(base_pix_arr_alpha, IMAGE_WIDTH, IMAGE_LENGTH)
    print("end final evaluate - {0}".format(datetime.now() - start_time))
    print("end resule - E = {0}, Fitness = {1}".format(best_state.evaluation, 1 - best_state.evaluation / MAX_PIXELS_DISTANCE))


if __name__ == "__main__":
    freeze_support()
    main()