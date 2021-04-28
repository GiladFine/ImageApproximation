import numpy as np
import random
from datetime import datetime
from copy import deepcopy
from multiprocessing import freeze_support, Pool
from shapes import Ellipse
from utils import *
from image_loader import ImageLoader
from shapes import Ellipse
from state import State
from state_gen import *

class Algorithm(object):
    def __init__(self, image_width, image_length, pixels_array, pixels_array_resized):
        freeze_support()
        self.start_time = datetime.now()
        self.im_width = image_width
        self.im_length = image_length
        self.pixels_array = pixels_array
        self.pixels_array_resized = pixels_array_resized

    def run_multiprocess(self, func, arg_list):
        with Pool() as pool:
            output_list = pool.starmap(func, arg_list)
        return output_list


class Genetics(Algorithm):
    def __init__(self, image_width, image_length, pixels_array, pixels_array_resized):
        super().__init__(image_width, image_length, pixels_array, pixels_array_resized)
        self.gen_count = 0
        self.initial_population = self.generate_initial_population(10, 30, 10)
        self.evaluate_generation(self.initial_population)
        self.initial_population.sort(key = lambda x: x.evaluation)
        self.best_state = self.initial_population[0]
        self.initial_image = self.best_state.get_image(self.im_width, self.im_length)
        self.current_generation = self.initial_population


    def generate_initial_population(self, rand_states_num, rand_avg_states_num, fixed_states_num):
        rand_states_list = []

        for i in range(rand_states_num):
            rand_states_list.append(random_state(self.im_width, self.im_length))

        ############################################################

        fixed_states_list = []
        initial_state = generate_initial_state(self.im_width, self.im_length, self.pixels_array)
        for i in range(rand_avg_states_num):
            fixed_states_list.append(deepcopy(initial_state))

        for state in fixed_states_list:
            if i == 0:
                continue
            random.shuffle(state.shapes_list)
            for ellipse in state.shapes_list:
                ellipse.mutate(1, self.im_width, self.im_length)

        fixed_states_list.append(initial_state)

        ####################################################################################

        input_list = [(self.im_width, self.im_length, self.pixels_array)] * rand_avg_states_num
        
        rand_avg_states_list = self.run_multiprocess(generate_initial_random_state, input_list)

        return rand_states_list + fixed_states_list + rand_avg_states_list


    def crossover_and_mutate(self, father, mother):
        new_shapes_list = []

        # Crossover
        for i in range(len(father.shapes_list)):
            ellipse = deepcopy(father.shapes_list[i] if random.uniform(0, 1) < 0.5 else mother.shapes_list[i])
            
            # Mutate
            ellipse.mutate(MUTATION_PROBABILITY, self.im_width, self.im_length)
            
            new_shapes_list.append(ellipse)
            random.shuffle(new_shapes_list)

        return State(new_shapes_list)


    def evaluate_state(self, state):
        return state.evaluate(self.pixels_array_resized, self.im_width, self.im_length)


    def evaluate_generation(self, generation):
        input_list = [[item] for item in generation]
        output_list = self.run_multiprocess(self.evaluate_state, input_list)
        for i in range(len(output_list)):
            generation[i].evaluation, generation[i].fitness = output_list[i]

    
    def run(self):
        while (datetime.now() - self.start_time).total_seconds() <= MAX_SECONDS:
            print("Gen {0}, time - {1}s, Best E = {2}, Fitness = {3}".format(self.gen_count, (datetime.now() - self.start_time).total_seconds(), self.best_state.evaluation, self.best_state.fitness))
            new_generation = []
            for i in range(CROSSOVER_POPULATION):
                for j in range(int(np.ceil(GENERATION_POPULATION / CROSSOVER_POPULATION))):
                    rand_index = i
                    while rand_index == i:
                        rand_index = random.randint(0, GENERATION_POPULATION - 1)
                    new_generation.append(self.crossover_and_mutate(self.current_generation[i], self.current_generation[rand_index]))

            self.evaluate_generation(new_generation)
            new_generation.extend(self.current_generation[:5])
            new_generation.sort(key = lambda x: x.evaluation)
            new_generation = new_generation[:(GENERATION_POPULATION - len(new_generation))] 
            self.best_state = new_generation[0]
            self.current_generation = new_generation
            self.gen_count += 1
        

    def get_best_image(self):
        return self.best_state.get_image(self.im_width, self.im_length)


    def full_evaluation(self):
        self.best_state.evaluate(self.pixels_array, self.im_width, self.im_length)
        print("Best State full evaluation: E = {0}, Fitness = {1}".format(self.best_state.evaluation, self.best_state.fitness))