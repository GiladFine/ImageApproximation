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
        self.initial_population = self.generate_initial_population(INITIAL_TRULY_RANDOM_STATES, INITIAL_RANDOM_LOCATION_STATES, INITIAL_FIXED_STATES)
        self.evaluate_generation(self.initial_population)
        self.initial_population.sort(key = lambda x: x.evaluation)
        self.best_state = self.initial_population[0]
        self.initial_image = self.best_state.get_image(self.im_width, self.im_length)
        self.current_generation = self.initial_population


    def generate_initial_population(self, rand_states_num, rand_avg_states_num, fixed_states_num):
        '''
        This function generates the initial population using the state_generator
        '''
        # Generate truly random states
        rand_states_list = []
        for i in range(rand_states_num):
            rand_states_list.append(random_state(self.im_width, self.im_length))

        # Generate fixed initial state copies, but mutate them a little bit to mix the initial gene pool
        fixed_states_list = []
        initial_state = generate_initial_state(self.im_width, self.im_length, self.pixels_array)
        for i in range(rand_avg_states_num):
            fixed_states_list.append(deepcopy(initial_state))

        for state in fixed_states_list:
            if i == 0: # keep first state as is
                continue
            random.shuffle(state.shapes_list)
            for ellipse in state.shapes_list:
                ellipse.mutate(1, self.im_width, self.im_length) # with 1 probability

        fixed_states_list.append(initial_state)

        # Generate mean-color states in random locations parallely
        input_list = [(self.im_width, self.im_length, self.pixels_array)] * rand_avg_states_num
        rand_avg_states_list = self.run_multiprocess(generate_initial_random_state, input_list)

        # return all states as intial population
        return rand_states_list + fixed_states_list + rand_avg_states_list 


    def crossover_and_mutate(self, father, mother):
        new_shapes_list = []

        # Crossover
        for i in range(len(father.shapes_list)):
            # Copy shape (gene) from father/mother at random
            shape = deepcopy(father.shapes_list[i] if random.uniform(0, 1) < 0.5 else mother.shapes_list[i])
            
            # Mutate
            shape.mutate(MUTATION_PROBABILITY, self.im_width, self.im_length)
            
            new_shapes_list.append(shape)
            random.shuffle(new_shapes_list) 

        return State(new_shapes_list)


    def evaluate_state(self, state):
        '''
        Wrapper for the state.evaluate function, for the multiprocessing
        '''
        return state.evaluate(self.pixels_array_resized, self.im_width, self.im_length)


    def evaluate_generation(self, generation):
        '''
        Evaluate entire generation in parallel, reducing computation time
        '''
        input_list = [[item] for item in generation]
        output_list = self.run_multiprocess(self.evaluate_state, input_list)
        for i in range(len(output_list)):
            generation[i].evaluation, generation[i].fitness = output_list[i]

    
    def run(self):
        '''
        Main function, running the algorithm
        '''
        while (datetime.now() - self.start_time).total_seconds() <= MAX_SECONDS:
            print("Gen {0}, time - {1}s, Best E = {2}, Fitness = {3}".format(self.gen_count, (datetime.now() - self.start_time).total_seconds(), self.best_state.evaluation, self.best_state.fitness))
            new_generation = []
            for i in range(CROSSOVER_POPULATION): # Best states of current generation
                for j in range(int(np.ceil(GENERATION_POPULATION / CROSSOVER_POPULATION))): # Random state
                    rand_index = i
                    while rand_index == i: # don't allow one parent reproduction
                        rand_index = random.randint(0, GENERATION_POPULATION - 1)

                    # Create new state and append to new generation
                    new_generation.append(self.crossover_and_mutate(self.current_generation[i], self.current_generation[rand_index]))

            self.evaluate_generation(new_generation)

            # Add top states from current generation to next (fittest survive!)
            new_generation.extend(self.current_generation[:5])
            new_generation.sort(key = lambda x: x.evaluation)

            # Drop worst states back to the desired population size
            new_generation = new_generation[:(GENERATION_POPULATION - len(new_generation))] 
            self.best_state = new_generation[0]
            self.current_generation = new_generation
            self.gen_count += 1
        

    def get_best_image(self):
        return self.best_state.get_image(self.im_width, self.im_length)


    def full_evaluation(self):
        '''
        Evaluates with respect to the full input image
        '''
        self.best_state.evaluate(self.pixels_array, self.im_width, self.im_length)
        print("Best State full evaluation: E = {0}, Fitness = {1}".format(self.best_state.evaluation, self.best_state.fitness))